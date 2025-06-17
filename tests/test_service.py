import os
import tempfile
from typing import Any, Dict
import unittest

from dhub.const import BackupPolicy
from dhub.utils.dir import is_dir_empty
from dhub.service import Service, DATA_FILE_EXT


class TestService(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="dhub_service_test_")
        self.service = Service(self.temp_dir, backup_policy=BackupPolicy.NONE)

    def tearDown(self):
        pass

    def test_create_and_list_tables(self):
        self.assertEqual(self.service.list_tables(), [])
        err = self.service.create_table("testtable")
        self.assertIsNone(err)
        self.assertIn("testtable", self.service.list_tables())

    def test_double_create_table(self):
        self.service.create_table("dup")
        err = self.service.create_table("dup")
        self.assertIsInstance(err, str)
        self.assertEqual(f"Table 'dup' already exists", err)

    def test_insert_and_find_all(self):
        self.service.create_table("users")
        record: Dict[str, Any] = {"name": "Ivan", "age": 33}
        err = self.service.insert("users", record)
        self.assertIsNone(err)
        records, err2 = self.service.find_all("users")
        self.assertIsNone(err2)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0], record)

    def test_insert_without_table(self):
        err = self.service.insert("ghost", {"foo": "bar"})
        self.assertIsInstance(err, str)
        self.assertEqual(f"Table 'ghost' does not exist", err)

    def test_find_by_key(self):
        self.service.create_table("heroes")
        self.service.insert("heroes", {"name": "Alyosha", "hero": True})
        self.service.insert("heroes", {"name": "Vasya"})
        found, err = self.service.find_by_key("heroes", "hero")
        self.assertIsNone(err)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["name"], "Alyosha")

        found2, err2 = self.service.find_by_key("heroes", "missingkey")
        self.assertIsNone(err2)
        self.assertEqual(len(found2), 0)

    def test_find_all_table_not_exist(self):
        records, err = self.service.find_all("noway")
        self.assertIsInstance(err, str)
        self.assertEqual(records, [])

    def test_delete_table(self):
        self.service.create_table("dtable")
        self.service.insert("dtable", {"d": 1})
        err = self.service.delete_table("dtable")
        self.assertIsNone(err)
        self.assertNotIn("dtable", self.service.list_tables())
        table_file = f"{self.temp_dir}/dtable.{DATA_FILE_EXT}"
        self.assertFalse(os.path.exists(table_file))
        empty, _ = is_dir_empty(self.temp_dir)
        self.assertTrue(empty or not os.path.exists(self.temp_dir))


if __name__ == "__main__":
    unittest.main()
