from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class FinancialProfileBase(BaseModel):
    monthly_net_income: Decimal = Field(default=0.0, ge=0)
    savings_percentage_goal: Decimal = Field(default=0.0, ge=0, le=100)
    emergency_fund_target: Decimal = Field(default=0.0, ge=0)


class FinancialProfileUpdate(FinancialProfileBase):
    monthly_net_income: Optional[Decimal] = None
    savings_percentage_goal: Optional[Decimal] = None
    emergency_fund_target: Optional[Decimal] = None


class FinancialProfileResponse(FinancialProfileBase):
    id: UUID
    account_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BudgetStatus(BaseModel):
    total_income: Decimal
    total_spent: Decimal
    remaining_budget: Decimal
    health_percentage: float
