import sys
from typing import List
from dhub.const import BACKUP_POLICY, DATA_DIR, BackupPolicy
from dhub.service import Service


class Cli:
    def __init__(
        self, data_dir: str = DATA_DIR, backup_policy: BackupPolicy = BACKUP_POLICY
    ) -> None:
        self._service = Service(data_dir, backup_policy)

    def _error(self, message: str, usage: bool = False, code: int = 1) -> None:
        print(f"[ERROR] {message}", file=sys.stderr)
        if usage:
            print("", file=sys.stderr)
            print("Usage:", file=sys.stderr)
            print("\t--list\t\t\tList tables", file=sys.stderr)
            print("\t--create <table_name>\tCreate table", file=sys.stderr)
            print("\t--delete <table_name>\tDelete table", file=sys.stderr)

    def run(self, args: List[str]) -> None:
        if len(args) < 1:
            self._error("No command given", usage=True)
            return

        if args[0] == "--list":
            if len(args) > 1:
                self._error("--list takes no additional arguments.", usage=True)
                return
            self._handle_list()

        elif args[0] == "--create":
            if len(args) < 2:
                self._error("Missing table name for --create.", usage=True)
                return
            elif len(args) > 2:
                self._error(
                    "--create takes exactly one argument (the table name).", usage=True
                )
                return
            self._handle_create(args[1])

        elif args[0] == "--delete":
            if len(args) < 2:
                self._error("Missing table name for --delete.", usage=True)
                return
            elif len(args) > 2:
                self._error(
                    "--delete takes exactly one argument (the table name).", usage=True
                )
                return
            self._handle_delete(args[1])

        else:
            self._error(f"Unknown command '{args[0]}'.", usage=True)

    def _handle_list(self) -> None:
        def print_tables(tables: List[str]):
            for table in tables:
                print(f"\t- {table}")

        tables = self._service.list_tables()
        if not tables:
            print("No tables found")
        elif len(tables) == 1:
            print("Found 1 table:")
        else:
            print(f"Found {len(tables)} tables:")

        print_tables(tables)

    def _handle_create(self, table_name: str) -> None:
        err = self._service.create_table(table_name)
        if err:
            self._error(err)
        print(f"Created table '{table_name}'")

    def _handle_delete(self, table_name: str) -> None:
        err = self._service.delete_table(table_name)
        if err:
            self._error(err)
        print(f"Deleted table '{table_name}'")


def main():  # pragma: no cover
    Cli().run(sys.argv[1:])


if __name__ == "__main__":  # pragma: no cover
    main()
