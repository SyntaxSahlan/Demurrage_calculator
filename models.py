from enum import Enum
from pydantic import BaseModel
from pydantic.fields import Field
from typing import Sequence

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
    
    model_config = {"strict": True, "populate_by_name": True}

class ChargeBreakdown(BaseModel):
    period_name: str
    days: int
    rate: float
    charge: float

class DemurrageResponse(BaseModel):
    total_charge: float
    breakdown: Sequence[ChargeBreakdown]
    
    model_config = {"strict": True, "populate_by_name": True}

