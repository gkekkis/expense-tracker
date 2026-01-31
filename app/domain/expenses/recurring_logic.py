"""Core module for handling recurring payments with EOM guards."""

from __future__ import annotations

from datetime import date  # noqa: TCH003

from dateutil.relativedelta import relativedelta

from ...domain.frequency_type import FrequencyType


def calculate_next_date(anchor_date: date, current_date: date, frequency: FrequencyType) -> date:
    """Calculates the next date, ensuring we always move forward."""
    if frequency == FrequencyType.DAILY:
        delta = relativedelta(days=1)
    elif frequency == FrequencyType.WEEKLY:
        delta = relativedelta(weeks=1)
    elif frequency == FrequencyType.MONTHLY:
        delta = relativedelta(months=1)
    elif frequency == FrequencyType.YEARLY:
        delta = relativedelta(years=1)
    else:
        # Fallback to prevent infinite loop if frequency is unknown
        return current_date + relativedelta(days=1)

    # 1. Move to the next period
    next_date = current_date + delta

    # 2. Re-apply the anchor day (to handle 31st -> 28th -> 31st logic)
    if frequency in [FrequencyType.MONTHLY, FrequencyType.YEARLY]:
        next_date = next_date + relativedelta(day=anchor_date.day)

    return next_date
