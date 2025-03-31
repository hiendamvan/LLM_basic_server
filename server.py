from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import cohere
import os 

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv("COHERE_API_KEY")
if not api_key:
    raise ValueError("COHERE_API_KEY not found in environment variables.")
co = cohere.Client(api_key)

app = FastAPI()

# Request model 
class TranslationRequest(BaseModel):
    text: str
    source_language: str
    target_language: str

# translation function 
def translate_text(text, source_language, target_language):
    response = co.chat(
        model = 'command-r', 
        message=text,
        chat_history=[
            {"role": "user", "message": f"Translate the following text from {source_language} to {target_language}: {text}"}
        ],
    )
    return response.text

# Endpoint for translation
@app.post("/translate")
async def translate(request: TranslationRequest):
    try:
        translated_text = translate_text(request.text, request.source_language, request.target_language)
        return {"translated_text": translated_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
