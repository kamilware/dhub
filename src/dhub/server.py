from flask import Flask, request, jsonify
from dhub.const import DATA_DIR, BackupPolicy
from dhub.service import Service
import sys


class Server:
    def __init__(self, data_dir: str, backup_policy: BackupPolicy):
        self.data_dir = data_dir
        self.service = Service(self.data_dir, backup_policy)
        self.server = Flask(__name__)
        self._register_routes()

    def _register_routes(self):
        @self.server.route("/<table>", methods=["POST"])
        def insert_record(table: str):  # type: ignore
            if not request.is_json:
                return jsonify({"error": "Request must be JSON"}), 400

            record = request.get_json()
            if not isinstance(record, dict):
                return jsonify({"error": "Record must be a JSON object"}), 400

            err = self.service.insert(table, record)  # type: ignore
            if err:
                return jsonify({"error": err}), 400

            return jsonify({"status": "ok"}), 201

        @self.server.route("/<table>", methods=["GET"])
        def get_records(table: str):  # type: ignore
            key = request.args.get("key")
            if key:
                records, err = self.service.find_by_key(table, key)
            else:
                records, err = self.service.find_all(table)

            if err:
                return jsonify({"error": err}), 400
            return jsonify({"records": records}), 200

    def run(self):  # pragma: no cover
        port = 8000
        debug = False

        args = sys.argv[1:]
        if "--debug" in args:
            debug = True

        if "--port" in args:
            idx = args.index("--port")
            if idx + 1 >= len(args):
                print(
                    "Error: --port needs to be followed by an int, example --port 4567"
                )
                sys.exit(1)
            try:
                port = int(args[idx + 1])
            except ValueError:
                print(
                    "Error: --port needs to be followed by an int, example --port 4567"
                )
                sys.exit(1)

        self.server.run(host="0.0.0.0", port=port, debug=debug)


if __name__ == "__main__":  # pragma: no cover
    Server(DATA_DIR, BackupPolicy.ON_UPDATE).run()
