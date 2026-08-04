"""Money value object.

An immutable monetary amount, always rounded to 2 decimal places.
Two Money instances are equal when their amounts are equal (value semantics).
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

_CENTS = Decimal("0.01")


@dataclass(frozen=True)
class Money:
    amount: Decimal

    def __post_init__(self) -> None:
        quantized = Decimal(self.amount).quantize(_CENTS, rounding=ROUND_HALF_UP)
        object.__setattr__(self, "amount", quantized)

    @classmethod
    def of(cls, value: int | float | str | Decimal) -> "Money":
        """Creates a Money from an int, float, string or Decimal amount."""
        return cls(Decimal(str(value)))

    def add(self, other: "Money") -> "Money":
        return Money(self.amount + other.amount)

    def subtract(self, other: "Money") -> "Money":
        return Money(self.amount - other.amount)

    def multiply(self, factor: int) -> "Money":
        return Money(self.amount * factor)

    def is_negative(self) -> bool:
        return self.amount < 0

    def __str__(self) -> str:
        return f"{self.amount}"


ZERO = Money.of(0)
