from app.services import ytdlp_service

VALID = "# Netscape HTTP Cookie File\n.example.com\tTRUE\t/\tTRUE\t1823399804\tname\tabc\n"
# generate_cookies.py once wrote literal "\t" instead of tab characters.
BROKEN = "# Netscape HTTP Cookie File\n.example.com\\tTRUE\\t/\\tTRUE\\t1823399804\\tname\\tabc\n"


def _use(monkeypatch, tmp_path, content):
    path = tmp_path / "cookies.txt"
    if content is not None:
        path.write_text(content)
    monkeypatch.setattr(ytdlp_service, "COOKIES_PATH", str(path))
    monkeypatch.setattr(ytdlp_service, "COOKIES_RUNTIME_PATH", str(tmp_path / "runtime.txt"))
    return str(path)


def test_valid_cookie_file_is_passed_as_writable_copy(monkeypatch, tmp_path):
    path = _use(monkeypatch, tmp_path, VALID)
    runtime = str(tmp_path / "runtime.txt")
    assert ytdlp_service._cookie_args() == ["--cookies", runtime]
    assert open(runtime).read() == VALID
    assert runtime != path  # the (possibly read-only) source is never handed to yt-dlp


def test_malformed_cookie_file_is_ignored(monkeypatch, tmp_path):
    _use(monkeypatch, tmp_path, BROKEN)
    assert ytdlp_service._cookie_args() == []


def test_missing_cookie_file_is_ignored(monkeypatch, tmp_path):
    _use(monkeypatch, tmp_path, None)
    assert ytdlp_service._cookie_args() == []
