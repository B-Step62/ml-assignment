import logging
import redis
from task_queue import TaskQueue
from translator.M2M100 import M2M100Translator, M2M100ModelType
from worker import TranslationWorker


REDIS_HOST = "redis"
REDIS_PORT = 6379
REDIS_DB = 0

logging.basicConfig(level=logging.INFO)


redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
task_queue = TaskQueue()
model = M2M100Translator(M2M100ModelType.M2M100_418M)
worker = TranslationWorker(translator=model, task_queue=task_queue, result_channel=redis_client)
worker.run()