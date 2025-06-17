import enum


class BackupPolicy(enum.Enum):
    NONE = "NONE"
    ON_UPDATE = "ON_UPDATE"


DATA_DIR = "data"
DATA_FILE_EXT = "ndjson"
BACKUP_POLICY = BackupPolicy.ON_UPDATE
