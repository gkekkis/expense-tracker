import reflex as rx

from ..config import GET_ACCOUNT_BY_ID_PATH, GET_ACCOUNT_EXPENSES_PATH
from ..models import Account, Expense
from ..services.backend_client import ApiError, request
from .auth_state import AuthState


class AccountDetailState(rx.State):
    # IMPORTANT: do NOT name this `account_id` (it will shadow the route arg)
    current_account_id: str = ""

    account_name: str = ""
    account_status: str = ""

    expenses: list[Expense] = []
    loading: bool = False
    error: str = ""
    error_code: str = ""

    async def load(self) -> None:
        """Called by on_load. Reads account_id from the URL router params."""
        self.loading = True
        self.error = ""
        self.error_code = ""

        # ✅ get dynamic route param from router
        account_id = self.router.page.params.get("account_id", "")
        self.current_account_id = account_id

        try:
            auth = await self.get_state(AuthState)
            user_id = (auth.user_id or "").strip()
            if not user_id or not account_id:
                self.expenses = []
                self.account_name = ""
                self.account_status = ""
                return

            acc_data = request(method="GET", path=GET_ACCOUNT_BY_ID_PATH.format(account_id=account_id), user_id=user_id)
            acc = Account.model_validate(acc_data)
            self.account_name = acc.name
            self.account_status = acc.status

            exp_data = request(
                method="GET", path=GET_ACCOUNT_EXPENSES_PATH.format(account_id=account_id), user_id=user_id
            )
            self.expenses = [Expense.model_validate(x) for x in exp_data] if isinstance(exp_data, list) else []

        except ApiError as e:
            self.error = e.message
            self.error_code = e.error_code or ""
            self.expenses = []
            self.account_name = ""
            self.account_status = ""

        finally:
            self.loading = False

    @rx.var
    def total_expenses(self) -> int:
        return len(self.expenses)

    @rx.var
    def total_amount(self) -> float:
        # amount is a string in your schema; convert safely
        total = 0.0
        for e in self.expenses:
            try:
                total += float(e.amount)
            except Exception:
                pass
        return round(total, 2)

    @rx.var
    def top_category(self) -> str:
        if not self.expenses:
            return "-"
        counts: dict[str, int] = {}
        for e in self.expenses:
            counts[e.category] = counts.get(e.category, 0) + 1
        return max(counts, key=counts.get)
