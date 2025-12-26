def test_create_and_complete_action_item(client):
    payload = {"description": "Ship it"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201, r.text
    item = r.json()
    assert item["completed"] is False

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200
    done = r.json()
    assert done["completed"] is True

    r = client.get("/action-items/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1


def test_create_action_item_empty_description(client):
    """Test that empty description returns 422 validation error"""
    payload = {"description": ""}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 422, r.text
    data = r.json()
    assert "detail" in data or "validation_error" in str(data).lower()


def test_create_action_item_missing_description(client):
    """Test that missing description field returns 422 validation error"""
    payload = {}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 422, r.text
    data = r.json()
    assert "detail" in data or "validation_error" in str(data).lower()


def test_delete_action_item_success(client):
    """Test successful deletion of an existing action item"""
    # Create an action item
    create_payload = {"description": "Item to Delete"}
    create_r = client.post("/action-items/", json=create_payload)
    assert create_r.status_code == 201
    item = create_r.json()
    item_id = item["id"]

    # Verify the item exists
    get_r = client.get("/action-items/")
    assert get_r.status_code == 200
    items = get_r.json()
    assert any(i["id"] == item_id for i in items)

    # Delete the action item
    delete_r = client.delete(f"/action-items/{item_id}")
    assert delete_r.status_code == 204, delete_r.text

    # Verify the action item is gone
    get_r = client.get("/action-items/")
    assert get_r.status_code == 200
    items = get_r.json()
    assert not any(i["id"] == item_id for i in items), "Action item should not exist after deletion"


def test_delete_action_item_not_found(client):
    """Test that deleting a non-existent action item returns 404"""
    delete_r = client.delete("/action-items/99999")
    assert delete_r.status_code == 404, delete_r.text
    data = delete_r.json()
    assert "detail" in data


def test_delete_action_item_removes_from_list(client):
    """Test that deleting an action item removes it from the list"""
    # Create multiple action items
    item_ids = []
    for i in range(3):
        create_payload = {"description": f"Action Item {i+1}"}
        create_r = client.post("/action-items/", json=create_payload)
        assert create_r.status_code == 201
        item_ids.append(create_r.json()["id"])

    # Get initial count
    list_r = client.get("/action-items/")
    assert list_r.status_code == 200
    initial_count = len(list_r.json())
    assert initial_count >= 3

    # Delete the first action item
    delete_r = client.delete(f"/action-items/{item_ids[0]}")
    assert delete_r.status_code == 204, delete_r.text

    # Get new count and verify it decreased
    list_r = client.get("/action-items/")
    assert list_r.status_code == 200
    new_count = len(list_r.json())
    assert new_count == initial_count - 1, "List count should decrease by 1"

    # Verify the deleted item is not in the list
    items = list_r.json()
    items_ids_in_list = [item["id"] for item in items]
    assert item_ids[0] not in items_ids_in_list, "Deleted action item should not appear in list"

    # Verify other items still exist
    assert item_ids[1] in items_ids_in_list, "Other action items should still exist"
    assert item_ids[2] in items_ids_in_list, "Other action items should still exist"
