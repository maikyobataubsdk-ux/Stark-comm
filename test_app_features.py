import asyncio
import os
import shutil
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import app

class TestAppFeatures(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.factory_db_path = os.path.join(self.tmp_dir, "factory.json")
        self.clone_db_path = os.path.join(self.tmp_dir, "clone_1001.json")

        app.DB_DIR = self.tmp_dir
        app.FACTORY = app.Store(self.factory_db_path)
        self.store = app.Store(self.clone_db_path)
        app.STORES[1001] = self.store

    def tearDown(self):
        app.STORES.pop(1001, None)
        app.SESSIONS.clear()
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    async def test_save_episode_qualities(self):
        await app.get_or_create_anime(self.store, "Naruto Shippuden")
        client = MagicMock()
        client.store = self.store
        client.bot_id = 1001
        client.username = "testbot"
        client.send_message = AsyncMock()

        # Save 720p episode
        doc1 = await app.save_episode(client, 101, "naruto_shippuden", 1, 1, "fid_720", "video", "Ep 1", None, quality="720p")
        self.assertIn("qualities", doc1)
        self.assertEqual(doc1["qualities"].get("720p"), "fid_720")

        # Save 1080p for same episode
        doc2 = await app.save_episode(client, 101, "naruto_shippuden", 1, 1, "fid_1080", "video", "Ep 1", None, quality="1080p")
        self.assertEqual(doc2["qualities"].get("720p"), "fid_720")
        self.assertEqual(doc2["qualities"].get("1080p"), "fid_1080")

    async def test_send_episode_requested_quality(self):
        await app.get_or_create_anime(self.store, "One Piece")
        client = MagicMock()
        client.store = self.store
        client.bot_id = 1001
        client.username = "testbot"
        client.send_video = AsyncMock()
        client.download_media = AsyncMock(return_value=None)

        await app.save_episode(client, 101, "one_piece", 1, 5, "fid_480", "video", "Ep 5", None, quality="480p")
        await app.save_episode(client, 101, "one_piece", 1, 5, "fid_1080", "video", "Ep 5", None, quality="1080p")

        user = {"_id": "999", "first_name": "User", "pref_quality": "1080p"}
        sent = await app.send_episode(client, 999, "one_piece", 1, 5, user=user, req_quality="1080p")
        self.assertTrue(sent)
        client.send_video.assert_called_once()
        args, kwargs = client.send_video.call_args
        self.assertEqual(args[1], "fid_1080")
        self.assertIn("Quality: 1080p", kwargs["caption"])

    async def test_anime_deep_link_handling(self):
        await app.ensure_defaults(self.store)
        await app.get_or_create_anime(self.store, "Bleach")

        client = MagicMock()
        client.store = self.store
        client.bot_id = 1001
        client.username = "testbot"
        client.send_message = AsyncMock()

        msg = MagicMock()
        msg.from_user.id = 555
        msg.from_user.first_name = "Alice"
        msg.from_user.username = "alice"
        msg.chat.id = 555
        msg.command = ["start", "anime_bleach"]

        with patch("app.show_user_season_list", new_callable=AsyncMock) as mock_season_list:
            await app.cmd_start(client, msg)
            mock_season_list.assert_called_once_with(client, 555, "bleach")

    async def test_get_official_link_fallback(self):
        await app.ensure_defaults(app.FACTORY)
        await app.ensure_defaults(self.store)

        client = MagicMock()
        client.store = self.store

        # Initially fallback to default
        self.assertEqual(app.get_official_link(client), "https://t.me")

        # Set Factory global official link
        await app.set_cfg(app.FACTORY, official_link="https://t.me/GlobalChannel")
        self.assertEqual(app.get_official_link(client), "https://t.me/GlobalChannel")

        # Set Clone custom official link
        await app.set_cfg(self.store, official_link="https://t.me/CloneChannel")
        self.assertEqual(app.get_official_link(client), "https://t.me/CloneChannel")

    async def test_callback_upload_quality_routing(self):
        await app.ensure_defaults(self.store)
        anime = await app.get_or_create_anime(self.store, "Naruto")
        aid = anime["_id"]

        client = MagicMock()
        client.store = self.store
        client.bot_id = 1001
        client.username = "testbot"

        # Mock admin permissions
        await self.store.put("admins", 123, {"_id": "123", "role": "owner", "permissions": app.PERMS})

        # Set active upload session with pending_file using actual anime_id
        app.set_sess(client, 123, "up_video", anime_id=aid, season=1, episode=1, pending_file={
            "fid": "vid_file_123",
            "mtype": "video",
            "caption": "Naruto Ep 1",
            "tid": None
        })

        q = MagicMock()
        q.from_user.id = 123
        q.data = "up_q|720p"
        q.answer = AsyncMock()
        q.message.edit_text = AsyncMock()

        await app.h_callback(client, q)

        # Check that episode was saved with 720p quality
        ep = await self.store.get("episodes", f"{aid}:1:1")
        self.assertIsNotNone(ep)
        self.assertEqual(ep["qualities"].get("720p"), "vid_file_123")

    async def test_send_start_content_buttons(self):
        await app.ensure_defaults(self.store)
        await app.set_cfg(self.store, official_link="https://t.me/MyOfficial")

        client = MagicMock()
        client.store = self.store
        client.username = "clonebot"
        client.is_factory = False
        client.send_message = AsyncMock()

        await app.send_start_content(client, 888, {"first_name": "Bob"})
        client.send_message.assert_called_once()
        args, kwargs = client.send_message.call_args
        kb = kwargs["reply_markup"]
        top_row = kb.inline_keyboard[0]
        self.assertEqual(len(top_row), 2)
        self.assertEqual(top_row[0].url, "https://t.me/MyOfficial")
        self.assertEqual(top_row[1].callback_data, "cloneme")

if __name__ == "__main__":
    unittest.main()
