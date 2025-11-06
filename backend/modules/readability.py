from typing import Dict, Any
import re


class ReadabilityAnalyzer:
    def analyze_text(self, text: str) -> Dict[str, Any]:
        words = self._split_words(text)
        sentences = self._split_sentences(text)
        syllables = sum(self._count_syllables(w) for w in words)

        num_words = max(len(words), 1)
        num_sentences = max(len(sentences), 1)
        num_syllables = max(syllables, 1)

        words_per_sentence = num_words / num_sentences
        syllables_per_word = num_syllables / num_words

        # Flesch Reading Ease (approx)
        flesch = 206.835 - (1.015 * words_per_sentence) - (84.6 * syllables_per_word)
        # Flesch-Kincaid Grade Level (approx)
        fkgl = (0.39 * words_per_sentence) + (11.8 * syllables_per_word) - 15.59

        return {
            "num_words": num_words,
            "num_sentences": num_sentences,
            "avg_words_per_sentence": round(words_per_sentence, 2),
            "avg_syllables_per_word": round(syllables_per_word, 2),
            "flesch_reading_ease": round(flesch, 2),
            "flesch_kincaid_grade": round(fkgl, 2),
        }

    def _split_sentences(self, text: str):
        return [s for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]

    def _split_words(self, text: str):
        return re.findall(r"[A-Za-z']+", text)

    def _count_syllables(self, word: str) -> int:
        word = word.lower()
        vowels = "aeiouy"
        count = 0
        prev_is_vowel = False
        for ch in word:
            is_vowel = ch in vowels
            if is_vowel and not prev_is_vowel:
                count += 1
            prev_is_vowel = is_vowel
        if word.endswith("e") and count > 1:
            count -= 1
        return max(count, 1)

