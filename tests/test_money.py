from decimal import Decimal

from portfolio_domain.money import Money


def test_money_rounds_to_two_decimals_half_up():
    assert Money.of("10.005").amount == Decimal("10.01")


def test_money_add():
    assert Money.of(10).add(Money.of("2.50")) == Money.of("12.50")


def test_money_subtract():
    assert Money.of(10).subtract(Money.of("2.50")) == Money.of("7.50")


def test_money_multiply_by_quantity():
    assert Money.of("2.50").multiply(4) == Money.of(10)


def test_money_equality_is_by_value_not_identity():
    assert Money.of("5.00") == Money.of(5)
    assert Money.of("5.00") is not Money.of(5)


def test_money_is_negative():
    assert Money.of(-5).is_negative()
    assert not Money.of(5).is_negative()
