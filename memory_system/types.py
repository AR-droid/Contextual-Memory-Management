from dataclasses import dataclass
from typing import Literal

@dataclass
class Memory:
    id: str
    content: str
    type: str  # e.g., USER_BELIEF, USER_PREFERENCE, USER_FACT

InfluenceLevel = Literal["HIGH", "CONDITIONAL", "SUPPRESS"]
RoleType = Literal["PERSONALIZATION", "USER_PERSPECTIVE", "CONTEXT", "EVIDENCE", "SUPPRESS"]

@dataclass
class ControllerDecision:
    memory_id: str
    relevance: float
    memory_type: str
    influence: InfluenceLevel
    role: RoleType
    reason: str
