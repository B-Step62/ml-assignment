import json
import unittest
from unittest.mock import MagicMock
from src.worker import TranslationWorker


class TranslationWorkerTest(unittest.TestCase):
    def setUp(self):
        self.redis_client_mock = MagicMock()
        self.translator_mock = MagicMock()
        self.worker = TranslationWorker(self.redis_client_mock, "test_channel", self.translator_mock)

    def test_process_message(self):
        message = {
            "type": "message",
            "data": json.dumps({
                "id": "123",
                "text": "Hello",
                "src_lang": "en",
                "tgt_lang": "ja",
                "result_channel": "result_channel_123"
            })
        }
        self.translator_mock.translate.return_value = "こんにちは"

        self.worker.process_message(message)

        self.translator_mock.translate.assert_called_once_with("Hello", "en", "ja")
        self.redis_client_mock.publish.assert_called_once_with(
            "result_channel_123", json.dumps({"id": "123", "text": "こんにちは"})
        )
