import tempfile
import unittest
import io
from contextlib import redirect_stdout, redirect_stderr

from dhub.cli import Cli
from dhub.const import BackupPolicy
from dhub.utils.test import print_cli_status
from dhub.utils.dir import remove_dir, does_dir_exist


class TestCli(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="dhub_cli_test_")
        self.cli = Cli(self.temp_dir, backup_policy=BackupPolicy.NONE)

    def tearDown(self):
        if does_dir_exist(self.temp_dir):
            remove_dir(self.temp_dir, remove_content=True)

    @print_cli_status("'unknown command' prints error and usage")
    def test_cli_unknown_command(self, out: io.StringIO, err: io.StringIO):
        with redirect_stdout(out), redirect_stderr(err):
            try:
                self.cli.run(["--wewew"])
            except SystemExit as e:
                exit_code = e.code
            else:
                exit_code = 0

        self.assertIn("[ERROR] Unknown command '--wewew'.", err.getvalue())
        self.assertIn("Usage:", err.getvalue())
        self.assertNotEqual(exit_code, 0)

    @print_cli_status("No command provided prints error message and usage")
    def test_cli_no_command(self, out: io.StringIO, err: io.StringIO):
        with redirect_stdout(out), redirect_stderr(err):
            try:
                self.cli.run([])
            except SystemExit as e:
                exit_code = e.code
            else:
                exit_code = 0

        self.assertIn("[ERROR] No command given.", err.getvalue())
        self.assertNotEqual(exit_code, 0)

    @print_cli_status("'--create' with no argument prints error")
    def test_cli_create_no_arg(self, out: io.StringIO, err: io.StringIO):
        with redirect_stdout(out), redirect_stderr(err):
            try:
                self.cli.run(["--create"])
            except SystemExit as e:
                exit_code = e.code
            else:
                exit_code = 0
        self.assertIn("[ERROR] Missing table name for --create.", err.getvalue())
        self.assertNotEqual(exit_code, 0)

    @print_cli_status("'--create' with too many arguments prints error")
    def test_cli_create_too_many_args(self, out: io.StringIO, err: io.StringIO):
        with redirect_stdout(out), redirect_stderr(err):
            try:
                self.cli.run(["--create", "table1", "extra"])
            except SystemExit as e:
                exit_code = e.code
            else:
                exit_code = 0
        self.assertIn(
            "[ERROR] --create takes exactly one argument (the table name).",
            err.getvalue(),
        )
        self.assertNotEqual(exit_code, 0)

    @print_cli_status(
        "'--create' with valid table name creates table and prints success"
    )
    def test_cli_create_success(self, out: io.StringIO, err: io.StringIO):
        with redirect_stdout(out), redirect_stderr(err):
            self.cli.run(["--create", "testy"])
        output = out.getvalue()
        self.assertIn("Created table 'testy'", output)
        out2 = io.StringIO()
        with redirect_stdout(out2), redirect_stderr(io.StringIO()):
            self.cli.run(["--list"])
        self.assertIn("- testy", out2.getvalue())

    @print_cli_status("'--create' of existing table prints error")
    def test_cli_create_existing_table(self, out: io.StringIO, err: io.StringIO):
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.cli.run(["--create", "foobar"])
        with redirect_stdout(out), redirect_stderr(err):
            try:
                self.cli.run(["--create", "foobar"])
            except SystemExit as e:
                exit_code = e.code
            else:
                exit_code = 0
        error_output = err.getvalue()
        self.assertIn("already exists", error_output)
        self.assertNotEqual(exit_code, 0)

    @print_cli_status("'--list' on empty DB prints 'No tables found'")
    def test_cli_list_empty(self, out: io.StringIO, err: io.StringIO):
        with redirect_stdout(out), redirect_stderr(err):
            self.cli.run(["--list"])
        self.assertIn("No tables found", out.getvalue())

    @print_cli_status("'--list' after creating table prints table name")
    def test_cli_list_with_table(self, out: io.StringIO, err: io.StringIO):
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.cli.run(["--create", "x"])
        with redirect_stdout(out), redirect_stderr(err):
            self.cli.run(["--list"])
        output = out.getvalue()
        self.assertIn("Found 1 table:", output)
        self.assertIn("- x", output)

    @print_cli_status("'--list' with multiple tables prints all table names and count")
    def test_cli_list_multiple_tables(self, out: io.StringIO, err: io.StringIO):
        for name in ("foo", "bar"):
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.cli.run(["--create", name])
        with redirect_stdout(out), redirect_stderr(err):
            self.cli.run(["--list"])
        output = out.getvalue()
        self.assertIn("Found 2 tables:", output)
        self.assertIn("- foo", output)
        self.assertIn("- bar", output)

    @print_cli_status("'--list' with extra argument errors out")
    def test_cli_list_extra_args(self, out: io.StringIO, err: io.StringIO):
        with redirect_stdout(out), redirect_stderr(err):
            try:
                self.cli.run(["--list", "extra"])
            except SystemExit as e:
                exit_code = e.code
            else:
                exit_code = 0
        self.assertIn("[ERROR] --list takes no additional arguments.", err.getvalue())
        self.assertNotEqual(exit_code, 0)

    @print_cli_status("'--delete' with no argument prints error")
    def test_cli_delete_no_arg(self, out: io.StringIO, err: io.StringIO):
        with redirect_stdout(out), redirect_stderr(err):
            try:
                self.cli.run(["--delete"])
            except SystemExit as e:
                exit_code = e.code
            else:
                exit_code = 0
        self.assertIn("[ERROR] Missing table name for --delete.", err.getvalue())
        self.assertNotEqual(exit_code, 0)

    @print_cli_status("'--delete' with too many arguments prints error")
    def test_cli_delete_too_many_args(self, out: io.StringIO, err: io.StringIO):
        with redirect_stdout(out), redirect_stderr(err):
            try:
                self.cli.run(["--delete", "table1", "extra"])
            except SystemExit as e:
                exit_code = e.code
            else:
                exit_code = 0
        self.assertIn(
            "[ERROR] --delete takes exactly one argument (the table name).",
            err.getvalue(),
        )
        self.assertNotEqual(exit_code, 0)

    @print_cli_status("'--delete' of non-existing table prints error")
    def test_cli_delete_nonexistent(self, out: io.StringIO, err: io.StringIO):
        with redirect_stdout(out), redirect_stderr(err):
            try:
                self.cli.run(["--delete", "ghost"])
            except SystemExit as e:
                exit_code = e.code
            else:
                exit_code = 0
        self.assertIn("does not exist", err.getvalue())
        self.assertNotEqual(exit_code, 0)

    @print_cli_status("'--delete' after create deletes table")
    def test_cli_delete_success(self, out: io.StringIO, err: io.StringIO):
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.cli.run(["--create", "to_del"])
        out_check = io.StringIO()
        with redirect_stdout(out_check), redirect_stderr(io.StringIO()):
            self.cli.run(["--list"])
        self.assertIn("- to_del", out_check.getvalue())
        with redirect_stdout(out), redirect_stderr(err):
            self.cli.run(["--delete", "to_del"])
        output = out.getvalue()
        self.assertIn("Deleted table 'to_del'", output)
        out_check2 = io.StringIO()
        with redirect_stdout(out_check2), redirect_stderr(io.StringIO()):
            self.cli.run(["--list"])
        self.assertNotIn("- to_del", out_check2.getvalue())


if __name__ == "__main__":
    unittest.main()
