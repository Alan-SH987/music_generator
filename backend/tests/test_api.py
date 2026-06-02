"""API endpoint tests."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _generate(client: TestClient, **body) -> dict:
    body.setdefault("scene", "finance")
    body.setdefault("duration", 5)
    resp = client.post("/api/generate_music", json=body)
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_health(client: TestClient) -> None:
    data = client.get("/api/health").json()
    assert data["status"] == "ok"


def test_scenes(client: TestClient) -> None:
    scenes = client.get("/api/scenes").json()
    keys = {s["key"] for s in scenes}
    assert keys == {"finance", "reading", "tech", "meditation", "cafe", "sports", "golf"}
    for scene in scenes:
        assert scene["label_zh"] and scene["label_en"]
        assert 40 <= scene["default_bpm"] <= 200


def test_providers(client: TestClient) -> None:
    providers = {p["key"]: p["implemented"] for p in client.get("/api/providers").json()}
    assert providers == {
        "mock": True,
        "mubert": False,
        "local_loop": False,
        "stable_audio": False,
    }


def test_policy(client: TestClient) -> None:
    policy = client.get("/api/policy").json()
    assert policy["rules"]
    assert "calm" in policy["moods"]
    assert policy["default_provider"] == "mock"


def test_generate_history_download(client: TestClient, decode_wav) -> None:
    gen = _generate(client, scene="tech", duration=6, bpm=110, intensity=6)
    assert gen["provider"] == "mock"
    assert gen["source_type"] == "mock_synthesis"
    assert gen["license_note"]
    assert gen["prompt"]

    history = client.get("/api/history").json()
    assert [g["id"] for g in history] == [gen["id"]]

    audio = client.get(gen["audio_url"])
    assert audio.status_code == 200
    assert audio.headers["content-type"] == "audio/wav"
    frames = decode_wav(audio.content)
    # stereo, 44.1k, exactly `duration` seconds
    assert frames.shape == (6 * 44_100, 2)


def test_download_supports_range(client: TestClient) -> None:
    gen = _generate(client)
    resp = client.get(gen["audio_url"], headers={"Range": "bytes=0-99"})
    assert resp.status_code == 206
    assert resp.headers["content-range"].startswith("bytes 0-99/")
    assert len(resp.content) == 100


def test_download_attachment_disposition(client: TestClient) -> None:
    gen = _generate(client)
    inline = client.get(gen["audio_url"])
    assert "inline" in inline.headers["content-disposition"]
    attach = client.get(gen["audio_url"], params={"download": "true"})
    assert "attachment" in attach.headers["content-disposition"]


def test_generate_unknown_scene_400(client: TestClient) -> None:
    resp = client.post("/api/generate_music", json={"scene": "nope", "duration": 5})
    assert resp.status_code == 400
    assert "Unknown scene" in resp.json()["detail"]


def test_generate_placeholder_provider_501(client: TestClient) -> None:
    resp = client.post(
        "/api/generate_music",
        json={"scene": "finance", "duration": 5, "provider": "mubert"},
    )
    assert resp.status_code == 501


def test_generate_validation_422(client: TestClient) -> None:
    # duration below the allowed minimum
    resp = client.post("/api/generate_music", json={"scene": "finance", "duration": 1})
    assert resp.status_code == 422


def test_download_unknown_404(client: TestClient) -> None:
    assert client.get("/api/download/does-not-exist").status_code == 404


def test_delete_one(client: TestClient) -> None:
    gen = _generate(client)
    assert client.delete(f"/api/history/{gen['id']}").status_code == 204
    assert client.get("/api/history").json() == []
    # audio file removed, so download 404s
    assert client.get(gen["audio_url"]).status_code == 404


def test_delete_missing_404(client: TestClient) -> None:
    assert client.delete("/api/history/does-not-exist").status_code == 404


def test_clear_history(client: TestClient) -> None:
    from app.config import settings

    for _ in range(3):
        _generate(client)
    assert len(client.get("/api/history").json()) == 3
    cleared = client.delete("/api/history").json()
    assert cleared["deleted"] == 3
    assert client.get("/api/history").json() == []
    assert list(settings.audio_dir.glob("*.wav")) == []
