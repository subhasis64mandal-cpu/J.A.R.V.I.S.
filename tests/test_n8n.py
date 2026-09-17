import os
import unittest
from unittest.mock import patch

from jarvis.n8n import N8nConfig, N8nUnavailable, N8nWorkflowClient, load_config


class N8nBridgeTests(unittest.TestCase):
    def test_bridge_is_disabled_without_endpoint(self) -> None:
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("JARVIS_N8N_WEBHOOK_URL", None)
            self.assertFalse(load_config().enabled)
            self.assertIn("disabled", N8nWorkflowClient().status().lower())

    def test_https_endpoint_is_allowed(self) -> None:
        config = N8nConfig("https://example.com/webhook/jarvis")
        self.assertTrue(config.enabled)

    def test_remote_plain_http_is_rejected(self) -> None:
        with self.assertRaises(N8nUnavailable):
            from jarvis.n8n import _validate_endpoint
            _validate_endpoint("http://example.com/webhook/jarvis")

    def test_loopback_http_is_allowed(self) -> None:
        from jarvis.n8n import _validate_endpoint
        self.assertEqual(
            _validate_endpoint("http://127.0.0.1:5678/webhook/jarvis"),
            "http://127.0.0.1:5678/webhook/jarvis",
        )

    def test_timeout_is_clamped(self) -> None:
        with patch.dict(os.environ, {"JARVIS_N8N_WEBHOOK_URL": "https://example.com/hook", "JARVIS_N8N_TIMEOUT_SECONDS": "999"}, clear=False):
            self.assertEqual(load_config().timeout_seconds, 60)


if __name__ == "__main__":
    unittest.main()
