import shutil
from typing import Optional, Tuple
import os


def does_dir_exist(path: str) -> bool:
    """
    Check if the given path exists and is a directory.

    Args:
        path (str): The directory path to check.

    Returns:
        bool: True if the directory exists, False otherwise.
    """
    return os.path.isdir(path)


def remove_dir(
    path: str,
    not_exist_ok: bool = False,
    remove_content: bool = False,
    remove_parents: bool = False,
) -> Optional[str]:
    """
    Remove a directory.

    Args:
        path (str): Path to the directory to remove.
        not_exist_ok (bool): If True, do not return error if directory does not exist.
        remove_content (bool): If True, remove directory and all contents recursively (like 'rm -rf').
                               If False, only remove empty directory (error if not empty).
        remove_parents (bool): If True, also try to remove all parent directories upward, stopping at first failure.

    Returns:
        Optional[str]: None if successful, or error message string if failed.
    """
    if not does_dir_exist(path):
        if not not_exist_ok:
            return f"Directory {path} does not exist"
        return None

    try:
        if remove_content:
            shutil.rmtree(path)
        else:
            os.rmdir(path)

        if remove_parents:
            parent = os.path.dirname(os.path.abspath(path))
            while parent and parent != "/" and parent != os.path.abspath(os.sep):
                try:
                    os.rmdir(parent)
                except OSError:
                    break
                parent = os.path.dirname(parent)
    except Exception as e:
        return f"Error removing directory {path}: {e}"

    return None


def create_dir(
    path: str, exists_ok: bool, create_parent_dirs: bool = False
) -> Optional[str]:
    """
    Create a directory.

    Args:
        path (str): Path to the directory to create.
        exists_ok (bool): If True, do not return error if directory already exists.
        create_parent_dirs (bool): If True, create any missing parent directories.

    Returns:
        Optional[str]: None if successful, or error message string if failed.
    """
    if does_dir_exist(path):
        if not exists_ok:
            return f"Directory {path} already exists"
        return None

    try:
        if create_parent_dirs:
            os.makedirs(path, exist_ok=exists_ok)
        else:
            os.mkdir(path)
    except Exception as e:
        return f"Error creating directory {path}: {e}"

    return None


def is_dir_empty(path: str) -> Tuple[bool, Optional[str]]:
    """
    Check if the given directory is empty.

    Args:
        path (str): Path to the directory.

    Returns:
        Tuple[bool, Optional[str]]:
            - True and None if directory exists and is empty.
            - False and None if directory exists and is not empty.
            - False and error string if directory does not exist or is not accessible.
    """
    if not does_dir_exist(path):
        return False, f"Directory {path} does not exist"
    try:
        return len(os.listdir(path)) == 0, None
    except Exception as e:
        return False, f"Error checking directory {path}: {e}"
