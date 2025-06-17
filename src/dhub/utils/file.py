from typing import Optional
import os


def does_file_exist(path: str) -> bool:
    """
    Check if the given path exists and is a file.

    Args:
        path (str): The file path to check.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    return os.path.isfile(path)


def remove_file(path: str, not_exist_ok: bool = False) -> Optional[str]:
    """
    Remove a file.

    Args:
        path (str): The path to the file to remove.
        not_exist_ok (bool): If True, do not return error if file does not exist.

    Returns:
        Optional[str]: None if successful, or error message string if failed.
    """
    if not does_file_exist(path):
        if not not_exist_ok:
            return f"File {path} does not exist"
        return None

    try:
        os.remove(path)
    except Exception as e:
        return f"Error removing file {path}: {e}"

    return None


def create_file(path: str, exists_ok: bool = False) -> Optional[str]:
    """
    Create a new empty file.

    Args:
        path (str): The file path to create.
        exists_ok (bool): If True, do not return error if file already exists.

    Returns:
        Optional[str]: None if successful, or error message string if failed.
    """
    if does_file_exist(path):
        if not exists_ok:
            return f"File {path} already exists"
        return None

    try:
        with open(path, "w") as _:
            pass
    except Exception as e:
        return f"Error creating file {path}: {e}"

    return None
