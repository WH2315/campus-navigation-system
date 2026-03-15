from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_route_plan() -> None:
    payload = {
        "start_id": "gate_north",
        "end_id": "stadium",
        "avoid_crowded": True,
        "prefer_indoor": False,
    }
    resp = client.post("/api/v1/route/plan", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["node_path"][0] == "gate_north"
    assert data["node_path"][-1] == "stadium"
    assert data["total_distance"] > 0


def test_guide_generate_fallback() -> None:
    payload = {
        "user_profile": "new_student",
        "style": "friendly",
        "language": "zh",
        "route_nodes": ["gate_north", "library", "teaching_a"],
    }
    resp = client.post("/api/v1/guide/generate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["script"]) > 0


def test_spot_list() -> None:
    resp = client.get("/api/v1/spots")
    assert resp.status_code == 200
    data = resp.json()
    assert "spots" in data
    assert len(data["spots"]) > 0
    assert "node_id" in data["spots"][0]


def test_spot_guide_generate() -> None:
    payload = {
        "node_id": "library",
        "user_profile": "new_student",
        "style": "friendly",
        "language": "zh",
    }
    resp = client.post("/api/v1/guide/spot-generate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["title"]) > 0
    assert len(data["script"]) > 0


def test_chat() -> None:
    payload = {
        "question": "图书馆开放时间是什么时候？",
        "language": "zh",
        "current_spot_id": "library",
    }
    resp = client.post("/api/v1/session/chat", json=payload)
    assert resp.status_code == 200
    assert len(resp.json()["answer"]) > 0


def test_asr() -> None:
    fake_wav = b"RIFF1234WAVEfmt "
    files = {"audio": ("question.wav", fake_wav, "audio/wav")}
    data = {"language": "zh"}
    resp = client.post("/api/v1/speech/asr", files=files, data=data)
    assert resp.status_code == 200
    assert len(resp.json()["text"]) > 0


def test_voice_chat() -> None:
    fake_wav = b"RIFF1234WAVEfmt "
    files = {"audio": ("question.wav", fake_wav, "audio/wav")}
    data = {"language": "zh", "current_spot_id": "library"}
    resp = client.post("/api/v1/session/voice-chat", files=files, data=data)
    assert resp.status_code == 200
    payload = resp.json()
    assert len(payload["transcript"]) > 0
    assert len(payload["answer"]) > 0
