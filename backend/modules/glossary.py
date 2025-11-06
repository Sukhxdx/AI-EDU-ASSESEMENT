from typing import Dict
import re
import os
import httpx


class GlossaryBuilder:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

    def build_glossary(self, text: str, target_lang: str = "en", top_k: int = 15) -> Dict[str, Dict[str, str]]:
        words = self._extract_keywords(text)
        words = words[:top_k]
        glossary = {}
        for w in words:
            definition = self._define_word(w, text)
            translation = self._translate_word(w, target_lang)
            glossary[w] = {"definition": definition, "translation": translation}
        return glossary

    def _extract_keywords(self, text: str):
        tokens = re.findall(r"[A-Za-z']+", text.lower())
        common = set(["the","and","is","in","to","of","a","for","on","with","as","by","an","or","be","are","this","that","it","from","at"]) 
        freq = {}
        for t in tokens:
            if t in common or len(t) < 4:
                continue
            freq[t] = freq.get(t, 0) + 1
        return [w for w, _ in sorted(freq.items(), key=lambda kv: kv[1], reverse=True)]

    def _define_word(self, word: str, context: str) -> str:
        if not self.gemini_api_key:
            return f"Key term related to the provided context."
        try:
            prompt = f"Define the term '{word}' in 1 concise sentence for a student. Context: {context[:500]}"
            resp = self._call_gemini(prompt)
            return resp.strip() or "Definition unavailable"
        except Exception:
            return "Definition unavailable"

    def _translate_word(self, word: str, target_lang: str) -> str:
        if target_lang == "en":
            return word
        if not self.gemini_api_key:
            return word  # fallback: no translation
        try:
            prompt = f"Translate the term '{word}' to language code {target_lang}. Only output the translation."
            resp = self._call_gemini(prompt)
            return resp.strip() or word
        except Exception:
            return word

    def _call_gemini(self, prompt: str) -> str:
        # Gemini 1.5/2.5 API (text-only simple call via REST)
        # Endpoint pattern example; adjust if needed by your account/region
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

