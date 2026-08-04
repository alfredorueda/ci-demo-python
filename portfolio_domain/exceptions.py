"""Domain-level errors raised by the portfolio model."""


class DomainError(Exception):
    """Base class for all portfolio domain errors."""


class InsufficientFundsError(DomainError):
    """Raised when a purchase would cost more than the available cash balance."""


class InsufficientSharesError(DomainError):
    """Raised when a sale would exceed the shares currently held for a ticker."""
