"""RAG pipeline: PDF ingestion, semantic retrieval (Pinecone), and Gemini-backed
answer / quiz generation.

Heavy and network-dependent resources (the SentenceTransformers embedder, the
Pinecone client, and the Gemini REST calls) are initialized lazily so that the
FastAPI app can import and boot without any external credentials. They are only
required when a ``/rag/*`` endpoint is actually invoked, at which point a clear
error is raised if configuration is missing.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from typing import Any, Dict, List, Optional

import httpx

EMBED_MODEL = "intfloat/e5-large-v2"
EMBED_DIM = 1024


class RAGPipeline:
    def __init__(self, index_name: Optional[str] = None):
        self.index_name = index_name or os.getenv("PINECONE_INDEX", "nlp")
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self._embedder = None
        self._index = None

    # ---------- lazy resources ----------
    def _get_embedder(self):
        if self._embedder is None:
            from sentence_transformers import SentenceTransformer

            self._embedder = SentenceTransformer(EMBED_MODEL)
        return self._embedder

    def _get_index(self):
        if self._index is not None:
            return self._index
        if not self.pinecone_api_key:
            raise RuntimeError(
                "PINECONE_API_KEY is not set. Configure it to use RAG endpoints."
            )
        from pinecone import Pinecone, ServerlessSpec

        pc = Pinecone(api_key=self.pinecone_api_key)
        existing = {i["name"] for i in pc.list_indexes()}
        if self.index_name not in existing:
            pc.create_index(
                name=self.index_name,
                dimension=EMBED_DIM,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
            # wait until the index is ready to accept traffic
            for _ in range(30):
                try:
                    if pc.describe_index(self.index_name).status.get("ready"):
                        break
                except Exception:
                    pass
                time.sleep(2)
        self._index = pc.Index(self.index_name)
        return self._index

    # ---------- ingestion helpers ----------
    def _extract_text_from_pdf_url(self, pdf_url: str) -> str:
        from PyPDF2 import PdfReader
        import io

        with httpx.Client(timeout=60, follow_redirects=True) as client:
            resp = client.get(pdf_url)
            resp.raise_for_status()
            data = resp.content
        reader = PdfReader(io.BytesIO(data))
        parts: List[str] = []
        for page in reader.pages:
            try:
                parts.append(page.extract_text() or "")
            except Exception:
                continue
        return "\n".join(parts)

    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
        chunks: List[str] = []
        current: List[str] = []
        current_words = 0
        for sentence in sentences:
            words = len(sentence.split())
            current.append(sentence)
            current_words += words
            if current_words >= chunk_size:
                chunk = " ".join(current)
                if len(chunk.split()) >= 20:
                    chunks.append(chunk)
                # keep the tail sentences for context continuity
                overlap_words = 0
                tail: List[str] = []
                for s in reversed(current):
                    tail.insert(0, s)
                    overlap_words += len(s.split())
                    if overlap_words >= overlap:
                        break
                current = tail
                current_words = sum(len(s.split()) for s in current)
        if current:
            chunk = " ".join(current)
            if len(chunk.split()) >= 20:
                chunks.append(chunk)
        return chunks

    # ---------- public API ----------
    def ingest_pdf(self, pdf_url: str) -> Dict[str, Any]:
        text = self._extract_text_from_pdf_url(pdf_url)
        if not text.strip():
            raise RuntimeError("No extractable text found in the PDF.")
        chunks = self._chunk_text(text)
        if not chunks:
            raise RuntimeError("PDF produced no usable text chunks.")

        index = self._get_index()
        embedder = self._get_embedder()

        doc_id = hashlib.sha1(pdf_url.encode("utf-8")).hexdigest()[:12]
        passages = [f"passage: {c}" for c in chunks]
        vectors = embedder.encode(
            passages, normalize_embeddings=True, batch_size=32
        )

        items = []
        for i, (chunk, vec) in enumerate(zip(chunks, vectors)):
            items.append(
                {
                    "id": f"{doc_id}-chunk-{i}",
                    "values": [float(x) for x in vec],
                    "metadata": {
                        "text": chunk[:1000],
                        "doc_id": doc_id,
                        "chunk_idx": i,
                        "timestamp": int(time.time()),
                        "source": pdf_url,
                    },
                }
            )

        added = 0
        for start in range(0, len(items), 100):
            batch = items[start : start + 100]
            index.upsert(vectors=batch)
            added += len(batch)

        return {"added": added, "doc_id": doc_id, "chunks": len(chunks)}

    def query(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        index = self._get_index()
        embedder = self._get_embedder()

        q_vec = embedder.encode(
            [f"query: {question}"], normalize_embeddings=True
        )[0]
        results = index.query(
            vector=[float(x) for x in q_vec], top_k=top_k, include_metadata=True
        )
        matches = results.get("matches", []) if isinstance(results, dict) else results.matches
        contexts: List[str] = []
        for m in matches:
            meta = m.get("metadata", {}) if isinstance(m, dict) else (m.metadata or {})
            txt = (meta or {}).get("text", "")
            if txt:
                contexts.append(re.sub(r"\s+", " ", txt).strip()[:300])

        answer = self._generate_answer(question, contexts)
        return {"answer": answer, "contexts": contexts}

    def generate_quiz(self, num_questions: int = 5, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        index = self._get_index()
        embedder = self._get_embedder()

        seed = f"query: {topic}" if topic else "query: main concepts and key information"
        q_vec = embedder.encode([seed], normalize_embeddings=True)[0]
        results = index.query(
            vector=[float(x) for x in q_vec], top_k=30, include_metadata=True
        )
        matches = results.get("matches", []) if isinstance(results, dict) else results.matches
        seen = set()
        contexts: List[str] = []
        for m in matches:
            meta = m.get("metadata", {}) if isinstance(m, dict) else (m.metadata or {})
            txt = (meta or {}).get("text", "")
            key = txt[:80]
            if txt and key not in seen:
                seen.add(key)
                contexts.append(re.sub(r"\s+", " ", txt).strip()[:500])
            if len(contexts) >= 10:
                break

        return self._generate_quiz_questions(contexts, num_questions)

    # ---------- LLM helpers ----------
    def _generate_answer(self, question: str, contexts: List[str]) -> str:
        joined = "\n".join(f"- {c}" for c in contexts[:5])
        if not self.gemini_api_key:
            if not contexts:
                return "No relevant context was found for this question."
            return "Based on the document context:\n" + joined
        prompt = (
            "You are a helpful educational assistant. Answer the question based ONLY "
            "on the provided context.\n\n"
            f"Question: {question}\n\n"
            f"Context from document:\n{joined}\n\n"
            "Instructions:\n"
            "- Provide a clear, concise answer in 2-4 sentences\n"
            "- Use only information from the context provided\n"
            "- If the context doesn't contain enough information, say so\n"
            "- Format your answer in plain text, no markdown\n\n"
            "Answer:"
        )
        text = self._call_gemini(prompt)
        if not text:
            if not contexts:
                return "No relevant context was found for this question."
            return "Based on the document context:\n" + joined
        return text.strip()

    def _generate_quiz_questions(self, contexts: List[str], num_questions: int) -> List[Dict[str, Any]]:
        joined = "\n".join(contexts)
        if not self.gemini_api_key or not joined.strip():
            return self._fallback_quiz(contexts, num_questions)
        prompt = (
            f"You are an expert quiz creator. Generate exactly {num_questions} high-quality "
            "multiple-choice quiz questions.\n\n"
            f"Content:\n{joined}\n\n"
            "Requirements:\n"
            "- Each question should test understanding of key concepts\n"
            "- Provide 4 multiple choice options (A, B, C, D)\n"
            "- Make questions clear and specific\n"
            "- Ensure correct answers are accurate based on content\n"
            "- Return ONLY a valid JSON array\n\n"
            'Format:\n[{"question": "...", "choices": ["...", "...", "...", "..."], "correct": "A"}]'
        )
        raw = self._call_gemini(prompt)
        parsed = self._parse_quiz_json(raw)
        if parsed:
            return parsed[:num_questions]
        return self._fallback_quiz(contexts, num_questions)

    def _fallback_quiz(self, contexts: List[str], num_questions: int) -> List[Dict[str, Any]]:
        questions: List[Dict[str, Any]] = []
        for ctx in contexts[:num_questions]:
            snippet = ctx.strip()
            if not snippet:
                continue
            questions.append(
                {
                    "question": f"Which statement is supported by the document? ({snippet[:80]}...)",
                    "choices": [
                        snippet[:120],
                        "None of the document content supports this.",
                        "The document contradicts this statement.",
                        "The document does not mention this topic.",
                    ],
                    "correct": "A",
                }
            )
        return questions

    def _parse_quiz_json(self, raw: str) -> List[Dict[str, Any]]:
        if not raw:
            return []
        text = raw.strip()
        fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
        if fence:
            text = fence.group(1).strip()
        start = text.find("[")
        end = text.rfind("]")
        if start == -1 or end == -1 or end <= start:
            return []
        try:
            data = json.loads(text[start : end + 1])
        except Exception:
            return []
        cleaned: List[Dict[str, Any]] = []
        for item in data if isinstance(data, list) else []:
            if not isinstance(item, dict):
                continue
            question = item.get("question")
            choices = item.get("choices")
            correct = item.get("correct")
            if not question or not isinstance(choices, list) or len(choices) < 2:
                continue
            cleaned.append(
                {
                    "question": str(question),
                    "choices": [str(c) for c in choices[:4]],
                    "correct": str(correct).strip().upper() if correct else "A",
                }
            )
        return cleaned

    def _call_gemini(self, prompt: str) -> str:
        models = ["gemini-2.0-flash-exp", "gemini-1.5-flash"]
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 500},
        }
        params = {"key": self.gemini_api_key}
        for model in models:
            url = (
                "https://generativelanguage.googleapis.com/v1beta/models/"
                f"{model}:generateContent"
            )
            try:
                with httpx.Client(timeout=45) as client:
                    r = client.post(url, headers=headers, params=params, json=payload)
                    r.raise_for_status()
                    data = r.json()
                    return (
                        data.get("candidates", [{}])[0]
                        .get("content", {})
                        .get("parts", [{}])[0]
                        .get("text", "")
                    )
            except Exception:
                continue
        return ""
