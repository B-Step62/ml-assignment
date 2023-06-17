from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from translator.M2M100 import M2M100Translator, M2M100ModelType


app = FastAPI()
translator = M2M100Translator(M2M100ModelType.M2M100_418M)


class TranslationRecord(BaseModel):
    id: str
    text: str
    
        
class TranslationPayload(BaseModel):
    records: List[TranslationRecord]
    fromLang: str
    toLang: str


class TranslationRequest(BaseModel):
    payload: TranslationPayload


@app.post("/translation")
async def translation(request: TranslationRequest):
    payload = request.payload
    
    results = []
    for record in payload.records:
        translated = translator.translate(record.text, payload.fromLang, payload.toLang)
        results.append({"id": record.id, "text": translated})   
        
    return {"result": results}


# For test
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9527)