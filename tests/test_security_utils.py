import json
import tempfile
import unittest
from pathlib import Path

from security_utils import (
    SecurityConfig,
    build_signed_qr_payload,
    load_security_config,
    sanitize_csv_cell,
    verify_login,
    verify_signed_qr_payload,
)


class SecurityUtilsTests(unittest.TestCase):
    def test_login_requires_exact_credentials(self):
        config = SecurityConfig("secure_admin", "StrongPassword407915", "k" * 32)
        self.assertTrue(verify_login(config, "secure_admin", "StrongPassword407915"))
        self.assertFalse(verify_login(config, "secure_admin", "wrong-password"))

    def test_csv_formula_prefix_is_neutralized(self):
        self.assertEqual(sanitize_csv_cell("=SUM(1,1)"), "'=SUM(1,1)")
        self.assertEqual(sanitize_csv_cell("Normal value"), "Normal value")

    def test_signed_qr_rejects_tampering(self):
        key = "a-unique-test-signing-key-that-is-long-enough"
        payload = build_signed_qr_payload("emp_test", "2026-08-05T00:00:00+00:00", key)
        self.assertTrue(verify_signed_qr_payload(payload, key))
        data = json.loads(payload)
        data["employee_id"] = "emp_tampered"
        self.assertFalse(verify_signed_qr_payload(json.dumps(data), key))

    def test_credentials_file_has_no_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing.txt"
            with self.assertRaises(RuntimeError):
                load_security_config(missing, environment={})


if __name__ == "__main__":
    unittest.main()
