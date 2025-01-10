from enum import Enum
from pydantic import BaseModel


class CommunicationState(str, Enum):
    ENGAGED = "ENGAGED"
    NO_RESPONE = "NO_RESPONSE"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class DebtorProfile(BaseModel):
    communication_state: str
    name: str
    income: float
    outstanding_balance: float
    overdue_days: int
    risk_level: str | None


class NextBestAction(BaseModel):
    action: str
    target: str
