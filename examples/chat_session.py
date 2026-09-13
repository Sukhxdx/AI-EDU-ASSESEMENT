"""Print chatbot intents for a short script of customer lines."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from banking_chatbot import BankingChatbot

LINES = [
    "hi",
    "block my debit card I lost my wallet",
    "what is my account balance",
    "update KYC with aadhaar",
    "personal loan eligibility",
    "unauthorised UPI debit please help",
    "thanks bye",
]


def main() -> None:
    bot = BankingChatbot()
    for line in LINES:
        reply = bot.respond(line)
        print(f"> {line}")
        print(f"  [{reply.intent} | {reply.confidence:.0%}] {reply.reply}\n")


if __name__ == "__main__":
    main()
