from fastapi import FastAPI
import hashlib
import json
import logging
import os
import redis
import time
import uuid
from schema import TranslationRequest
from task_queue import TaskQueue

logging.basicConfig(level=logging.INFO)

app = FastAPI()

task_queue = TaskQueue()

r = redis.Redis(
    host=os.environ.get("REDIS_HOST"),
    port=os.environ.get("REDIS_PORT"), 
    db=os.environ.get("REDIS_DB")
)
RESULT_CHANNEL = "result_channel_{job_id}"  # Each job has its own result channel


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/translation")
async def translation(request: TranslationRequest, cache: bool = True):
    payload = request.payload
    job_id = str(uuid.uuid4())
    result_channel = RESULT_CHANNEL.format(job_id=job_id)
    
    results = []
    task_waitlist = set()
    for record in payload.records:
        # Check if the translation is in cache
        if cache:
            key = generate_hash(record.text, payload.fromLang, payload.toLang)
            cached_translation = r.get(key)
            if cached_translation:
                results.append({"id": record.id, "text": cached_translation})
                logging.info(f"Cache hit: {key}")
                continue
                
        # If not, publish translation task to worker
        task = {
            "id": record.id,
            "text": record.text,
            "src_lang": payload.fromLang,
            "tgt_lang": payload.toLang,
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
    
    # Busy wait for translation results
    while len(task_waitlist) > 0:
        msg = pubsub.get_message()
        if msg and msg["type"] == "message":
            result = json.loads(msg["data"].decode("utf-8"))
            logging.info(f"Translation result received for {result['id']}")
            if result["status"] == "OK":
                id = result["id"]
                input_text = result["text"]
                translation = result["translation"]
                results.append({"id": id, "text": translation})
                task_waitlist.remove(id)
            
                key = generate_hash(input_text, payload.fromLang, payload.toLang)
                r.set(key, translation)
                logging.info(f"Cached set for {key}")
            else:
                # For the time being, just return failure message for partial translation error rather than retrying.
                result.append({"id": id, "text": "Translation failed."})
        else:
            time.sleep(0.1)
            
    return {"result": results}

def generate_hash(text: str, src_lang="en", tgt_lang="ja") -> str:
    hash_base = f"{src_lang}_{tgt_lang}_{text}"
    hash_object = hashlib.sha256(hash_base.encode())
    return hash_object.hexdigest()
