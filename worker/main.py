import os
import redis
from task_queue import TaskQueue
from translator.M2M100 import M2M100Translator, M2M100ModelType
from worker import TranslationWorker

redis_client = redis.Redis(
    host=os.environ.get("REDIS_HOST"), 
    port=os.environ.get("REDIS_PORT"), 
    db=os.environ.get("REDIS_DB")
)
task_queue = TaskQueue()
model = M2M100Translator(M2M100ModelType.M2M100_418M)
worker = TranslationWorker(translator=model, task_queue=task_queue, result_channel=redis_client)
worker.run()