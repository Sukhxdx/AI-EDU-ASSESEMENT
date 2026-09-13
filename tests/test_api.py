from fastapi.testclient import TestClient

from api import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_endpoint():
    response = client.post("/chat", json={"text": "what is my account balance"})
    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "balance_inquiry"
    assert body["reply"]


def test_fraud_endpoint():
    response = client.post(
        "/fraud/score",
        json={"amount": 1200, "hour": 11, "merchant_category": "fuel"},
    )
    assert response.status_code == 200
    assert "risk_score" in response.json()
