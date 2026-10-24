from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)

def test_health(): assert client.get("/health").json()["ok"]

def test_security_finding():
    r=client.post("/review",json={"repository":"demo","pull_request":1,"diff":"eval(user_input)"})
    assert r.status_code==200
    assert any(x["category"]=="security" for x in r.json()["findings"])

def test_test_generation():
    r=client.post("/generate-tests",json={"repository":"demo","pull_request":2,"diff":"def add(a,b): return a+b"})
    assert r.status_code==200
    assert r.json()["framework"]=="pytest"
