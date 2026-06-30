"""Module containing custom errors."""

from decimal import Decimal
from uuid import UUID

from ..domain.operations import Operation


class ExpenseTrackerProjectError(Exception):
    pass


# USERS
class UserDoesNotExistError(ExpenseTrackerProjectError):
    def __init__(self, user_id: UUID):
        self.user_id = user_id


class UserListForbiddenError(ExpenseTrackerProjectError):
    pass


class UserReadForbiddenError(ExpenseTrackerProjectError):
    def __init__(self, user_id: UUID, target_user_id: UUID):
        self.user_id = user_id
        self.target_user_id = target_user_id


class UserNotMemberOfTheAccountError(ExpenseTrackerProjectError):
    def __init__(self, user_id: UUID, account_id: UUID):
        self.user_id = user_id
        self.account_id = account_id


class UserHasNoAccountsError(ExpenseTrackerProjectError):
    def __init__(self, user_id: UUID):
        self.user_id = user_id


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


class AccountMutationForbiddenError(ExpenseTrackerProjectError):
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


# CATEGORIES
class CategoryNotFoundError(ExpenseTrackerProjectError):
    def __init__(self, category_id: UUID):
        self.category_id = category_id


# FINANCIAL PROFILES
class ProfileUpdateForbiddenError(ExpenseTrackerProjectError):
    def __init__(self, financial_profile_id: UUID, account_id: UUID, user_id: UUID):
        self.financial_profile_id = financial_profile_id
        self.account_id = account_id
        self.user_id = user_id


class InvalidUserShareError(ExpenseTrackerProjectError):
    def __init__(self, personal_responsibility_factor: Decimal):
        self.personal_responsibility_factor = personal_responsibility_factor


# RECURRING TEMPLATES
class RecurringTemplateDoesNotExistError(ExpenseTrackerProjectError):
    def __init__(self, recurring_template_id: UUID):
        self.recurring_template_id = recurring_template_id


class RecurringTemplateUpdateForbiddenError(ExpenseTrackerProjectError):
    def __init__(self, user_id: UUID, recurring_template_id: UUID, account_id: UUID):
        self.user_id = user_id
        self.recurring_template_id = recurring_template_id
        self.account_id = account_id


class RecurringTemplateCreateForbiddenError(ExpenseTrackerProjectError):
    def __init__(self, user_id: UUID, account_id: UUID):
        self.user_id = user_id
        self.account_id = account_id
