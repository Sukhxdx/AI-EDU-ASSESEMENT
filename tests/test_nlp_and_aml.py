from aml_monitor import AmlMonitor
from banking_chatbot import BankingChatbot
from kyc_classifier import KycClassifier
from news_sentiment import NewsSentiment
from spend_categorizer import SpendCategorizer


def test_chatbot_blocks_card_intent():
    reply = BankingChatbot().respond("please block my debit card immediately it is stolen")
    assert reply.intent == "card_block"
    assert reply.confidence > 0.4
    assert "card" in reply.reply.lower()


def test_chatbot_fallback_on_noise():
    reply = BankingChatbot().respond("who won the cricket match yesterday")
    assert reply.intent == "fallback"


def test_kyc_pan_is_accepted():
    text = (
        "INCOME TAX DEPARTMENT GOVT OF INDIA Permanent Account Number Card ABCDE1234F "
        "Name RAHUL SHARMA Father's Name VIJAY SHARMA Date of Birth 12/03/1992"
    )
    result = KycClassifier().assess(text)
    assert result.doc_type == "pan"
    assert result.fields.get("pan") == "ABCDE1234F"
    assert result.accepted is True


def test_kyc_rejects_grocery_receipt():
    result = KycClassifier().assess("Grocery receipt tomato onion milk total 430 thank you visit again")
    assert result.accepted is False


def test_spend_swiggy_is_dining():
    result = SpendCategorizer().classify("SWIGGY *ORDER #441")
    assert result.category == "dining"


def test_news_profit_beat_is_positive():
    result = NewsSentiment().score("Private bank profits beat street estimates in Q2")
    assert result.label == "positive"


def test_aml_structuring_alert():
    txns = [
        {"amount": 490000, "counterparty_country": "CY", "channel": "cash", "direction": "in", "hours_since_inflow": 1},
        {"amount": 485000, "counterparty_country": "PA", "channel": "cash", "direction": "out", "hours_since_inflow": 2},
        {"amount": 470000, "counterparty_country": "AE", "channel": "cash", "direction": "out", "hours_since_inflow": 3},
    ]
    alert = AmlMonitor().evaluate_customer(txns, "CUSTX")
    assert alert.alert_score >= 65
    assert "structuring" in alert.typologies
