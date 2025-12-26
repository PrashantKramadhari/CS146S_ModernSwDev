def test_create_and_list_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/search/")
    assert r.status_code == 200

    r = client.get("/notes/search/", params={"q": "Hello"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1


def test_create_note_empty_title(client):
    """Test that empty title returns 422 validation error"""
    payload = {"title": "", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 422, r.text
    data = r.json()
    assert "detail" in data or "validation_error" in str(data).lower()


def test_create_note_title_too_long(client):
    """Test that title exceeding 200 characters returns 422 validation error"""
    long_title = "a" * 201  # 201 characters
    payload = {"title": long_title, "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 422, r.text
    data = r.json()
    assert "detail" in data or "validation_error" in str(data).lower()


def test_create_note_empty_content(client):
    """Test that empty content returns 422 validation error"""
    payload = {"title": "Valid Title", "content": ""}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 422, r.text
    data = r.json()
    assert "detail" in data or "validation_error" in str(data).lower()


def test_create_note_missing_fields(client):
    """Test that missing required fields returns 422 validation error"""
    # Missing both title and content
    payload = {}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 422, r.text
    data = r.json()
    assert "detail" in data or "validation_error" in str(data).lower()

    # Missing title only
    payload = {"content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 422, r.text
    data = r.json()
    assert "detail" in data or "validation_error" in str(data).lower()

    # Missing content only
    payload = {"title": "Test"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 422, r.text
    data = r.json()
    assert "detail" in data or "validation_error" in str(data).lower()


def test_update_note_success(client):
    """Test successful update of an existing note"""
    # Create a note
    create_payload = {"title": "Original Title", "content": "Original content"}
    create_r = client.post("/notes/", json=create_payload)
    assert create_r.status_code == 201
    note = create_r.json()
    note_id = note["id"]

    # Update the note
    update_payload = {"title": "Updated Title", "content": "Updated content"}
    update_r = client.put(f"/notes/{note_id}", json=update_payload)
    assert update_r.status_code == 200, update_r.text
    updated_note = update_r.json()

    # Assert response contains updated title and content
    assert updated_note["title"] == "Updated Title"
    assert updated_note["content"] == "Updated content"
    assert updated_note["id"] == note_id

    # Verify by fetching the note again
    get_r = client.get(f"/notes/{note_id}")
    assert get_r.status_code == 200
    fetched_note = get_r.json()
    assert fetched_note["title"] == "Updated Title"
    assert fetched_note["content"] == "Updated content"


def test_update_note_not_found(client):
    """Test that updating a non-existent note returns 404"""
    payload = {"title": "Some Title", "content": "Some content"}
    r = client.put("/notes/99999", json=payload)
    assert r.status_code == 404, r.text
    data = r.json()
    assert "detail" in data


def test_update_note_partial_title_only(client):
    """Test updating only the title while keeping content unchanged"""
    # Create a note
    create_payload = {"title": "Original Title", "content": "Original content"}
    create_r = client.post("/notes/", json=create_payload)
    assert create_r.status_code == 201
    note = create_r.json()
    note_id = note["id"]

    # Update only the title
    update_payload = {"title": "New Title", "content": "Original content"}
    update_r = client.put(f"/notes/{note_id}", json=update_payload)
    assert update_r.status_code == 200, update_r.text
    updated_note = update_r.json()

    # Assert title changed and content unchanged
    assert updated_note["title"] == "New Title"
    assert updated_note["content"] == "Original content"

    # Verify by fetching the note again
    get_r = client.get(f"/notes/{note_id}")
    assert get_r.status_code == 200
    fetched_note = get_r.json()
    assert fetched_note["title"] == "New Title"
    assert fetched_note["content"] == "Original content"


def test_update_note_partial_content_only(client):
    """Test updating only the content while keeping title unchanged"""
    # Create a note
    create_payload = {"title": "Original Title", "content": "Original content"}
    create_r = client.post("/notes/", json=create_payload)
    assert create_r.status_code == 201
    note = create_r.json()
    note_id = note["id"]

    # Update only the content
    update_payload = {"title": "Original Title", "content": "New content"}
    update_r = client.put(f"/notes/{note_id}", json=update_payload)
    assert update_r.status_code == 200, update_r.text
    updated_note = update_r.json()

    # Assert content changed and title unchanged
    assert updated_note["title"] == "Original Title"
    assert updated_note["content"] == "New content"

    # Verify by fetching the note again
    get_r = client.get(f"/notes/{note_id}")
    assert get_r.status_code == 200
    fetched_note = get_r.json()
    assert fetched_note["title"] == "Original Title"
    assert fetched_note["content"] == "New content"


def test_delete_note_success(client):
    """Test successful deletion of an existing note"""
    # Create a note
    create_payload = {"title": "Note to Delete", "content": "This will be deleted"}
    create_r = client.post("/notes/", json=create_payload)
    assert create_r.status_code == 201
    note = create_r.json()
    note_id = note["id"]

    # Verify the note exists
    get_r = client.get(f"/notes/{note_id}")
    assert get_r.status_code == 200
    assert get_r.json()["title"] == "Note to Delete"

    # Delete the note
    delete_r = client.delete(f"/notes/{note_id}")
    assert delete_r.status_code == 204, delete_r.text

    # Verify the note is gone
    get_r = client.get(f"/notes/{note_id}")
    assert get_r.status_code == 404, "Note should not exist after deletion"


def test_delete_note_not_found(client):
    """Test that deleting a non-existent note returns 404"""
    delete_r = client.delete("/notes/99999")
    assert delete_r.status_code == 404, delete_r.text
    data = delete_r.json()
    assert "detail" in data


def test_delete_note_removes_from_list(client):
    """Test that deleting a note removes it from the list"""
    # Create multiple notes
    note_ids = []
    for i in range(3):
        create_payload = {"title": f"Note {i+1}", "content": f"Content {i+1}"}
        create_r = client.post("/notes/", json=create_payload)
        assert create_r.status_code == 201
        note_ids.append(create_r.json()["id"])

    # Get initial count
    list_r = client.get("/notes/")
    assert list_r.status_code == 200
    initial_count = len(list_r.json())
    assert initial_count >= 3

    # Delete the first note
    delete_r = client.delete(f"/notes/{note_ids[0]}")
    assert delete_r.status_code == 204, delete_r.text

    # Get new count and verify it decreased
    list_r = client.get("/notes/")
    assert list_r.status_code == 200
    new_count = len(list_r.json())
    assert new_count == initial_count - 1, "List count should decrease by 1"

    # Verify the deleted note is not in the list
    notes = list_r.json()
    note_ids_in_list = [note["id"] for note in notes]
    assert note_ids[0] not in note_ids_in_list, "Deleted note should not appear in list"

    # Verify other notes still exist
    assert note_ids[1] in note_ids_in_list, "Other notes should still exist"
    assert note_ids[2] in note_ids_in_list, "Other notes should still exist"
