import reflex as rx

from ..config import GET_MY_ACCOUNTS_PATH
from ..models import Account
from ..services.backend_client import ApiError, request
from .app_state import AppState
from .auth_state import AuthState


class AccountsState(AppState):
    accounts: list[Account] = []
    loading: bool = False
    error: str = ""
    error_code: str = ""

    async def load_accounts(self) -> None:
        self.loading = True
        self.error = ""
        self.error_code = ""

        try:
            auth = await self.get_state(AuthState)
            user_id = (auth.user_id or "").strip()
            if not user_id:
                self.accounts = []
                return

            data = request(method="GET", path=GET_MY_ACCOUNTS_PATH, user_id=user_id)
            self.accounts = [Account.model_validate(x) for x in data] if isinstance(data, list) else []

        except ApiError as e:
            self.error = e.message
            self.error_code = e.error_code or ""
            self.accounts = []

        finally:
            self.loading = False

    @rx.var
    def total_accounts(self) -> int:
        return len(self.accounts)

    @rx.var
    def active_accounts(self) -> int:
        return sum(1 for a in self.accounts if a.status == "ACTIVE")

    @rx.var
    def inactive_accounts(self) -> int:
        return sum(1 for a in self.accounts if a.status == "INACTIVE")
