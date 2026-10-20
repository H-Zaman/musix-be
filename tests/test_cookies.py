from app.services import ytdlp_service

VALID = "# Netscape HTTP Cookie File\n.example.com\tTRUE\t/\tTRUE\t1823399804\tname\tabc\n"
# generate_cookies.py once wrote literal "\t" instead of tab characters.
BROKEN = "# Netscape HTTP Cookie File\n.example.com\\tTRUE\\t/\\tTRUE\\t1823399804\\tname\\tabc\n"


def _use(monkeypatch, tmp_path, content):
    path = tmp_path / "cookies.txt"
    if content is not None:
        path.write_text(content)
    monkeypatch.setattr(ytdlp_service, "COOKIES_PATH", str(path))
    return str(path)


def test_valid_cookie_file_is_passed(monkeypatch, tmp_path):
    path = _use(monkeypatch, tmp_path, VALID)
    assert ytdlp_service._cookie_args() == ["--cookies", path]


def test_malformed_cookie_file_is_ignored(monkeypatch, tmp_path):
    _use(monkeypatch, tmp_path, BROKEN)
    assert ytdlp_service._cookie_args() == []


def test_missing_cookie_file_is_ignored(monkeypatch, tmp_path):
    _use(monkeypatch, tmp_path, None)
    assert ytdlp_service._cookie_args() == []
