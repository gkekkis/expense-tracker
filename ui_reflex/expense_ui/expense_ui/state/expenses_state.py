from ..config import GET_ACCOUNT_EXPENSES_PATH
from ..services.backend_client import ApiError, request
from .accounts_state import AccountsState
from .app_state import AppState
from .auth_state import AuthState


class ExpensesState(AppState):
    expenses: list[dict] = []
    loading: bool = False
    error: str = ""
    error_code: str = ""

    async def load_expenses_for_selected_account(self) -> None:
        self.loading = True
        self.error = ""
        self.error_code = ""

        try:
            auth = await self.get_state(AuthState)
            accounts = await self.get_state(AccountsState)

            user_id = (auth.user_id or "").strip()
            account_id = (accounts.selected_account_id or "").strip()

            if not user_id or not account_id:
                self.expenses = []
                return

            path = GET_ACCOUNT_EXPENSES_PATH(account_id)
            data = request(method="GET", path=path, user_id=user_id)
            self.expenses = data if isinstance(data, list) else []

        except ApiError as e:
            self.error = e.message
            self.error_code = e.error_code or ""
            self.expenses = []

        finally:
            self.loading = False

    def clear_expenses(self) -> None:
        self.expenses = []
        self.error = ""
        self.error_code = ""
        self.loading = False
