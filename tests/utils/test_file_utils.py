import os
import tempfile
import unittest

from dhub.utils.file import (
    create_file,
    remove_file,
    does_file_exist,
)


class TestFileUtils(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="dhub_file_test_")

    def tearDown(self):
        for fname in os.listdir(self.test_dir):
            try:
                os.remove(os.path.join(self.test_dir, fname))
            except Exception:
                pass
        try:
            os.rmdir(self.test_dir)
        except Exception:
            pass

    def test_create_file(self):
        file_path = os.path.join(self.test_dir, "test.txt")
        err = create_file(file_path, exists_ok=False)
        self.assertIsNone(err)
        self.assertTrue(os.path.isfile(file_path))

    def test_create_existing_file(self):
        file_path = os.path.join(self.test_dir, "test_exists.txt")
        with open(file_path, "w") as f:
            f.write("privet")
        err = create_file(file_path, exists_ok=False)
        self.assertIsInstance(err, str)
        err2 = create_file(file_path, exists_ok=True)
        self.assertIsNone(err2)

    def test_does_file_exist(self):
        file_path = os.path.join(self.test_dir, "exist.txt")
        self.assertFalse(does_file_exist(file_path))
        with open(file_path, "w") as f:
            f.write("1")
        self.assertTrue(does_file_exist(file_path))

    def test_remove_file(self):
        file_path = os.path.join(self.test_dir, "del.txt")
        with open(file_path, "w") as f:
            f.write("2")
        err = remove_file(file_path)
        self.assertIsNone(err)
        self.assertFalse(os.path.exists(file_path))

    def test_remove_file_not_exist(self):
        file_path = os.path.join(self.test_dir, "ghost.txt")
        err = remove_file(file_path)
        self.assertIsInstance(err, str)
        err2 = remove_file(file_path, not_exist_ok=True)
        self.assertIsNone(err2)


if __name__ == "__main__":
    unittest.main()
