from typing import List, Dict, Optional
import os
import re
import httpx


class QuizGenerator:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

    def generate(self, text: str, num_questions: int = 5) -> List[Dict]:
        sentences = self._split_sentences(text)
        candidates = self._select_candidates(sentences, k=max(num_questions * 2, 10))
        questions: List[Dict] = []
        for cand in candidates:
            if len(questions) >= num_questions:
                break
            q_text = self._generate_from_sentence(cand)
            if not q_text:
                q_text = self._heuristic_question(cand)
            formatted = self._format_question(q_text)
            if formatted and formatted.get("question"):
                questions.append(formatted)
        return questions

    def _split_sentences(self, text: str) -> List[str]:
        return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.split()) > 6]

    def _select_candidates(self, sentences: List[str], k: int = 10) -> List[str]:
        scored = [(len(s), s) for s in sentences]
        scored.sort(reverse=True)
        return [s for _, s in scored[:k]]

    def _generate_from_sentence(self, sentence: str) -> Optional[str]:
        if not self.gemini_api_key:
            return None
        prompt = (
            "Create one clear question from the sentence below. Only output the question.\n"
            f"Sentence: {sentence}"
        )
        try:
            return self._call_gemini(prompt)
        except Exception:
            return None

    def _heuristic_question(self, sentence: str) -> str:
        base = sentence.strip()
        base = re.sub(r"^[A-Z][a-z]+\s*,\s*", "", base)
        if not base.endswith("?"):
            base = base.rstrip(".") + "?"
        return base

    def _format_question(self, q_text: str) -> Dict:
        q = q_text.strip()
        if not q.endswith("?"):
            q += "?"
        return {"question": q, "answer": "", "choices": None}

    def _call_gemini(self, prompt: str) -> str:
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        params = {"key": self.gemini_api_key}
        with httpx.Client(timeout=30) as client:
            r = client.post(url, headers=headers, params=params, json=payload)
            r.raise_for_status()
            data = r.json()
            text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            return text

