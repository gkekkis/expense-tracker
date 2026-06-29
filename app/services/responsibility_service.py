from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.membership import Membership


class ResponsibilityService:
    @staticmethod
    def calculate_user_share(
        session: Session,
        user_id: UUID | None,
        account_id: UUID,
        total_amount: Decimal,
        personal_responsibility_factor: Decimal | None = None,
    ) -> Decimal:
        """
        Determines the user's portion of a cost.
        Priority: Override (My Treat) > Membership Default
        """
        amount = total_amount if isinstance(total_amount, Decimal) else Decimal(str(total_amount))

        # 1. Use manual override if provided (e.g., 1.0 for 100%)
        if personal_responsibility_factor is not None:
            factor = (
                personal_responsibility_factor
                if isinstance(personal_responsibility_factor, Decimal)
                else Decimal(str(personal_responsibility_factor))
            )
            return amount * factor

        # 2. Otherwise, look up the default split for this user in this account
        membership = (
            session.query(Membership).filter(Membership.account_id == account_id, Membership.user_id == user_id).first()
        )

        factor = membership.default_contribution_share if membership else Decimal("1.00")

        return amount * factor
