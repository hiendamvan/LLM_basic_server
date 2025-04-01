from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import cohere
import os
import fitz  # PyMuPDF để đọc file PDF

# Load biến môi trường từ .env
load_dotenv()

api_key = os.getenv("COHERE_API_KEY")
if not api_key:
    raise ValueError("COHERE_API_KEY not found in environment variables.")
co = cohere.Client(api_key)

app = FastAPI()

# Bộ nhớ tạm để lưu nội dung các file PDF đã upload
pdf_store = {}

# Hàm trích xuất văn bản từ file PDF
def extract_text_from_pdf(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Endpoint upload file PDF
@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        pdf_bytes = await file.read()
        text = extract_text_from_pdf(pdf_bytes)
        pdf_store[file.filename] = text
        return {"message": "File uploaded successfully!", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Request model cho câu hỏi
class QuestionRequest(BaseModel):
    filename: str
    question: str

# Endpoint hỏi đáp dựa trên nội dung file PDF đã upload
@app.post("/ask_pdf/")
async def ask_pdf(request: QuestionRequest):
    if request.filename not in pdf_store:
        raise HTTPException(status_code=404, detail="File not found.")
    
    # Lấy nội dung file PDF từ bộ nhớ
    pdf_content = pdf_store[request.filename]
    
    # Tạo prompt chứa nội dung tài liệu và câu hỏi
    prompt = f"Nội dung tài liệu:\n{pdf_content}\n\nCâu hỏi: {request.question}\nTrả lời:"
    
    try:
        response = co.chat(
            model="command-r",
            message=request.question,
            chat_history=[
                {"role": "user", "message": prompt}
            ]
        )
        return {"answer": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
