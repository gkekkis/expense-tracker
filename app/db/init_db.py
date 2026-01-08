"""Module for initializing the db package."""

from .base import Base
from .engine import engine
from .models.account import Account  # noqa: F401
from .models.expense import Expense  # noqa: F401
from .models.membership import Membership  # noqa: F401
from .models.user import User  # noqa: F401


def init_db():
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    init_db()
