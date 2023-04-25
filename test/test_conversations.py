from fastapi.testclient import TestClient
from src.api.server import app

import json

client = TestClient(app)

def test_get_conversation():
    response = client.get("/conversations/83079")
    assert response.status_code == 200

    with open(
        "test/conversations/83079.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)

def test_get_line():
    response = client.get("/lines/666228")
    assert response.status_code == 200

    with open(
        "test/lines/666228.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)


