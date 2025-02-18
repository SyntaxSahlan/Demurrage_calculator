from enum import Enum
from pydantic import BaseModel, Field
from typing import List

class ContainerType(str, Enum):
    FULL = "FULL"
    REEFER = "REEFER"
    IMCO = "IMCO"
    EMPTY = "EMPTY"

class ContainerSize(str, Enum):
    TWENTY = "20"
    FORTY = "40"

class DemurrageRequest(BaseModel):
    container_type: ContainerType
    container_size: ContainerSize
    days: int = Field(ge=0)

class ChargeBreakdown(BaseModel):
    period_name: str
    days: int
    rate: float
    charge: float

class DemurrageResponse(BaseModel):
    total_charge: float
    breakdown: List[ChargeBreakdown]

