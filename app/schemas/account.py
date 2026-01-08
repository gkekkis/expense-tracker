"""Module containing Account Pydantic models."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ValidationInfo, field_validator

from ..domain.accounts.account import AccountStatus


class AccountCreate(BaseModel):
    name: str
    status: AccountStatus = AccountStatus.ACTIVE

    @field_validator("name", mode="before")
    @classmethod
    def non_empty_name(cls, value: Any, info: ValidationInfo) -> str:
        if value is None:
            raise ValueError(f"{info.field_name} must not be empty.")

        try:
            s = str(value)
        except Exception as e:
            raise ValueError(f"{info.field_name} must be a string. Got type {type(value)}.") from e

        s = s.strip()
        if not s:
            raise ValueError(f"{info.field_name} must not be blank.")

        return s


class AccountRead(BaseModel):
    id: UUID
    name: str
    status: AccountStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AccountUpdate(BaseModel):
    name: str | None = None
    status: AccountStatus | None = None

    @field_validator("name", mode="before")
    @classmethod
    def non_empty_name(cls, value: Any, info: ValidationInfo) -> str | None:
        if value is None:
            return None

        try:
            s = str(value)
        except Exception as e:
            raise ValueError(f"{info.field_name} must be a string. Got type {type(value)}.") from e

        s = s.strip()
        if not s:
            raise ValueError(f"{info.field_name} must not be blank.")

        return s
