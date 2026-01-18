from sqlalchemy import MetaData  # noqa: F401

from .declarative_base import Base
from .models.account import Account  # noqa: F401
from .models.currency import CurrencyRate  # noqa: F401
from .models.expense import Expense  # noqa: F401
from .models.membership import Membership  # noqa: F401
from .models.user import User  # noqa: F401

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
Base.metadata.naming_convention = naming_convention
