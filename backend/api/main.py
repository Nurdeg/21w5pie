# backend/api/main.py
from fastapi import FastAPI, HTTPException, UploadFile, File
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from backend.core.schemas import AnalysisRequest, AnalysisResult
from backend.services.orchestrator import Orchestrator
from backend.utils.file_parser import parse_file
from backend.utils.logger import logger # New Logger

load_dotenv()

tools = {}

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
    logger.info(f"📝 Analyzing text input: {request.text[:30]}...")
    try:
        result = await tools["orchestrator"].run_hybrid_analysis(request.text)
        return result
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- NEW FILE ENDPOINT ---
@app.post("/analyze/file", response_model=AnalysisResult)
async def analyze_file(file: UploadFile = File(...)):
    """
    Upload a PDF, DOCX, or TXT file for analysis.
    """
    logger.info(f"📂 Received file: {file.filename}")
    
    # 1. Extract text from the file
    text_content = await parse_file(file)
    
    if len(text_content) < 10:
        raise HTTPException(status_code=400, detail="File contains insufficient text.")

    logger.info(f"📄 Extracted {len(text_content)} characters.")

    # 2. Run analysis on the extracted text
    try:
        result = await tools["orchestrator"].run_hybrid_analysis(text_content)
        return result
    except Exception as e:
        logger.error(f"File analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))