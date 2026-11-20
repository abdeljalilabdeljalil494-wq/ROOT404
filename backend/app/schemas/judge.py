from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class JudgeRunRequest(BaseModel):
    project_slug: str
    files: Dict[str, str]
    language: str = "c"

class JudgeRunResponse(BaseModel):
    status: str
    score: int
    tests: List[Dict[str, Any]]
    logs: str
    execution_time: float = 0.0

class MoulinetteTest(BaseModel):
    name: str
    status: str  # pass, fail, warn
    detail: str

class MoulinetteResponse(BaseModel):
    project_slug: str
    score: int
    tests: List[MoulinetteTest]
    passed: int
    total: int

class AICodeReviewRequest(BaseModel):
    code: str
    project_slug: Optional[str] = None
    language: str = "c"

class AICodeReviewResponse(BaseModel):
    metrics: List[Dict[str, Any]]
    notes: List[Dict[str, str]]
    suggestions: List[str] = []
