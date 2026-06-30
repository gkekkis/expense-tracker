"""Blueprint module of the Expense default categories."""

from __future__ import annotations

from .expense import ExpenseCategory

CATEGORY_EMOJI_MAP = {
    ExpenseCategory.RENTAL: "🏠",
    ExpenseCategory.BILLS: "📄",
    ExpenseCategory.GROCERIES: "🛒",
    ExpenseCategory.HOUSEHOLD: "🧼",
    ExpenseCategory.DELIVERY_FOOD: "🥡",
    ExpenseCategory.DINING_OUT: "🍽️",
    ExpenseCategory.PET: "🐾",
    ExpenseCategory.GAS: "⛽",
    ExpenseCategory.CAR: "🚗",
    ExpenseCategory.TRAVEL: "✈️",
    ExpenseCategory.ENTERTAINMENT: "🎬",
    ExpenseCategory.HEALTH: "🏥",
    ExpenseCategory.PERSONAL: "💆",
    ExpenseCategory.SAVINGS: "💰",
    ExpenseCategory.MISC: "📦",
}
