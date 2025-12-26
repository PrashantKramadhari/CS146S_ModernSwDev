import os
import json
import pytest
from unittest.mock import patch

from ..app.services.extract import extract_action_items, extract_action_items_llm


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


def test_extract_action_items_llm_bullets_and_checkboxes():
    """Test LLM extraction with bullet lists and checkboxes."""
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    # Mock Ollama response
    mock_response = {
        "message": {
            "content": json.dumps({
                "action_items": [
                    "Set up database",
                    "implement API extract endpoint",
                    "Write tests"
                ]
            })
        }
    }

    with patch("app.services.extract.chat", return_value=mock_response):
        items = extract_action_items_llm(text)
        assert "Set up database" in items
        assert "implement API extract endpoint" in items
        assert "Write tests" in items


def test_extract_action_items_llm_keyword_prefixes():
    """Test LLM extraction with keyword-prefixed lines."""
    text = """
    Meeting notes:
    todo: Review the code changes
    action: Schedule follow-up meeting
    next: Update documentation
    This is just a regular note.
    """.strip()

    mock_response = {
        "message": {
            "content": json.dumps({
                "action_items": [
                    "Review the code changes",
                    "Schedule follow-up meeting",
                    "Update documentation"
                ]
            })
        }
    }

    with patch("app.services.extract.chat", return_value=mock_response):
        items = extract_action_items_llm(text)
        assert "Review the code changes" in items
        assert "Schedule follow-up meeting" in items
        assert "Update documentation" in items


def test_extract_action_items_llm_empty_input():
    """Test LLM extraction with empty input."""
    text = ""

    items = extract_action_items_llm(text)
    assert items == []

    text_whitespace = "   \n\t  "
    items = extract_action_items_llm(text_whitespace)
    assert items == []


def test_extract_action_items_llm_mixed_content():
    """Test LLM extraction with mixed narrative and action items."""
    text = """
    We discussed several topics in today's meeting. The team is making good progress.
    - Fix the bug in the authentication module
    - Add error handling to the API
    We also talked about next week's goals and priorities.
    todo: Write unit tests for the new feature
    action: Deploy to staging environment
    """.strip()

    mock_response = {
        "message": {
            "content": json.dumps({
                "action_items": [
                    "Fix the bug in the authentication module",
                    "Add error handling to the API",
                    "Write unit tests for the new feature",
                    "Deploy to staging environment"
                ]
            })
        }
    }

    with patch("app.services.extract.chat", return_value=mock_response):
        items = extract_action_items_llm(text)
        assert len(items) == 4
        assert "Fix the bug in the authentication module" in items
        assert "Add error handling to the API" in items
        assert "Write unit tests for the new feature" in items
        assert "Deploy to staging environment" in items


def test_extract_action_items_llm_deduplication():
    """Test that LLM extraction deduplicates items."""
    text = """
    - Complete the report
    - Complete the report
    todo: Complete the report
    """.strip()

    mock_response = {
        "message": {
            "content": json.dumps({
                "action_items": [
                    "Complete the report",
                    "Complete the report",
                    "Complete the report"
                ]
            })
        }
    }

    with patch("app.services.extract.chat", return_value=mock_response):
        items = extract_action_items_llm(text)
        # Should deduplicate case-insensitively
        assert len(items) == 1
        assert "Complete the report" in items


def test_extract_action_items_llm_fallback_on_error():
    """Test that LLM extraction falls back to heuristic extraction on error."""
    text = """
    - [ ] Set up database
    * implement API extract endpoint
    """.strip()

    # Mock Ollama to raise an exception
    with patch("app.services.extract.chat", side_effect=Exception("Connection error")):
        items = extract_action_items_llm(text)
        # Should fall back to heuristic extraction
        assert len(items) > 0
        assert "Set up database" in items or "implement API extract endpoint" in items


def test_extract_action_items_llm_fallback_on_empty_response():
    """Test that LLM extraction falls back when LLM returns empty content."""
    text = """
    - [ ] Set up database
    * implement API extract endpoint
    """.strip()

    # Mock Ollama to return empty content
    mock_response = {
        "message": {
            "content": ""
        }
    }

    with patch("app.services.extract.chat", return_value=mock_response):
        items = extract_action_items_llm(text)
        # Should fall back to heuristic extraction
        assert len(items) > 0


def test_extract_action_items_llm_fallback_on_invalid_json():
    """Test that LLM extraction falls back when LLM returns invalid JSON."""
    text = """
    - [ ] Set up database
    """.strip()

    # Mock Ollama to return invalid JSON
    mock_response = {
        "message": {
            "content": "This is not valid JSON"
        }
    }

    with patch("app.services.extract.chat", return_value=mock_response):
        items = extract_action_items_llm(text)
        # Should fall back to heuristic extraction
        assert len(items) > 0


def test_extract_action_items_llm_no_action_items():
    """Test LLM extraction when there are no action items in the text."""
    text = """
    This is just a regular note with no action items.
    It contains narrative text and descriptions.
    Nothing actionable here.
    """.strip()

    mock_response = {
        "message": {
            "content": json.dumps({
                "action_items": []
            })
        }
    }

    with patch("app.services.extract.chat", return_value=mock_response):
        items = extract_action_items_llm(text)
        assert items == []
