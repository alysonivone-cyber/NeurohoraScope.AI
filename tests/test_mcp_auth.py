"""Tests du verificateur Bearer de NeurohoraScope.AI."""

import asyncio
import os
import unittest
from unittest.mock import patch

from src.mcp.auth import NeurohoraTokenVerifier


class TestMCPAuthentication(unittest.TestCase):

    def setUp(self):
        self.token = "test-token-" + "a" * 40
        self.environment = patch.dict(
            os.environ,
            {
                "MCP_ACCESS_TOKEN": self.token,
                "MCP_PUBLIC_URL": "https://example.com/mcp",
            },
        )
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.verifier = NeurohoraTokenVerifier()

    def test_valid_token(self):
        result = asyncio.run(
            self.verifier.verify_token(self.token)
        )
        self.assertIsNotNone(result)
        self.assertIn("mcp:tools", result.scopes)

    def test_invalid_token(self):
        result = asyncio.run(
            self.verifier.verify_token("incorrect-token")
        )
        self.assertIsNone(result)

    def test_missing_token(self):
        result = asyncio.run(
            self.verifier.verify_token("")
        )
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
