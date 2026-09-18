from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ProjectBase(BaseModel):
    slug: str
    name: str
    description: str
    level: str = "Niveau 1"
    lang: str = "C"
    lang_color: str = "#3B9EFF"
    tags: List[str] = []
    difficulty: int = 1
    xp: int = 1000
    duration: str = "1 sem."

class ProjectCreate(ProjectBase):
    long_description: Optional[str] = None
    requires: Optional[str] = None
    objectives: List[str] = []
    constraints: List[Dict[str, str]] = []

class ProjectResponse(ProjectBase):
    id: str
    requires: Optional[str] = None
    xp: int
    status: Optional[str] = "available"
    progress: Optional[int] = None
    score: Optional[int] = None
    
    class Config:
        from_attributes = True

class SubmissionCreate(BaseModel):
    files: Dict[str, str]
    language: str = "c"

class SubmissionResponse(BaseModel):
    id: str
    project_id: str
    status: str
    score: Optional[int] = None
    tests: List[Dict[str, Any]] = []
    logs: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProgressResponse(BaseModel):
    project_id: str
    status: str
    progress: int
    score: Optional[int] = None
    attempts: int
    best_score: int
