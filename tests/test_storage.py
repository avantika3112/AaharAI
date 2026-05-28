import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from utils import storage


class StorageTests(unittest.TestCase):
    def test_save_and_load_user_data_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_file = Path(tmp_dir) / "user_data.json"
            payload = {"profile": {"name": "test-user"}}

            with patch.object(storage, "DATA_FILE", temp_file):
                storage.save_user_data(payload)
                loaded = storage.load_user_data()

            self.assertEqual(loaded, payload)

    def test_append_to_user_bucket_list_respects_limit(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_file = Path(tmp_dir) / "user_data.json"

            with patch.object(storage, "DATA_FILE", temp_file):
                storage.append_to_user_bucket_list("alice", "events", {"n": 1}, limit=2)
                storage.append_to_user_bucket_list("alice", "events", {"n": 2}, limit=2)
                storage.append_to_user_bucket_list("alice", "events", {"n": 3}, limit=2)

                bucket = storage.load_user_bucket("alice")

            self.assertEqual(bucket["events"], [{"n": 2}, {"n": 3}])

    def test_delete_user_bucket_removes_user_data(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_file = Path(tmp_dir) / "user_data.json"

            with patch.object(storage, "DATA_FILE", temp_file):
                storage.update_user_bucket("alice", {"profile": {"name": "Alice"}})
                storage.delete_user_bucket("alice")

                bucket = storage.load_user_bucket("alice")

            self.assertEqual(bucket, {})


if __name__ == "__main__":
    unittest.main()
