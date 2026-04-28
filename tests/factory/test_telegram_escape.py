from factory.control.telegram_escape import escape_markdown_v2


def test_escape_markdown_v2_reserved_chars():
    raw = "file_path/a-b.py status=OK!"
    escaped = escape_markdown_v2(raw)
    assert "file\\_path/a\\-b\\.py" in escaped
    assert "status\\=OK\\!" in escaped


def test_escape_markdown_v2_plain_text():
    assert escape_markdown_v2("abc") == "abc"
