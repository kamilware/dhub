import json
import os
from typing import Any, Dict, List, Optional, Tuple
from dhub.backup import backup
from dhub.const import BackupPolicy
from dhub.utils.dir import create_dir, is_dir_empty, remove_dir, does_dir_exist
from dhub.utils.file import create_file, does_file_exist, remove_file
from dhub.const import DATA_FILE_EXT


class Service:
    def __init__(self, data_dir: str, backup_policy: BackupPolicy):
        """
        Map of table : table_file
        """
        self._data_dir = data_dir
        self._table_files: Dict[str, str] = {}
        self._backup_policy = backup_policy

        self._load_table_files()

    def _load_table_files(self):
        if not does_dir_exist(self._data_dir):
            return

        for f in os.listdir(self._data_dir):
            if f.endswith(DATA_FILE_EXT):
                self._table_files[f.removesuffix(f".{DATA_FILE_EXT}")] = (
                    f"{self._data_dir}/{f}"
                )

    def _get_table_file(self, table: str) -> str:
        if table not in self._table_files:
            self._table_files[table] = f"{self._data_dir}/{table}.{DATA_FILE_EXT}"

        return self._table_files[table]

    def create_table(self, name: str) -> Optional[str]:
        """
        Create a new table by creating its data file.

        Args:
            name (str): The table name. Will be used as the filename (name.ndjson).

        Returns:
            Optional[str]: None if successful, or error message string if failed.
        """
        table_file = self._get_table_file(name)

        if does_file_exist(table_file):
            return f"Table '{name}' already exists"

        err = create_dir(self._data_dir, exists_ok=True, create_parent_dirs=True)
        if err:
            return f"Error creating table '{name}': {err}"

        err = create_file(table_file)
        if err:
            return f"Error creating table '{name}': {str(err)}"

        if self._backup_policy == BackupPolicy.ON_UPDATE:
            backup()

        return None

    def delete_table(self, name: str) -> Optional[str]:
        """
        Delete a table by removing its data file.

        Args:
            name (str): The table name.

        Returns:
            Optional[str]: None if successful, or an error message string if failed.
        """
        table_file = self._get_table_file(name)

        if not does_file_exist(table_file):
            return f"Table '{name}' does not exist"

        err = remove_file(table_file)
        if err:
            return f"Error deleting table '{name}': {err}"

        is_empty, _ = is_dir_empty(self._data_dir)
        if is_empty:
            remove_dir(self._data_dir, remove_parents=True)

        del self._table_files[name]

        if self._backup_policy == BackupPolicy.ON_UPDATE:
            backup()

        return None

    def list_tables(self) -> List[str]:
        """
        List all tables in the data directory by scanning for NDJSON files.

        Scans the data directory on disk for files ending with ".ndjson"
        and returns their names (without the file extension) as the list of tables.

        Returns:
            List[str]: List of table names (without file extension).
                    Returns an empty list if directory missing or no tables found.
        """
        if not does_dir_exist(self._data_dir):
            return []

        tables: List[str] = []
        for fname in os.listdir(self._data_dir):
            if fname.endswith("." + DATA_FILE_EXT):
                tables.append(fname[: -len("." + DATA_FILE_EXT)])
        return tables

    def find_all(self, name: str) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Retrieve all records from the given table.

        Args:
            name (str): The table name.

        Returns:
            Tuple[List[Dict[str, Any]], Optional[str]]:
                - ([records...], None) if successful,
                - ([]], error message string) if table missing or error occurs.
        """
        table_file = self._get_table_file(name)

        if not does_file_exist(table_file):
            return [], f"Table '{name}' does not exist"

        records: List[Dict[str, Any]] = []
        try:
            # todo: parse to utils.file.read_ndjson
            with open(table_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            return [], f"Error reading table '{name}': {str(e)}"

        return records, None

    def insert(self, name: str, record: Dict[str, Any]) -> Optional[str]:
        """
        Insert a single record into the specified table.

        Args:
            name (str): The table name.
            record (Dict[str, Any]): The record to insert.

        Returns:
            Optional[str]: None if successful, or error message string if failed.
        """
        table_file = self._get_table_file(name)

        if not does_file_exist(table_file):
            return f"Table '{name}' does not exist"

        try:
            with open(table_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception as e:
            return f"Error inserting into table '{name}': {e}"

        if self._backup_policy == BackupPolicy.ON_UPDATE:
            backup()

        return None

    def find_by_key(
        self, name: str, key: str
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Retrieve all records from the table where the given key exists.

        Args:
            name (str): The table name.
            key (str): The key to look for.

        Returns:
            Tuple[List[Dict[str, Any]], Optional[str]]:
                - ([records...], None) if successful,
                - ([]], error message string) if table missing or error occurs.
        """
        records, err = self.find_all(name)
        if err:
            return [], f"Error reading table '{name}': {str(err)}"

        found = [record for record in records if key in record]

        return found, None
