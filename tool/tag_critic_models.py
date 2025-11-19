from typing import List, Optional
from pydantic import BaseModel, Field

class TagEvaluation(BaseModel):
    tag: str
    relevance: float = Field(0.0, ge=0.0, le=100.0)
    clarity: float = Field(0.0, ge=0.0, le=100.0)
    quality: float = Field(0.0, ge=0.0, le=100.0)
    specificity: float = Field(0.0, ge=0.0, le=100.0)
    coverage: float = Field(0.0, ge=0.0, le=100.0)
    distinctiveness: float = Field(0.0, ge=0.0, le=100.0)
    score: float = Field(0.0, ge=0.0, le=100.0)

class RevisionModel(BaseModel):
    original: Optional[str] = None
    revised: str
    reason: Optional[str] = None

class IterationLog(BaseModel):
    iteration: int
    evaluations: List[TagEvaluation]
    failing_count: int
    passing_count: int

class TagCriticResponse(BaseModel):
    original_tags: List[str]
    final_tags: List[str]
    threshold: float
    iterations: int
    iteration_logs: List[IterationLog]
    last_evaluations: List[TagEvaluation]
    agent: str
    error: Optional[str] = None
