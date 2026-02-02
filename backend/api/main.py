from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from pydantic import BaseModel

from backend.core.schemas import AnalysisRequest, AnalysisResult
from backend.services.orchestrator import Orchestrator
from backend.utils.file_parser import parse_file
from backend.utils.report_generator import generate_pdf
from backend.utils.logger import logger

load_dotenv()

tools = {}

# Data Models
class SearchQuery(BaseModel):
    query: str

class ChatRequest(BaseModel):  # <--- NEW
    question: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🧠 Initializing Hybrid Brain...")
    tools["orchestrator"] = Orchestrator()
    yield
    logger.info("💤 Shutting down...")

app = FastAPI(title="Smart Text Analyzer", lifespan=lifespan)

@app.get("/")
def health_check():
    return {"status": "ready"}

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_text(request: AnalysisRequest):
    try:
        return await tools["orchestrator"].run_hybrid_analysis(request.text)
    except Exception as e:
        logger.error(f"Analysis Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/file", response_model=AnalysisResult)
async def analyze_file(file: UploadFile = File(...)):
    text = await parse_file(file)
    if len(text) < 10: raise HTTPException(status_code=400, detail="File empty.")
    try:
        return await tools["orchestrator"].run_hybrid_analysis(text)
    except Exception as e:
        logger.error(f"File Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/report/pdf")
async def create_report(data: AnalysisResult):
    try:
        pdf_path = generate_pdf(data.model_dump())
        return FileResponse(pdf_path, media_type="application/pdf", filename="report.pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/memory/search")
async def search_memory(search: SearchQuery):
    try:
        results = tools["orchestrator"].query_memory(search.query)
        # Simplify structure for frontend
        simple_res = []
        if results['documents']:
            for i in range(len(results['documents'][0])):
                simple_res.append({
                    "text": results['documents'][0][i],
                    "sentiment": results['metadatas'][0][i].get("sentiment"),
                    "summary": results['metadatas'][0][i].get("summary"),
                    "intent": results['metadatas'][0][i].get("intent")
                })
        return simple_res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- NEW CHAT ENDPOINT ---
@app.post("/memory/chat")
async def chat_memory(request: ChatRequest):
    try:
        answer = await tools["orchestrator"].chat_with_memory(request.question)
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Chat Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))