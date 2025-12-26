def test_create_and_complete_action_item(client):
    payload = {"description": "Ship it"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["ok"] is True
    item = body["data"]
    assert item["completed"] is False

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    done = body["data"]
    assert done["completed"] is True

    r = client.get("/action-items/")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    data = body["data"]
    assert len(data["items"]) == 1


def test_complete_missing_action_item_returns_envelope(client):
    r = client.put("/action-items/9999/complete")
    assert r.status_code == 404
    body = r.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "NOT_FOUND"


def test_pagination_boundaries_for_action_items(client):
    # create 3 items
    for i in range(3):
        r = client.post("/action-items/", json={"description": f"Item {i}"})
        assert r.status_code == 201

    # page size larger than max is clamped
    r = client.get("/action-items/", params={"page": 1, "page_size": 1000})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    data = body["data"]
    assert data["total"] == 4  # 3 new + 1 from previous test

    # empty last page
    r = client.get("/action-items/", params={"page": 10, "page_size": 5})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    data = body["data"]
    assert data["items"] == []
