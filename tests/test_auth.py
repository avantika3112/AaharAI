import unittest
from unittest.mock import patch

from utils import auth


class AuthTests(unittest.TestCase):
    def test_normalize_username(self):
        self.assertEqual(auth._normalize_username("  UserOne  "), "userone")

    def test_is_admin_user_from_env(self):
        with patch.dict("os.environ", {"AAHARAI_ADMIN_USERS": "admin, manager"}, clear=False):
            self.assertTrue(auth.is_admin_user("ADMIN"))
            self.assertTrue(auth.is_admin_user("manager"))
            self.assertFalse(auth.is_admin_user("visitor"))

    def test_get_audit_logs_with_limit(self):
        data = {"audit_logs": [{"id": 1}, {"id": 2}, {"id": 3}]}
        with patch("utils.auth.load_user_data", return_value=data):
            self.assertEqual(auth.get_audit_logs(limit=2), [{"id": 2}, {"id": 3}])
            self.assertEqual(auth.get_audit_logs(limit=0), [{"id": 1}, {"id": 2}, {"id": 3}])

    def test_get_audit_log_stats(self):
        data = {
            "audit_logs": [{"id": 1}, {"id": 2}],
            "audit_logs_archive": [{"id": 10}],
        }
        with patch("utils.auth.load_user_data", return_value=data):
            stats = auth.get_audit_log_stats()

        self.assertEqual(stats["active"], 2)
        self.assertEqual(stats["archived"], 1)


if __name__ == "__main__":
    unittest.main()
