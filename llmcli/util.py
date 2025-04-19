import mimetypes
import os


def get_mime_type(image_path: str) -> str:
    mime_type, _ = mimetypes.guess_type(image_path)
    return mime_type


def parse_api_params(params: list[str]) -> dict:
    if params is None:
        return {}

    return {
        k: v for [k, v] in
        [
            [s.strip() for s in param.split("=", maxsplit=1)]
            for param in params
            if "=" in param
        ]
    }

def normalize_path(path: str) -> str:
    return os.path.relpath(
        os.path.normpath(os.path.abspath(os.path.realpath(os.path.expanduser(path)))),
        os.getcwd(),
    )
