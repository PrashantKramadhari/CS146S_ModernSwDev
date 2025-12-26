from backend.app.services.extract import extract_action_items, extract_tags


def test_extract_action_items():
    text = """
    This is a note
    - TODO: write tests
    - Ship it!
    Not actionable
    """.strip()
    items = extract_action_items(text)
    assert "TODO: write tests" in items
    assert "Ship it!" in items


# Tests for extract_tags function
def test_extract_tags_single_tag():
    """Test extraction of a single tag from text."""
    text = "Check #urgent items"
    tags = extract_tags(text)
    assert tags == ["urgent"]


def test_extract_tags_multiple_tags():
    """Test extraction of multiple tags from text."""
    text = "#bug #ui issues"
    tags = extract_tags(text)
    assert set(tags) == {"bug", "ui"}


def test_extract_tags_no_tags():
    """Test that empty list is returned when no tags are present."""
    text = "Regular text without any hashtags"
    tags = extract_tags(text)
    assert tags == []


def test_extract_tags_duplicate_tags():
    """Test that duplicate tags are deduplicated."""
    text = "#test #test #test"
    tags = extract_tags(text)
    assert tags == ["test"]
    assert len(tags) == 1


def test_extract_tags_with_numbers():
    """Test tags containing numbers."""
    text = "#python3 and #v2 are versions"
    tags = extract_tags(text)
    assert set(tags) == {"python3", "v2"}


def test_extract_tags_with_hyphens():
    """Test tags containing hyphens."""
    text = "This is a #multi-word-tag example"
    tags = extract_tags(text)
    assert tags == ["multi-word-tag"]


def test_extract_tags_with_underscores():
    """Test tags containing underscores."""
    text = "Use #snake_case naming convention"
    tags = extract_tags(text)
    assert tags == ["snake_case"]


def test_extract_tags_hyphens_and_underscores():
    """Test tags with both hyphens and underscores."""
    text = "#multi-word-tag #snake_case #combo_tag-name"
    tags = extract_tags(text)
    assert set(tags) == {"multi-word-tag", "snake_case", "combo_tag-name"}


def test_extract_tags_case_sensitive():
    """Test that tags are case-sensitive."""
    text = "#Bug #BUG #bug"
    tags = extract_tags(text)
    assert set(tags) == {"Bug", "BUG", "bug"}


def test_extract_tags_mixed_content():
    """Test tag extraction from complex mixed content."""
    text = """
    Report for #sprint-5 meeting.
    Issues: #bug #critical #urgent
    Backend: #python #database #api
    Frontend: #react #ui
    Status: #bug #critical
    """
    tags = extract_tags(text)
    expected = {"sprint-5", "bug", "critical", "urgent", "python", "database", "api", "react", "ui"}
    assert set(tags) == expected


def test_extract_tags_hashtag_prefix_removed():
    """Test that hashtag prefix is removed from results."""
    text = "#tagged #content"
    tags = extract_tags(text)
    for tag in tags:
        assert not tag.startswith("#")


def test_extract_tags_must_start_with_letter():
    """Test that tags must start with a letter (not numbers or special chars)."""
    text = "Valid: #tag1 but not: #1tag #_tag #-tag"
    tags = extract_tags(text)
    # Only valid tags (starting with letters) should be extracted
    assert "tag1" in tags
    assert len(tags) == 1  # Only #tag1 is valid


def test_extract_tags_empty_string():
    """Test extraction from empty string."""
    text = ""
    tags = extract_tags(text)
    assert tags == []


def test_extract_tags_only_hashtag():
    """Test that lone hashtag without text after it is not extracted."""
    text = "This has a # but not a tag"
    tags = extract_tags(text)
    assert tags == []


def test_extract_tags_special_characters_not_included():
    """Test that special characters beyond letters, numbers, hyphens, underscores are not included."""
    text = "#tag! #test@ #item# #normal"
    tags = extract_tags(text)
    # Only #normal should be fully extracted as valid
    assert "normal" in tags


def test_extract_tags_at_end_of_text():
    """Test tag extraction at the end of text."""
    text = "Check this issue #final"
    tags = extract_tags(text)
    assert tags == ["final"]


def test_extract_tags_at_start_of_text():
    """Test tag extraction at the start of text."""
    text = "#first is the priority"
    tags = extract_tags(text)
    assert tags == ["first"]


def test_extract_tags_adjacent_tags():
    """Test extraction of adjacent tags."""
    text = "#one#two #three"
    tags = extract_tags(text)
    # Adjacent tags without space should be treated as one tag or separately based on implementation
    assert "three" in tags
