"""
Utility functions for handling file paths, MIME types, and API parameter parsing.
"""

import mimetypes
import os


def get_mime_type(image_path: str) -> str:
    """
    Get the MIME type of a file based on its path.

    Parameters
    ----------
    image_path : str
        The path to the file.

    Returns
    -------
    str
        The MIME type of the file, or None if it cannot be determined.
    """
    mime_type, _ = mimetypes.guess_type(image_path)
    return mime_type

def normalize_path(path: str) -> str:
    """
    Normalize a file path to a relative path from the current working directory.

    Parameters
    ----------
    path : str
        The file path to normalize.

    Returns
    -------
    str
        The normalized relative file path.
    """
    return os.path.relpath(
        os.path.normpath(os.path.abspath(os.path.realpath(os.path.expanduser(path)))),
        os.getcwd(),
    )
