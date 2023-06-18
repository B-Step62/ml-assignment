from fastapi import FastAPI
import hashlib
import json
import logging
from pydantic import BaseModel
import redis
import time
from typing import List
import uuid
from task_queue import TaskQueue

logging.basicConfig(level=logging.INFO)

app = FastAPI()

REDIS_HOST = "redis"
REDIS_PORT = 6379
REDIS_DB = 0

task_queue = TaskQueue()

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
RESULT_CHANNEL = "result_channel_{job_id}"  # Each job has its own result channel


class TranslationRecord(BaseModel):
    id: str
    text: str
    
        
class TranslationPayload(BaseModel):
    records: List[TranslationRecord]
    fromLang: str
    toLang: str


class TranslationRequest(BaseModel):
    payload: TranslationPayload


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/translation")
async def translation(request: TranslationRequest, cache: bool = True):
    payload = request.payload
    src_lang = payload.fromLang
    tgt_lang = payload.toLang
    job_id = str(uuid.uuid4())
    result_channel = RESULT_CHANNEL.format(job_id=job_id)
    
    results = []
    task_waitlist = set()
    for record in payload.records:
        if cache:
            key = generate_hash(record.text, payload.fromLang, payload.toLang)
            cached_translation = r.get(key)
            if cached_translation:
                results.append({"id": record.id, "text": cached_translation})
                logging.info(f"Cache hit: {key}")
                continue
                
        task = {
            "id": record.id,
            "text": record.text,
            "src_lang": src_lang,
            "tgt_lang": tgt_lang,
            "result_channel": result_channel
        }
        task_queue.publish(json.dumps(task))
        task_waitlist.add(record.id)
        logging.info(f"Cache miss: {key}. Translation task {record.id} sent to worker.")

    # All requests can be handled by cache, no translation needed            
    if len(task_waitlist) == 0:
        logging.info("All requests can be handled by cache, no translation needed")
        return {"result": results}

    pubsub = r.pubsub()
    pubsub.subscribe(result_channel)
    
    # Busy waiting for translation results
    while len(task_waitlist) > 0:
        msg = pubsub.get_message()
        if msg and msg["type"] == "message":
            result = json.loads(msg["data"].decode("utf-8"))
            id = result["id"]
            input_text = result["text"]
            translation = result["translation"]
            results.append({"id": id, "text": translation})
            task_waitlist.remove(id)
            logging.info(f"Translation result received for {id}")
            
            key = generate_hash(input_text, src_lang, tgt_lang)
            r.set(key, translation)
            logging.info(f"Cached set for {key}")
        else:
            # If result queue is empty, wait for 0.1 second
            time.sleep(0.1)           
            
    return {"result": results}


def generate_hash(text: str, src_lang="en", tgt_lang="ja") -> str:
    hash_base = f"{src_lang}_{tgt_lang}_{text}"
    hash_object = hashlib.sha256(hash_base.encode())
    return hash_object.hexdigest()
