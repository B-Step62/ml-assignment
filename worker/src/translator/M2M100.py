from enum import Enum
import threading
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer


class M2M100ModelType(Enum):
    M2M100_418M = "facebook/m2m100_418M"
    
    
class M2M100Translator:
    def __init__(self, model_type: M2M100ModelType) -> None:
        self.tokenizer = M2M100Tokenizer.from_pretrained(model_type.value)
        self.model = M2M100ForConditionalGeneration.from_pretrained(model_type.value)
        
        self.lock = threading.Lock()
    
    def translate(self, text: str, src_lang: str, tgt_lang: str) -> str:
        # Limit the number of threads trying to translate at the same time to 1 to avoid tokenizer conflicts
        with self.lock:  
            self.tokenizer.src_lang = src_lang
            self.tokenizer.tgt_lang = tgt_lang
        
            model_inputs = self.tokenizer(text, return_tensors="pt")
            generated_tokens = self.model.generate(
                **model_inputs, 
                forced_bos_token_id=self.tokenizer.get_lang_id(tgt_lang),
                max_new_tokens=200
            )
            result = self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
            
        return result[0]