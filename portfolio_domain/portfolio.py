"""Portfolio aggregate: tracks cash and stock holdings for one investor.

Shares are sold FIFO (first lot bought is the first lot sold), which is
the standard convention for computing realized gains.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from .exceptions import InsufficientFundsError, InsufficientSharesError
from .money import Money


@dataclass
class _Lot:
    """A batch of shares bought together at the same price."""

    quantity: int
    price: Money


class Portfolio:
    def __init__(self, initial_cash: Money | None = None) -> None:
        self._cash = initial_cash if initial_cash is not None else Money.of(0)
        self._lots: dict[str, deque[_Lot]] = {}

    @property
    def cash_balance(self) -> Money:
        return self._cash

    def shares_owned(self, ticker: str) -> int:
        return sum(lot.quantity for lot in self._lots.get(ticker, ()))

    def deposit(self, amount: Money) -> None:
        self._cash = self._cash.add(amount)

    def buy(self, ticker: str, quantity: int, price: Money) -> None:
        cost = price.multiply(quantity)
        if cost.amount > self._cash.amount:
            raise InsufficientFundsError(
                f"Cannot buy {quantity} {ticker}: cost {cost} exceeds cash balance {self._cash}"
            )
        self._cash = self._cash.subtract(cost)
        self._lots.setdefault(ticker, deque()).append(_Lot(quantity, price))

    def sell(self, ticker: str, quantity: int, price: Money) -> Money:
        """Sells shares FIFO and returns the realized gain (or loss, if negative)."""
        available = self.shares_owned(ticker)
        if quantity > available:
            raise InsufficientSharesError(
                f"Cannot sell {quantity} {ticker}: only {available} shares owned"
            )

        lots = self._lots[ticker]
        remaining_to_sell = 0
        cost_basis = Money.of(0)

        while remaining_to_sell > 0:
            oldest_lot = lots[0]
            consumed = min(oldest_lot.quantity, remaining_to_sell)
            cost_basis = cost_basis.add(oldest_lot.price.multiply(consumed))
            oldest_lot.quantity -= consumed
            remaining_to_sell -= consumed
            if oldest_lot.quantity == 0:
                lots.popleft()

        proceeds = price.multiply(quantity)
        self._cash = self._cash.add(proceeds)
        return proceeds.subtract(cost_basis)
