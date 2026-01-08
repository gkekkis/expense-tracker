"""Module containing domain operations."""

from __future__ import annotations

from enum import Enum


class Operation(Enum):
    # Accounts
    ACCOUNT_CREATE = "account.create"
    ACCOUNT_READ = "account.read"
    ACCOUNT_UPDATE = "account.update"
    ACCOUNT_DELETE = "account.delete"

    # Users
    USER_CREATE = "user.create"
    USER_READ = "user.read"
    USER_UPDATE = "user.update"
    USER_DELETE = "user.delete"

    # Memberships
    MEMBERSHIP_CREATE = "membership.create"
    MEMBERSHIP_READ = "membership.read"
    MEMBERSHIP_UPDATE = "membership.update"
    MEMBERSHIP_DELETE = "membership.delete"

    # Expenses
    EXPENSE_CREATE = "expense.create"
    EXPENSE_READ = "expense.read"
    EXPENSE_UPDATE = "expense.update"
    EXPENSE_DELETE = "expense.delete"
