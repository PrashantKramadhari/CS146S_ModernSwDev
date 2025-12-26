def test_create_and_list_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["ok"] is True
    note = body["data"]
    assert note["title"] == "Test"

    r = client.get("/notes/")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    data = body["data"]
    assert "items" in data
    assert data["total"] >= 1

    r = client.get("/notes/search/")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True

    r = client.get("/notes/search/", params={"q": "Hello"})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    items = body["data"]
    assert len(items) >= 1


def test_get_missing_note_returns_envelope(client):
    r = client.get("/notes/9999")
    assert r.status_code == 404
    body = r.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "NOT_FOUND"
