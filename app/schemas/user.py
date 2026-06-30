"""Module containing User Pydantic models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID  # noqa: TCH003

from pydantic import BaseModel, EmailStr, Field, ValidationInfo, field_validator

from ..domain.users.user import UserStatus


class UserCreate(BaseModel):
    name: str
    status: UserStatus = UserStatus.ACTIVE
    email: EmailStr
    password: str | None = Field(default=None, min_length=8, max_length=128)

    @field_validator("name", mode="before")
    @classmethod
    def non_empty_str(cls, value: Any, info: ValidationInfo) -> str:
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


class UserRead(BaseModel):
    id: UUID
    name: str
    email: Optional[EmailStr] = None
    status: UserStatus
    created_at: datetime

    model_config = {"from_attributes": True}
