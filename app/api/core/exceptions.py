"""Module for registering custom errors to specific HTTP responses."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from ...errors.errors import (
    AccountDoesNotExistError,
    AccountInactiveError,
    AccountUpdateForbiddenError,
    AccountUpdateNoFieldsProvidedError,
    ExpenseDeleteForbiddenError,
    ExpenseDoesNotExistError,
    ExpenseUpdateForbiddenError,
    ExpenseUpdateNoFieldsProvidedError,
    MembershipAlreadyExistError,
    MembershipCreateForbiddenError,
    MembershipDeleteForbiddenError,
    MembershipDoesNotExistError,
    MembershipFirstOwnerRequiredError,
    MembershipLastOwnerDeleteForbiddenError,
    MembershipLastOwnerDemoteForbiddenError,
    MembershipUpdateForbiddenError,
    MembershipUpdateNoFieldsProvidedError,
    UserDoesNotExistError,
    UserHasNoAccountsError,
    UserNotMemberOfTheAccountError,
)


# USERS
def register_exception_handlers(app: FastAPI):
    @app.exception_handler(UserDoesNotExistError)
    async def user_does_not_exist_handler(request: Request, exc: UserDoesNotExistError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error_code": "USER_NOT_FOUND",
                "detail": f"User with id `{exc.user_id}` does not exist.",
                "path": request.url.path,
            },
        )

    @app.exception_handler(UserNotMemberOfTheAccountError)
    async def user_not_member_of_the_account_handler(
        request: Request, exc: UserNotMemberOfTheAccountError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error_code": "USER_NOT_MEMBER_OF_THE_ACCOUNT",
                "detail": f"User with id `{exc.user_id}` is not a member of the account with id `{exc.account_id}`.",
                "path": request.url.path,
            },
        )

    @app.exception_handler(UserHasNoAccountsError)
    async def user_has_no_accounts_handler(request: Request, exc: UserHasNoAccountsError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error_code": "USER_HAS_NO_ACCOUNTS",
                "detail": f"User with id `{exc.user_id}` has no accounts.",
                "path": request.url.path,
            },
        )

    # ACCOUNTS
    @app.exception_handler(AccountDoesNotExistError)
    async def account_does_not_exist_handler(request: Request, exc: AccountDoesNotExistError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error_code": "ACCOUNT_NOT_FOUND",
                "detail": f"Account with id `{exc.account_id}` does not exist.",
                "path": request.url.path,
            },
        )

    @app.exception_handler(AccountInactiveError)
    async def account_inactive_handler(request: Request, exc: AccountInactiveError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error_code": "ACCOUNT_INACTIVE",
                "detail": f"Account with id `{exc.account_id}` is currently inactive. "
                f"Can not perform operation `{exc.operation.value}`.",
                "path": request.url.path,
            },
        )

    @app.exception_handler(AccountUpdateNoFieldsProvidedError)
    async def account_update_no_fields_provided_handler(
        request: Request, exc: AccountUpdateNoFieldsProvidedError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error_code": "ACCOUNT_UPDATE_NO_FIELDS_PROVIDED",
                "detail": f"Tried to update account with id `{exc.account_id}` but no fields were provided.",
                "path": request.url.path,
            },
        )

    @app.exception_handler(AccountUpdateForbiddenError)
    async def account_update_forbidden_handler(request: Request, exc: AccountUpdateForbiddenError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error_code": "ACCOUNT_UPDATE_FORBIDDEN",
                "detail": f"User with id `{exc.user_id}` is not authorized to update account"
                f" with id `{exc.account_id}`.",
                "path": request.url.path,
            },
        )

    # EXPENSES
    @app.exception_handler(ExpenseDoesNotExistError)
    async def expense_does_not_exist_handler(request: Request, exc: ExpenseDoesNotExistError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error_code": "EXPENSE_NOT_FOUND",
                "detail": f"Expense with id `{exc.expense_id}` does not exist.",
                "path": request.url.path,
            },
        )

    @app.exception_handler(ExpenseUpdateNoFieldsProvidedError)
    async def expense_update_no_fields_provided_handler(
        request: Request, exc: ExpenseUpdateNoFieldsProvidedError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error_code": "EXPENSE_UPDATE_NO_FIELDS_PROVIDED",
                "detail": f"Tried to update expense with id `{exc.expense_id}` but no fields were provided.",
                "path": request.url.path,
            },
        )

    @app.exception_handler(ExpenseUpdateForbiddenError)
    async def expense_update_forbidden_handler(request: Request, exc: ExpenseUpdateForbiddenError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error_code": "EXPENSE_UPDATE_FORBIDDEN",
                "detail": f"User with id `{exc.user_id}` that has account with id `{exc.account_id}` is not authorized"
                f" to update expense with id `{exc.expense_id}`.",
                "path": request.url.path,
            },
        )

    @app.exception_handler(ExpenseDeleteForbiddenError)
    async def expense_delete_forbidden_handler(request: Request, exc: ExpenseDeleteForbiddenError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error_code": "EXPENSE_DELETE_FORBIDDEN",
                "detail": f"User with id `{exc.user_id}` that has account with id `{exc.account_id}` is not authorized"
                f" to delete expense with id `{exc.expense_id}`.",
                "path": request.url.path,
            },
        )

    # MEMBERSHIPS
    @app.exception_handler(MembershipDoesNotExistError)
    async def membership_does_not_exist_handler(request: Request, exc: MembershipDoesNotExistError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error_code": "MEMBERSHIP_NOT_FOUND",
                "detail": f"Membership with id `{exc.membership_id}` does not exist.",
                "path": request.url.path,
            },
        )

    @app.exception_handler(MembershipAlreadyExistError)
    async def membership_already_exists_handler(request: Request, exc: MembershipAlreadyExistError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error_code": "MEMBERSHIP_ALREADY_EXISTS",
                "detail": f"User with id `{exc.user_id}` is already a member of account with id `{exc.account_id}`.",
                "path": request.url.path,
            },
        )

    @app.exception_handler(MembershipUpdateNoFieldsProvidedError)
    async def membership_update_no_fields_provided_handler(
        request: Request, exc: MembershipUpdateNoFieldsProvidedError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error_code": "MEMBERSHIP_UPDATE_NO_FIELDS_PROVIDED",
                "detail": f"Tried to update membership with id `{exc.membership_id}` but no fields were provided.",
                "path": request.url.path,
            },
        )

    @app.exception_handler(MembershipUpdateForbiddenError)
    async def membership_update_forbidden_handler(
        request: Request, exc: MembershipUpdateForbiddenError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error_code": "MEMBERSHIP_UPDATE_FORBIDDEN",
                "detail": f"User with id `{exc.user_id}` that has account with id `{exc.account_id}` is not authorized"
                f" to update membership with id `{exc.membership_id}`.",
                "path": request.url.path,
            },
        )

    @app.exception_handler(MembershipLastOwnerDeleteForbiddenError)
    async def membership_last_owner_delete_forbidden_handler(
        request: Request, exc: MembershipLastOwnerDeleteForbiddenError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error_code": "MEMBERSHIP_LAST_OWNER_DELETE_FORBIDDEN",
                "detail": f"Membership with id `{exc.membership_id}` deletion forbidden. User with id `{exc.user_id}` "
                f"is the only OWNER of account with id `{exc.account_id}`.",
                "path": request.url.path,
            },
        )

    @app.exception_handler(MembershipDeleteForbiddenError)
    async def membership_delete_forbidden_handler(
        request: Request, exc: MembershipDeleteForbiddenError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error_code": "MEMBERSHIP_DELETE_FORBIDDEN",
                "detail": f"User with id `{exc.user_id}` is not authorized to delete membership with "
                f"id `{exc.membership_id}` of account with id `{exc.account_id}`.",
                "path": request.url.path,
            },
        )

    @app.exception_handler(MembershipLastOwnerDemoteForbiddenError)
    async def membership_last_owner_demote_forbidden_handler(
        request: Request, exc: MembershipLastOwnerDemoteForbiddenError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error_code": "MEMBERSHIP_LAST_OWNER_DEMOTE_FORBIDDEN",
                "detail": f"Membership with id `{exc.membership_id}` update forbidden. "
                f"User with id `{exc.user_id}` is the only OWNER of account with id `{exc.account_id}`.",
                "path": request.url.path,
            },
        )

    @app.exception_handler(MembershipCreateForbiddenError)
    async def membership_create_forbidden_handler(
        request: Request, exc: MembershipCreateForbiddenError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error_code": "MEMBERSHIP_CREATE_FORBIDDEN",
                "detail": f"User with id `{exc.user_id}` is not authorized to create membership of "
                f"account with id `{exc.account_id}`.",
                "path": request.url.path,
            },
        )

    @app.exception_handler(MembershipFirstOwnerRequiredError)
    async def membership_first_owner_required_handler(
        request: Request, exc: MembershipFirstOwnerRequiredError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error_code": "MEMBERSHIP_FIRST_OWNER_REQUIRED",
                "detail": f"Can not create membership for account with id "
                f"`{exc.account_id}`. Need to have at least one OWNER.",
                "path": request.url.path,
            },
        )
