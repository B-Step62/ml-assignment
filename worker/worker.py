import json
import logging
import pika
import redis
from task_queue import TaskQueue
from translator.M2M100 import M2M100Translator


class TranslationWorker:
    def __init__(self,
                 translator: M2M100Translator,
                 task_queue: TaskQueue,
                 result_channel: redis.Redis) -> None:
        self._translator = translator
        self._task_queue = task_queue
        self._result_channel = result_channel

    def run(self):
        self._task_queue.consume(callback=self.process_message)
        logging.info("Translation worker started")    
            
    def process_message(self, 
                        ch: pika.channel.Channel, 
                        method: pika.spec.Basic.Deliver, 
                        properties: pika.BasicProperties, 
                        body: bytes) -> None:
        task = json.loads(body)
        logging.info(f"Translation task {task['id']} is received")
        
        text = task["text"]
        src_lang = task["src_lang"]
        tgt_lang = task["tgt_lang"]
        
        # TODO: Add error handling
        translation = self._translator.translate(text, src_lang, tgt_lang)
        logging.info(f"Translation task {task['id']} is completed")
        
        self._result_channel.publish(task["result_channel"], json.dumps({
            "id": task["id"],
            "text": text,
            "translation": translation
        }))
        
        self._task_queue.channel.basic_ack(delivery_tag=method.delivery_tag)