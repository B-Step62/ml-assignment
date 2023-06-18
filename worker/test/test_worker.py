import json
import unittest
from unittest.mock import MagicMock
from worker import TranslationWorker


class TranslationWorkerTest(unittest.TestCase):
    def setUp(self):
        self.translator_mock = MagicMock()
        self.task_queue_mock = MagicMock()
        self.result_channel_mock = MagicMock()
        self.worker = TranslationWorker(
            self.translator_mock,
            self.task_queue_mock,
            self.result_channel_mock)

    def test_process_message(self):
        task = {
                "id": "123",
                "text": "Hello",
                "src_lang": "en",
                "tgt_lang": "ja",
                "result_channel": "result_channel_123"
        }
        body = json.dumps(task).encode("utf-8")
        method = MagicMock()
        method.delivery_tag = 123
        
        self.translator_mock.translate.return_value = "こんにちは"

        self.worker.process_message(None, method, None, body)

        self.translator_mock.translate.assert_called_once_with("Hello", "en", "ja")
        self.result_channel_mock.publish.assert_called_once_with(
            "result_channel_123", json.dumps({"id": "123", "text": "Hello", "translation": "こんにちは"})
        )
        self.task_queue_mock.channel.basic_ack.assert_called_once_with(delivery_tag=123)
