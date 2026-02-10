from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.models.account import Account
from ..db.models.financial_profile import FinancialProfile
from ..db.models.membership import Membership, MembershipRole
from ..errors.errors import AccountDoesNotExistError, ProfileUpdateForbiddenError, UserNotMemberOfTheAccountError
from ..schemas.financial_profile import FinancialProfileUpdate


class ProfileService:
    @staticmethod
    def get_profile_by_account_id(session: Session, account_id: UUID) -> FinancialProfile | None:
        # Check if account exists first
        statement = select(1).where(Account.id == account_id).limit(1)
        if session.scalar(statement) is None:
            raise AccountDoesNotExistError(account_id=account_id)

        # Use .scalar_one_or_none() to get the object directly, not an iterator
        statement = select(FinancialProfile).where(FinancialProfile.account_id == account_id)
        return session.execute(statement).scalar_one_or_none()

    def update_profile(
        self, session: Session, account_id: UUID, user_id: UUID, data: FinancialProfileUpdate
    ) -> FinancialProfile:
        # 1. Fetch membership to check permissions
        membership = session.execute(
            select(Membership).where(Membership.user_id == user_id, Membership.account_id == account_id)
        ).scalar_one_or_none()

        if not membership:
            raise UserNotMemberOfTheAccountError(user_id=user_id, account_id=account_id)

        # 2. Fetch the profile
        profile_db = self.get_profile_by_account_id(session=session, account_id=account_id)

        # 3. Permission Gate
        if membership.role != MembershipRole.OWNER:
            # We use profile_db.id only if it exists, otherwise use None
            # This prevents 'NoneType' has no attribute 'id' errors
            p_id = profile_db.id if profile_db else None
            raise ProfileUpdateForbiddenError(financial_profile_id=p_id, user_id=user_id, account_id=account_id)

        # 4. Upsert Logic: Create if missing
        if profile_db is None:
            profile_db = FinancialProfile(account_id=account_id)
            session.add(profile_db)

        # 5. Apply updates
        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(profile_db, key, value)

        return profile_db
