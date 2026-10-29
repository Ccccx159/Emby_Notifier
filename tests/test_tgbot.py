import unittest
from unittest.mock import Mock, patch

import tgbot


class TelegramGetChatTests(unittest.TestCase):
    @staticmethod
    def _response(chat):
        response = Mock()
        response.text = '{"ok": true}'
        response.raise_for_status.return_value = None
        response.json.return_value = {"ok": True, "result": chat}
        return response

    @patch("tgbot.log.logger.info")
    @patch("tgbot.requests.post")
    def test_private_chat_without_username_uses_name(self, post, info):
        post.return_value = self._response(
            {
                "id": 5139318475,
                "type": "private",
                "first_name": "Test",
                "last_name": "User",
            }
        )

        tgbot.get_chat()

        info.assert_called_once_with(
            "Telegram getChat successful. Chat User: [Test User], type: private"
        )

    @patch("tgbot.log.logger.info")
    @patch("tgbot.requests.post")
    def test_private_chat_without_name_uses_chat_id(self, post, info):
        post.return_value = self._response(
            {"id": 5139318475, "type": "private"}
        )

        tgbot.get_chat()

        info.assert_called_once_with(
            "Telegram getChat successful. Chat User: [5139318475], type: private"
        )


if __name__ == "__main__":
    unittest.main()
