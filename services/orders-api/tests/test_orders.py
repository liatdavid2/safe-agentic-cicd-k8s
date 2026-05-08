from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_orders_endpoint():
    response = client.get("/orders")
    assert response.status_code == 200
    body = response.json()
    assert body["count"] >= 1
    assert isinstance(body["orders"], list)


def test_create_order():
    response = client.post("/orders", json={"customer_id": "cust-003", "amount": 42.0})
    assert response.status_code == 200
    assert response.json()["status"] == "created"
