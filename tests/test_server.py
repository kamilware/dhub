import unittest
import tempfile
import json

from dhub.server import Server
from dhub.utils.dir import does_dir_exist, remove_dir
from dhub.utils.test import print_server_status
from dhub.const import BackupPolicy


class TestServer(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="dhub_server_test_")
        self.server_obj = Server(self.temp_dir, backup_policy=BackupPolicy.NONE)
        self.client = self.server_obj.server.test_client()

    def tearDown(self):
        if does_dir_exist(self.temp_dir):
            remove_dir(self.temp_dir, remove_content=True)

    @print_server_status("insert: valid record returns 201 and status ok")
    def test_insert_success(self):
        self.server_obj.service.create_table("working")
        record = {"abc": 123}
        rv = self.client.post(
            "/working", data=json.dumps(record), content_type="application/json"
        )
        self.assertEqual(rv.status_code, 201)
        self.assertEqual(rv.get_json().get("status"), "ok")

    @print_server_status("insert: nonexistent table returns 400 and error")
    def test_insert_nonexistent_table(self):
        record = {"abc": 123}
        rv = self.client.post(
            "/ghost", data=json.dumps(record), content_type="application/json"
        )
        self.assertEqual(rv.status_code, 400)
        self.assertIn("does not exist", rv.get_json().get("error"))

    @print_server_status("insert: non-JSON request returns 400 and error")
    def test_insert_not_json(self):
        rv = self.client.post(
            "/whatever", data="not json at all", content_type="text/plain"
        )
        self.assertEqual(rv.status_code, 400)
        self.assertIn("Request must be JSON", rv.get_json().get("error"))

    @print_server_status("insert: JSON not dict returns 400 and error")
    def test_insert_not_dict(self):
        self.server_obj.service.create_table("nodict")
        rv = self.client.post(
            "/nodict", data=json.dumps([1, 2, 3]), content_type="application/json"
        )
        self.assertEqual(rv.status_code, 400)
        self.assertIn("Record must be a JSON object", rv.get_json().get("error"))

    @print_server_status("insert: service insert error returns 400 and error string")
    def test_insert_service_error(self):
        self.server_obj.service.create_table("table")
        # monkey patch
        orig_insert = self.server_obj.service.insert

        self.server_obj.service.insert = lambda *a, **kw: "fail-test"  # type: ignore
        record = {"yo": "ho"}
        rv = self.client.post(
            "/table", data=json.dumps(record), content_type="application/json"
        )
        self.assertEqual(rv.status_code, 400)
        self.assertIn("fail-test", rv.get_json().get("error"))

        # revert monkey patch
        self.server_obj.service.insert = orig_insert

    @print_server_status("get: returns all records for table, 200")
    def test_get_all_records(self):
        self.server_obj.service.create_table("mytable")
        self.server_obj.service.insert("mytable", {"a": 1})
        self.server_obj.service.insert("mytable", {"b": 2})
        rv = self.client.get("/mytable")
        self.assertEqual(rv.status_code, 200)
        data = rv.get_json()
        self.assertIn("records", data)
        self.assertEqual(len(data["records"]), 2)
        self.assertIn({"a": 1}, data["records"])
        self.assertIn({"b": 2}, data["records"])

    @print_server_status("get: empty table returns empty list, 200")
    def test_get_empty_table(self):
        self.server_obj.service.create_table("emptytable")
        rv = self.client.get("/emptytable")
        self.assertEqual(rv.status_code, 200)
        data = rv.get_json()
        self.assertIn("records", data)
        self.assertEqual(data["records"], [])

    @print_server_status("get: non-existent table returns 400 and error")
    def test_get_nonexistent_table(self):
        rv = self.client.get("/ghosttable")
        self.assertEqual(rv.status_code, 400)
        data = rv.get_json()
        self.assertIn("error", data)
        self.assertIn("does not exist", data["error"])

    @print_server_status("get: key param returns matching records, 200")
    def test_get_with_key_matches(self):
        self.server_obj.service.create_table("cars")
        self.server_obj.service.insert("cars", {"brand": "lada", "hp": 50})
        self.server_obj.service.insert("cars", {"brand": "bmw", "hp": 300})
        self.server_obj.service.insert("cars", {"foo": "bar"})
        rv = self.client.get("/cars?key=brand")
        self.assertEqual(rv.status_code, 200)
        records = rv.get_json().get("records", [])
        self.assertEqual(len(records), 2)
        for rec in records:
            self.assertIn("brand", rec)

    @print_server_status("get: key param matches no records returns empty list")
    def test_get_with_key_no_match(self):
        self.server_obj.service.create_table("emptykey")
        self.server_obj.service.insert("emptykey", {"x": 1})
        rv = self.client.get("/emptykey?key=never")
        self.assertEqual(rv.status_code, 200)
        records = rv.get_json().get("records", [])
        self.assertEqual(records, [])

    @print_server_status("get: key param on empty table returns empty list")
    def test_get_with_key_empty_table(self):
        self.server_obj.service.create_table("totallyempty")
        rv = self.client.get("/totallyempty?key=whatever")
        self.assertEqual(rv.status_code, 200)
        records = rv.get_json().get("records", [])
        self.assertEqual(records, [])

    @print_server_status("get: key param on non-existent table returns 400 error")
    def test_get_with_key_nonexistent_table(self):
        rv = self.client.get("/nothere?key=foo")
        self.assertEqual(rv.status_code, 400)
        self.assertIn("error", rv.get_json())


if __name__ == "__main__":
    unittest.main()
