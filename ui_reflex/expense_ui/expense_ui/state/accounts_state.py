import reflex as rx

from ..config import GET_ACCOUNTS_PATH
from ..services.backend_client import ApiError, request
from .auth_state import AuthState


class AccountsState(rx.State):
    accounts: list[dict] = []
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

            data = request(method="GET", path=GET_ACCOUNTS_PATH, user_id=user_id)
            self.accounts = data if isinstance(data, list) else []

        except ApiError as e:
            self.error = e.message
            self.error_code = e.error_code or ""
            self.accounts = []

        finally:
            self.loading = False
