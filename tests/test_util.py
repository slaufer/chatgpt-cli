from llmcli.util import get_mime_type, normalize_path
from unittest import mock


def test_get_mime_type():
    assert get_mime_type("image.png") == "image/png"
    assert get_mime_type("file.txt") == "text/plain"
    assert get_mime_type("") == None

def test_normalize_path():
    # this test will probably fail on windows
    with mock.patch("llmcli.util.os.getcwd", return_value="/home/user"):
        assert normalize_path("/home/user/file.txt") == "file.txt"
        assert normalize_path("/home/user/files/file.txt") == "files/file.txt"
        assert normalize_path("/file.txt") == "../../file.txt"
        assert normalize_path("./file.txt") == "file.txt"
        assert normalize_path("../file.txt") == "../file.txt"
