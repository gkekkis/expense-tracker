from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...api.dependencies import get_current_user_id, get_db
from ...schemas.recurring_template import RecurringTemplateCreate, RecurringTemplateRead, RecurringTemplateUpdate
from ...services import recurring_template_service

router = APIRouter(prefix="/recurring-templates", tags=["recurring-templates"])

CurrentUser = Annotated[UUID, Depends(get_current_user_id)]
Db = Annotated[Session, Depends(get_db)]


@router.post("/", response_model=RecurringTemplateRead)
def create_recurring_template_endpoint(payload: RecurringTemplateCreate, current_user_id: CurrentUser, db: Db):
    tmpl = recurring_template_service.create(session=db, current_user_id=current_user_id, payload=payload)
    db.commit()
    db.refresh(tmpl)
    return tmpl


@router.patch("/{template_id}", response_model=RecurringTemplateRead)
def update_recurring_template_endpoint(
    template_id: UUID, payload: RecurringTemplateUpdate, current_user_id: CurrentUser, db: Db
):
    tmpl = recurring_template_service.update(
        session=db, current_user_id=current_user_id, template_id=template_id, payload=payload
    )
    db.commit()
    db.refresh(tmpl)
    return tmpl


@router.delete("/{template_id}", status_code=204)
def delete_recurring_template_endpoint(template_id: UUID, current_user_id: CurrentUser, db: Db):
    recurring_template_service.delete(session=db, current_user_id=current_user_id, template_id=template_id)
    db.commit()
