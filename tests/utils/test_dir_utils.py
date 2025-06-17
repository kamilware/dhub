import os
import shutil
import tempfile
import unittest

from dhub.utils.dir import (
    create_dir,
    remove_dir,
    does_dir_exist,
    is_dir_empty,
)


class TestDirUtils(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="dhub_dir_test_")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_create_dir(self):
        dir_path = os.path.join(self.test_dir, "newdir")
        err = create_dir(dir_path, exists_ok=False)
        self.assertIsNone(err)
        self.assertTrue(os.path.isdir(dir_path))

    def test_create_existing_dir(self):
        dir_path = os.path.join(self.test_dir, "existdir")
        os.mkdir(dir_path)
        err = create_dir(dir_path, exists_ok=False)
        self.assertIsInstance(err, str)
        err2 = create_dir(dir_path, exists_ok=True)
        self.assertIsNone(err2)

    def test_create_dir_with_parents(self):
        deep_path = os.path.join(self.test_dir, "a/b/c/d")
        err = create_dir(deep_path, exists_ok=False, create_parent_dirs=True)
        self.assertIsNone(err)
        self.assertTrue(os.path.isdir(deep_path))

    def test_remove_dir_empty(self):
        dir_path = os.path.join(self.test_dir, "to_remove")
        os.mkdir(dir_path)
        err = remove_dir(dir_path)
        self.assertIsNone(err)
        self.assertFalse(os.path.exists(dir_path))

    def test_remove_dir_non_empty(self):
        dir_path = os.path.join(self.test_dir, "non_empty")
        os.makedirs(dir_path)
        with open(os.path.join(dir_path, "file.txt"), "w") as f:
            f.write("w!")
        err = remove_dir(dir_path, remove_content=True)
        self.assertIsNone(err)
        self.assertFalse(os.path.exists(dir_path))

    def test_remove_dir_not_exist(self):
        dir_path = os.path.join(self.test_dir, "does_not_exist")
        err = remove_dir(dir_path)
        self.assertIsInstance(err, str)
        err2 = remove_dir(dir_path, not_exist_ok=True)
        self.assertIsNone(err2)

    def test_does_dir_exist(self):
        dir_path = os.path.join(self.test_dir, "exists")
        os.mkdir(dir_path)
        self.assertTrue(does_dir_exist(dir_path))
        fake_path = os.path.join(self.test_dir, "no_such_dir")
        self.assertFalse(does_dir_exist(fake_path))

    def test_is_dir_empty(self):
        dir_path = os.path.join(self.test_dir, "empty")
        os.mkdir(dir_path)
        result, err = is_dir_empty(dir_path)
        self.assertTrue(result)
        self.assertIsNone(err)
        with open(os.path.join(dir_path, "file.txt"), "w") as f:
            f.write("x!")
        result2, err2 = is_dir_empty(dir_path)
        self.assertFalse(result2)
        self.assertIsNone(err2)

    def test_is_dir_empty_not_exist(self):
        dir_path = os.path.join(self.test_dir, "gone")
        result, err = is_dir_empty(dir_path)
        self.assertFalse(result)
        self.assertIsInstance(err, str)


if __name__ == "__main__":
    unittest.main()
