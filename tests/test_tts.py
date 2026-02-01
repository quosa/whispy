"""Tests for TTS text cleaning."""

from whispy.tts import clean_for_speech


def test_strips_emojis():
    assert clean_for_speech("Hello! 😊🌟") == "Hello!"


def test_numbered_list_gets_periods():
    text = "Here are some facts:\n1. The sky is blue\n2. Grass is green\n3. Water is wet"
    result = clean_for_speech(text)
    # Numbers removed, items separated by periods
    assert "1." not in result
    assert "The sky is blue." in result
    assert "Grass is green." in result


def test_bullet_list_gets_periods():
    text = "Things to remember:\n- Brush your teeth\n- Do your homework\n- Be kind"
    result = clean_for_speech(text)
    assert "- " not in result
    assert "Brush your teeth." in result
    assert "Do your homework." in result


def test_markdown_bold_removed():
    assert clean_for_speech("This is **important** stuff") == "This is important stuff"


def test_markdown_italic_removed():
    assert clean_for_speech("This is *really* cool") == "This is really cool"


def test_markdown_headers_removed():
    text = "### My Header\nSome content"
    result = clean_for_speech(text)
    assert "###" not in result
    assert "My Header" in result


def test_no_double_periods():
    text = "Already has punctuation.\n- Item one.\n- Item two."
    result = clean_for_speech(text)
    assert ".." not in result


def test_empty_and_whitespace():
    assert clean_for_speech("") == ""
    assert clean_for_speech("   ") == ""
    assert clean_for_speech("  hello  ") == "hello"


def test_preserves_normal_text():
    text = "Two plus two equals four. That's like having two apples and getting two more."
    assert clean_for_speech(text) == text
