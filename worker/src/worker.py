import json
import logging
import redis
import time
from src.translator.M2M100 import M2M100Translator


class TranslationWorker:
    def __init__(self, redis_client: redis.Redis, task_channel: str, translator: M2M100Translator) -> None:
        self._redis_client = redis_client
        self._task_channel = task_channel
        self._translator = translator
    
    def run(self):
        pubsub = self._redis_client.pubsub()
        pubsub.subscribe(self._task_channel)

        logging.debug("Translation worker started")        
        while True:
            message = pubsub.get_message()
            if message and message["type"] == "message":
                self.process_message(message)
            else:
                time.sleep(0.1)
            
    def process_message(self, message):
        task = json.loads(message["data"])
        logging.debug(f"Translation task {task['id']} is received")
        
        text = task["text"]
        src_lang = task["src_lang"]
        tgt_lang = task["tgt_lang"]
        
        # TODO: Add error handling
        translation = self._translator.translate(text, src_lang, tgt_lang)
        
        self._redis_client.publish(task["result_channel"], json.dumps({
            "id": task["id"],
            "text": text,
            "translation": translation
        }))