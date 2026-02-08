from decimal import Decimal
from uuid import UUID, uuid4


class FinancialProfile:
    """Blueprint class for an Account's Financial Profile."""

    def __init__(
        self,
        account_id: UUID,
        monthly_net_income: Decimal = Decimal("0.00"),
        savings_percentage_goal: Decimal = Decimal("0.00"),
        emergency_fund_target: Decimal = Decimal("0.00"),
        profile_id: UUID | None = None,
    ) -> None:
        if savings_percentage_goal < 0 or savings_percentage_goal > 100:
            raise ValueError("Savings goal must be between 0 and 100.")

        self.id = profile_id or uuid4()
        self.account_id = account_id
        self.monthly_net_income = monthly_net_income
        self.savings_percentage_goal = savings_percentage_goal
        self.emergency_fund_target = emergency_fund_target
