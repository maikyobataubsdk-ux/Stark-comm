import asyncio
import os
import shutil
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import app

class TestLogUI(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp_dir, "test_store.json")
        self.store = app.Store(self.db_path)
        app.STORES[12345] = self.store

    def tearDown(self):
        app.STORES.pop(12345, None)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    async def test_ensure_defaults_and_set_cfg_log_channel(self):
        await app.ensure_defaults(self.store)
        cfg = app.cfg(self.store)
        self.assertIn("log_channel", cfg)
        self.assertEqual(cfg["log_channel"], 0)

        await app.set_cfg(self.store, log_channel=-1001234567890)
        updated_cfg = app.cfg(self.store)
        self.assertEqual(updated_cfg["log_channel"], -1001234567890)

    async def test_show_log_panel(self):
        await app.ensure_defaults(self.store)
        await app.set_cfg(self.store, log_channel=-1001234567890)

        client = MagicMock()
        client.store = self.store
        client.send_message = AsyncMock()

        await app.show_log_panel(client, 999)
        client.send_message.assert_called_once()
        args, kwargs = client.send_message.call_args
        self.assertEqual(args[0], 999)
        self.assertIn("-1001234567890", args[1])

    async def test_cb_log_disable(self):
        await app.ensure_defaults(self.store)
        await app.set_cfg(self.store, log_channel=-1001234567890)

        client = MagicMock()
        client.store = self.store
        client.send_message = AsyncMock()

        query = MagicMock()
        query.from_user.id = 7524032836  # Supreme ID
        query.message = MagicMock()
        query.message.edit_text = AsyncMock()
        query.answer = AsyncMock()

        await app.cb_log(client, query, ["log", "off"])
        cfg = app.cfg(self.store)
        self.assertEqual(cfg["log_channel"], 0)

    async def test_save_episode_logs_event(self):
        await app.ensure_defaults(self.store)
        await app.set_cfg(self.store, log_channel=-1001234567890)

        client = MagicMock()
        client.store = self.store
        client.bot_id = 12345
        client.username = "testbot"
        client.send_message = AsyncMock()

        await app.get_or_create_anime(self.store, "Naruto")
        await app.save_episode(client, 111, "naruto", 1, 1, "fid_123", "video", "Test Caption", None)

        client.send_message.assert_called()
        # Verify log message was sent to log_channel
        log_calls = [call for call in client.send_message.call_args_list if call[0][0] == -1001234567890]
        self.assertTrue(len(log_calls) > 0)
        self.assertIn("Naruto", log_calls[0][0][1])

if __name__ == "__main__":
    unittest.main()
