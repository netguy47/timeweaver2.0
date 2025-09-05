from pydantic import BaseModel, Field
from typing import List

class EvidenceCard(BaseModel):
    title: str
    date: str
    type: str
    trust: float
    recency_days: int
    summary: str
    link: str

class Scenario(BaseModel):
    name: str
    likelihood: float
    thesis: str
    tripwires: List[str] = []

class Driver(BaseModel):
    factor: str
    direction: str = Field("+", pattern="[+-]")
    weight: float

class Calculation(BaseModel):
    inquiry: str
    probability: float
    band: tuple
    drivers: List[Driver]
    scenarios: List[Scenario]
    evidence: List[EvidenceCard] = []
