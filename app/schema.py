from pydantic import BaseModel
from typing import List


class TranslationRecord(BaseModel):
    id: str
    text: str
    
        
class TranslationPayload(BaseModel):
    records: List[TranslationRecord]
    fromLang: str
    toLang: str


class TranslationRequest(BaseModel):
    payload: TranslationPayload