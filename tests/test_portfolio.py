import pytest

from portfolio_domain.exceptions import InsufficientFundsError, InsufficientSharesError
from portfolio_domain.money import Money
from portfolio_domain.portfolio import Portfolio


def test_new_portfolio_has_zero_balance_by_default():
    portfolio = Portfolio()
    assert portfolio.cash_balance == Money.of(0)


def test_deposit_increases_cash_balance():
    portfolio = Portfolio()
    portfolio.deposit(Money.of(1000))
    assert portfolio.cash_balance == Money.of(1000)


def test_buy_deducts_cash_balance():
    portfolio = Portfolio(Money.of(1000))
    portfolio.buy("AAPL", 10, Money.of("50.00"))
    assert portfolio.cash_balance == Money.of(500)


def test_buy_records_shares_owned():
    portfolio = Portfolio(Money.of(1000))
    portfolio.buy("AAPL", 10, Money.of("50.00"))
    assert portfolio.shares_owned("AAPL") == 10


def test_buy_with_insufficient_funds_raises():
    portfolio = Portfolio(Money.of(100))
    with pytest.raises(InsufficientFundsError):
        portfolio.buy("AAPL", 10, Money.of("50.00"))


def test_sell_increases_cash_balance():
    portfolio = Portfolio(Money.of(1000))
    portfolio.buy("AAPL", 10, Money.of("50.00"))
    portfolio.sell("AAPL", 10, Money.of("60.00"))
    assert portfolio.cash_balance == Money.of(1100)  # 500 left + 600 proceeds


def test_sell_reduces_shares_owned():
    portfolio = Portfolio(Money.of(1000))
    portfolio.buy("AAPL", 10, Money.of("50.00"))
    portfolio.sell("AAPL", 4, Money.of("60.00"))
    assert portfolio.shares_owned("AAPL") == 6


def test_sell_more_than_owned_raises():
    portfolio = Portfolio(Money.of(1000))
    portfolio.buy("AAPL", 5, Money.of("50.00"))
    with pytest.raises(InsufficientSharesError):
        portfolio.sell("AAPL", 10, Money.of("60.00"))


def test_sell_uses_fifo_lots_for_realized_gain():
    portfolio = Portfolio(Money.of(10_000))
    portfolio.buy("AAPL", 10, Money.of("50.00"))  # lot 1: cost basis $50/share
    portfolio.buy("AAPL", 10, Money.of("70.00"))  # lot 2: cost basis $70/share

    realized_gain = portfolio.sell("AAPL", 15, Money.of("80.00"))

    # Sells all 10 shares from lot 1 (@50) plus 5 shares from lot 2 (@70).
    # cost basis = 10*50 + 5*70 = 850 | proceeds = 15*80 = 1200 | gain = 350
    assert realized_gain == Money.of(350)
