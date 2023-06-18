import logging
import redis
from src.translator.M2M100 import M2M100Translator, M2M100ModelType
from src.worker import TranslationWorker


REDIS_HOST = "redis"
REDIS_PORT = 6379
REDIS_DB = 0
TASK_CHANNEL = "task_channel"


logging.basicConfig(level=logging.DEBUG)

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
model = M2M100Translator(M2M100ModelType.M2M100_418M)
worker = TranslationWorker(redis_client, TASK_CHANNEL, model)
worker.run()