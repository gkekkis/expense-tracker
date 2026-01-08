"""Module containing custom errors."""

from uuid import UUID

from ..domain.operations import Operation


class ExpenseTrackerProjectError(Exception):
    pass


# USERS
class UserDoesNotExistError(ExpenseTrackerProjectError):
    def __init__(self, user_id: UUID):
        self.user_id = user_id


class UserNotMemberOfTheAccountError(ExpenseTrackerProjectError):
    def __init__(self, user_id: UUID, account_id: UUID):
        self.user_id = user_id
        self.account_id = account_id


# ACCOUNTS
class AccountDoesNotExistError(ExpenseTrackerProjectError):
    def __init__(self, account_id: UUID):
        self.account_id = account_id


class AccountUpdateNoFieldsProvidedError(ExpenseTrackerProjectError):
    def __init__(self, account_id: UUID):
        self.account_id = account_id


class AccountUpdateForbiddenError(ExpenseTrackerProjectError):
    def __init__(self, user_id: UUID, account_id: UUID):
        self.user_id = user_id
        self.account_id = account_id


class AccountInactiveError(ExpenseTrackerProjectError):
    def __init__(self, account_id: UUID, operation: Operation):
        self.account_id = account_id
        self.operation = operation


# EXPENSES
class ExpenseDoesNotExistError(ExpenseTrackerProjectError):
    def __init__(self, expense_id: UUID):
        self.expense_id = expense_id


class ExpenseUpdateNoFieldsProvidedError(ExpenseTrackerProjectError):
    def __init__(self, expense_id: UUID):
        self.expense_id = expense_id


class ExpenseUpdateForbiddenError(ExpenseTrackerProjectError):
    def __init__(self, user_id: UUID, expense_id: UUID, account_id: UUID):
        self.user_id = user_id
        self.expense_id = expense_id
        self.account_id = account_id


class ExpenseDeleteForbiddenError(ExpenseTrackerProjectError):
    def __init__(self, user_id: UUID, expense_id: UUID, account_id: UUID):
        self.user_id = user_id
        self.expense_id = expense_id
        self.account_id = account_id


# MEMBERSHIPS
class MembershipDoesNotExistError(ExpenseTrackerProjectError):
    def __init__(self, membership_id: UUID):
        self.membership_id = membership_id


class MembershipAlreadyExistError(ExpenseTrackerProjectError):
    def __init__(self, user_id: UUID, account_id: UUID):
        self.user_id = user_id
        self.account_id = account_id


class MembershipUpdateNoFieldsProvidedError(ExpenseTrackerProjectError):
    def __init__(self, membership_id: UUID):
        self.membership_id = membership_id


class MembershipUpdateForbiddenError(ExpenseTrackerProjectError):
    def __init__(self, user_id: UUID, membership_id: UUID, account_id: UUID):
        self.user_id = user_id
        self.membership_id = membership_id
        self.account_id = account_id


class MembershipDeleteForbiddenError(ExpenseTrackerProjectError):
    def __init__(self, user_id: UUID, membership_id: UUID, account_id: UUID):
        self.user_id = user_id
        self.membership_id = membership_id
        self.account_id = account_id


class MembershipLastOwnerDeleteForbiddenError(ExpenseTrackerProjectError):
    def __init__(self, user_id: UUID, membership_id: UUID, account_id: UUID):
        self.user_id = user_id
        self.membership_id = membership_id
        self.account_id = account_id


class MembershipLastOwnerDemoteForbiddenError(ExpenseTrackerProjectError):
    def __init__(self, user_id: UUID, membership_id: UUID, account_id: UUID):
        self.user_id = user_id
        self.membership_id = membership_id
        self.account_id = account_id


class MembershipCreateForbiddenError(ExpenseTrackerProjectError):
    def __init__(self, user_id: UUID, account_id: UUID):
        self.user_id = user_id
        self.account_id = account_id


class MembershipFirstOwnerRequiredError(ExpenseTrackerProjectError):
    def __init__(self, account_id: UUID):
        self.account_id = account_id
