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

    async def test_help_command_excludes_rajpapa(self):
        await app.ensure_defaults(self.store)
        client = MagicMock()
        client.store = self.store
        client.is_factory = True
        msg = MagicMock()
        msg.from_user.id = app.DEFAULT_SUPREME_ID
        msg.reply = AsyncMock()

        await app.cmd_help(client, msg)
        msg.reply.assert_called_once()
        help_text = msg.reply.call_args[0][0]

        self.assertNotIn("/rajpapa", help_text)
        self.assertIn("/seasonend", help_text)
        self.assertIn("/coming", help_text)
        self.assertIn("/done", help_text)
        self.assertIn("/cancel", help_text)

    async def test_show_user_episode_list_no_anime_banner_leak(self):
        await app.ensure_defaults(self.store)
        anime = await app.get_or_create_anime(self.store, "Solo Leveling")
        aid = anime["_id"]
        await self.store.update("animes", aid, banner_file_id="anime_banner_123")

        client = MagicMock()
        client.store = self.store
        client.send_message = AsyncMock()

        await app.show_user_episode_list(client, 999, aid, 1)
        client.send_message.assert_called_once()
        # Ensure send_photo was not called because season banner was not set
        client.send_photo = getattr(client, "send_photo", AsyncMock())
        client.send_photo.assert_not_called()

    async def test_ed_apply_video_and_thumb_updates(self):
        await app.ensure_defaults(self.store)
        anime = await app.get_or_create_anime(self.store, "Jujutsu Kaisen")
        aid = anime["_id"]

        client = MagicMock()
        client.store = self.store
        client.bot_id = 1001

        await app.save_episode(client, 123, aid, 1, 1, "old_fid", "video", "Caption", "old_tid", quality="720p")

        # Mock active session for video edit
        app.set_sess(client, 123, "ed_video", aid=aid, s=1, e=1)

        m = MagicMock()
        m.from_user.id = 123
        m.video.file_id = "new_fid"
        m.video.thumbs = [MagicMock(file_id="new_tid")]
        m.reply = AsyncMock()

        with patch("app.show_editor", new_callable=AsyncMock):
            await app.ed_apply(client, m, "video")

        ep = await self.store.get("episodes", f"{aid}:1:1")
        self.assertEqual(ep["file_id"], "new_fid")
        self.assertEqual(ep["file_ids"], ["new_fid"])
        self.assertEqual(ep["qualities"], {})

    async def test_validate_channel_parsing(self):
        client = MagicMock()
        chat_mock = MagicMock()
        chat_mock.id = -100123456789
        client.get_chat = AsyncMock(return_value=chat_mock)

        member_mock = MagicMock()
        member_mock.status = app.CMS.ADMINISTRATOR
        client.get_chat_member = AsyncMock(return_value=member_mock)

        # Test string positive channel ID
        chat = await app.validate_channel(client, "123456789")
        self.assertIsNotNone(chat)
        self.assertEqual(chat.id, -100123456789)

    async def test_ban_user_flow(self):
        await app.ensure_defaults(self.store)
        client = MagicMock()
        client.store = self.store
        client.bot_id = 1001

        # Add admin with ban_users perm
        await self.store.put("admins", "100", {"_id": "100", "role": "owner", "permissions": app.PERMS})

        msg = MagicMock()
        msg.from_user.id = 100
        msg.command = ["ban", "200"]
        msg.reply_to_message = None
        msg.reply = AsyncMock()

        await app.cmd_ban(client, msg)

        is_banned = await app.is_user_banned(client, 200)
        self.assertTrue(is_banned)

        # Unban user
        msg.command = ["unban", "200"]
        await app.cmd_unban(client, msg)

        is_banned_after = await app.is_user_banned(client, 200)
        self.assertFalse(is_banned_after)

    async def test_transfer_ownership_flow(self):
        await app.ensure_defaults(self.store)
        client = MagicMock()
        client.store = self.store
        client.bot_id = 1001
        client.username = "testbot"
        client.is_factory = False
        client.send_message = AsyncMock()

        # Set owner 111
        await app.set_cfg(self.store, owner_id=111)
        await self.store.put("admins", "111", {"_id": "111", "name": "Old Owner", "role": "owner", "permissions": app.PERMS})

        # Test transfer to non-existent user 222 (not started bot)
        msg1 = MagicMock()
        msg1.from_user.id = 111
        msg1.text = "222"
        msg1.reply = AsyncMock()

        app.set_sess(client, 111, "transfer_owner_target")
        await app.route_session(client, msg1, app.get_sess(client, 111))
        msg1.reply.assert_called_once()
        self.assertIn("USER HAS NOT STARTED THE BOT", msg1.reply.call_args[0][0])

        # Register user 222 in bot's database
        await self.store.put("users", "222", {"_id": "222", "first_name": "New Owner", "started_at": app.now()})

        # Now target user exists -> route_session prompts for confirmation
        msg2 = MagicMock()
        msg2.from_user.id = 111
        msg2.text = "222"
        msg2.reply = AsyncMock()

        app.set_sess(client, 111, "transfer_owner_target")
        await app.route_session(client, msg2, app.get_sess(client, 111))
        msg2.reply.assert_called_once()
        self.assertIn("CONFIRM OWNERSHIP TRANSFER", msg2.reply.call_args[0][0])

        # Execute callback `adm|do_transfer|222`
        q = MagicMock()
        q.from_user.id = 111
        q.data = "adm|do_transfer|222"
        q.answer = AsyncMock()
        q.message.edit_text = AsyncMock()

        await app.h_callback(client, q)

        # Verify new owner configuration
        cfg = app.cfg(self.store)
        self.assertEqual(cfg["owner_id"], 222)

        new_owner_doc = await self.store.get("admins", "222")
        self.assertIsNotNone(new_owner_doc)
        self.assertEqual(new_owner_doc["role"], "owner")

        old_owner_doc = await self.store.get("admins", "111")
        self.assertEqual(old_owner_doc["role"], "manager")

    async def test_clone_forcesub_verification_flow(self):
        await app.ensure_defaults(self.store)
        await app.ensure_defaults(app.FACTORY)

        client = MagicMock()
        client.store = self.store
        client.bot_id = 1001
        client.username = "factorybot"
        client.is_factory = True
        client.send_message = AsyncMock()

        # Set user with pending_action = "clone"
        await self.store.put("users", "777", {"_id": "777", "first_name": "CloneUser", "pending_action": "clone"})

        # Mock fs_state to return True (verified)
        with patch("app.fs_state", new_callable=AsyncMock) as mock_fs:
            mock_fs.return_value = (True, None)

            q = MagicMock()
            q.from_user.id = 777
            q.from_user.first_name = "CloneUser"
            q.data = "ckfs"
            q.answer = AsyncMock()
            q.message.delete = AsyncMock()

            await app.h_callback(client, q)

            # Verify session set to clone_token and CLONE_PROMPT sent directly
            sess = app.get_sess(client, 777)
            self.assertIsNotNone(sess)
            self.assertEqual(sess["step"], "clone_token")

            client.send_message.assert_called_once()
            self.assertIn("ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ᴏᴡɴ ᴀɴɪᴍᴇ ʙᴏᴛ", client.send_message.call_args[0][1])

    async def test_episode_thumb_replacement(self):
        await app.ensure_defaults(self.store)
        anime = await app.get_or_create_anime(self.store, "Demon Slayer")
        aid = anime["_id"]

        client = MagicMock()
        client.store = self.store
        client.bot_id = 1001
        client.download_media = AsyncMock(return_value="/tmp/test_thumb.jpg")

        await app.save_episode(client, 123, aid, 1, 1, "video_123", "video", "Caption", None)

        # Set active session for thumb edit
        app.set_sess(client, 123, "ed_thumb", aid=aid, s=1, e=1)

        m = MagicMock()
        m.from_user.id = 123
        m.text = None
        m.photo = MagicMock(file_id="new_photo_thumb_fid")
        m.document = None
        m.reply = AsyncMock()

        with patch("app.show_editor", new_callable=AsyncMock), patch("os.path.exists", return_value=True):
            await app.ed_apply(client, m, "thumb")

        ep = await self.store.get("episodes", f"{aid}:1:1")
        self.assertEqual(ep["thumb_id"], "new_photo_thumb_fid")
        self.assertEqual(ep["thumb_path"], "/tmp/test_thumb.jpg")

if __name__ == "__main__":
    unittest.main()
