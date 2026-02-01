# backend/core/schemas.py
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

# --- Output Models (What we send back) ---

class Entity(BaseModel):
    text: str
    label: str

class AnalysisResult(BaseModel):
    sentiment: Literal["positive", "neutral", "negative"]
    sentiment_score: float = Field(..., description="Score between -1.0 and 1.0")
    summary: str = Field(..., description="Concise summary of the text")
    topics: List[str]
    intent: str
    entities: List[Entity]

# --- Input Models (What we receive) ---

class AnalysisRequest(BaseModel):
    text: str = Field(..., min_length=10, description="The text to analyze")
    modules: Optional[List[str]] = ["all"] # Optional config for later