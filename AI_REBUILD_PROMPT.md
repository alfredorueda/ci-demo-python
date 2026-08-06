# Prompt: Rebuild `ci-demo-python` From Scratch (for restricted networks)

**Copy this entire file and paste it as a single prompt to your AI coding
assistant** (Claude Code, Copilot, or similar) inside an empty folder. It
reconstructs the whole teaching repository with maximum fidelity — code,
tests, CI workflow, and the live demo script — without needing to fork or
clone the original from GitHub, for environments where that isn't possible.

---

## Instructions for the AI assistant

You are setting up a small, self-contained Python teaching repository from
this specification. Follow these steps in order:

1. Create the directory structure listed in **"File tree"** below.
2. Create every file listed in **"File contents"** with the content given
   **exactly as written** — do not reformat, "improve", rename, or
   reorganize anything. Fidelity to the original matters more than style
   here.
3. Create and activate a Python virtual environment, then install
   dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
4. Run the test suite and confirm it reports **`15 passed`**:
   ```bash
   pytest -v
   ```
   If it doesn't, stop and diff every file against the spec below before
   continuing — nothing past this point works on a broken baseline.
5. Initialize git and make the first commit on `main`:
   ```bash
   git init -b main
   git add -A
   git commit -m "Initial commit: recreate ci-demo-python teaching repo"
   ```
6. Tell the user (a human) to create a new, empty repository on whatever
   git hosting their organization allows — GitHub, GitHub Enterprise,
   GitLab, Bitbucket, an internal server, anything — and to push this
   repository to it:
   ```bash
   git remote add origin <the-new-repository-url>
   git push -u origin main
   ```
7. Tell the user this **cannot** be done by writing files — it requires
   clicking through their git host's web UI (or its CLI/API) — and walk
   them through **"Recreating branch protection"** below. This step is
   the entire point of the exercise: without it, the rest of the demo
   script has nothing to demonstrate.
8. Once branch protection is confirmed working, hand the user the
   **"Demo script"** section at the end of this file for the live
   exercise.

Do not skip step 7 or treat it as optional — a repository with all the
right code but no protected `main` teaches nothing about CI enforcement.

---

## File tree

```
ci-demo-python/
  .github/
    workflows/
      ci.yml
  portfolio_domain/
    __init__.py
    exceptions.py
    money.py
    portfolio.py
  tests/
    test_money.py
    test_portfolio.py
  .gitignore
  DEMO_SCRIPT.md
  LICENSE
  pyproject.toml
  README.md
  requirements.txt
```

---

## File contents

### `.github/workflows/ci.yml` — critical

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    name: Run domain tests
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: pytest -v
```

### `portfolio_domain/__init__.py` — critical

```python
"""portfolio_domain: a tiny, dependency-free stock portfolio domain model.

Used as a live example for a continuous integration training session.
No web framework, no database, no external services — just business rules
and the tests that pin them down.
"""
```

### `portfolio_domain/exceptions.py` — critical

```python
"""Domain-level errors raised by the portfolio model."""


class DomainError(Exception):
    """Base class for all portfolio domain errors."""


class InsufficientFundsError(DomainError):
    """Raised when a purchase would cost more than the available cash balance."""


class InsufficientSharesError(DomainError):
    """Raised when a sale would exceed the shares currently held for a ticker."""
```

### `portfolio_domain/money.py` — critical

```python
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
```

### `portfolio_domain/portfolio.py` — critical

```python
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
        remaining_to_sell = quantity
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
```

### `tests/test_money.py` — critical

```python
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
```

### `tests/test_portfolio.py` — critical

```python
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
```

### `.gitignore` — critical

```
__pycache__/
*.pyc
.pytest_cache/
.venv/
venv/
.vscode/
.idea/
*.egg-info/

# OS-generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
Thumbs.db
ehthumbs.db
Desktop.ini
```

### `pyproject.toml` — critical

```toml
[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
```

### `requirements.txt` — critical

```
pytest>=8.0,<9
```

### `LICENSE` — optional, include for completeness

```
MIT License

Copyright (c) 2026 Alfredo Rueda

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### `README.md` — optional, include for completeness

````markdown
# ci-demo-python

A tiny, dependency-free stock portfolio domain model in Python, used as a live
example in a Continuous Integration training session. No web framework, no
database, no external services — just business rules and the tests that pin
them down, wired to a GitHub Actions pipeline that blocks merging into `main`
when a test fails.

## What's here

```
portfolio_domain/
  money.py       Money value object (immutable, rounds to 2 decimals)
  portfolio.py   Portfolio aggregate: deposit / buy / sell shares, FIFO lots
  exceptions.py  Domain errors (insufficient funds / insufficient shares)
tests/
  test_money.py
  test_portfolio.py
.github/workflows/ci.yml   Runs the full test suite on every push and PR
```

## Running it locally

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -v
```

All 15 tests run in well under a second — no Docker, no network, no database.

## The point of this repo

`main` is protected: a pull request cannot be merged while the
**Run domain tests** check is failing. Try it yourself:

1. Create a branch.
2. Break something in `portfolio_domain/portfolio.py` (or "fix" a test to
   expect the wrong thing).
3. Push the branch and open a pull request against `main`.
4. Watch the check turn red — the **Merge** button is disabled.
5. Fix the code, push again — the check turns green and the PR becomes
   mergeable.

See [DEMO_SCRIPT.md](DEMO_SCRIPT.md) for the condensed, copy-paste-ready
run sheet for the live walkthrough above.

## License

MIT — see [LICENSE](LICENSE).
````

### `DEMO_SCRIPT.md` — critical

This is the same demo script used in the original training, adapted for a
repository you already own (no "fork" step — you already have write
access to your own repo). Everything else — the branch protection
mechanism, the bug, the recovery steps — is identical.

````markdown
# Demo Script

A condensed, copy-paste-ready run sheet for the live walkthrough. About 10
minutes end to end.

## Before starting

- [ ] **Install dependencies** — `pytest` is not installed by default,
      it comes from `requirements.txt`:
      ```bash
      python3 -m venv .venv
      source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
      pip install -r requirements.txt
      ```
      Confirmed it worked if the terminal prompt now starts with
      `(.venv)` and `pytest --version` prints a version instead of
      "command not found".
- [ ] On `main`, terminal open, the repository's **Actions** (or
      equivalent CI) tab open in a browser tab.
- [ ] Confirm the baseline:
  ```bash
  git checkout main
  git pull
  pytest -v
  ```
  Expected: `15 passed`.

## 1. Baseline (~1 min)

```bash
pytest -v
```

`15 passed` in ~0.02s — no Docker, no database, no network call. That's
what makes the rest of this run fast.

## 2. Branch, then break the build on purpose (~2 min)

> ⚠️ **STOP — switch branch before editing or committing anything.**
> `main` is protected: no direct pushes, no exceptions, not even for
> repository admins. Run the command below *first*, before touching
> `portfolio_domain/portfolio.py`. If you forget and commit on `main` by
> mistake, nothing is lost — see "Committed straight to `main` by
> mistake?" under "If something stalls" below — but saving yourself that
> detour starts here:

```bash
git checkout -b break-the-build
```

In `portfolio_domain/portfolio.py`, inside `buy(...)`, comment out:

```python
self._cash = self._cash.subtract(cost)
```

```bash
pytest -v
```

Expected: `2 failed, 13 passed` —
`test_buy_deducts_cash_balance` and `test_sell_increases_cash_balance`.
One bug, two broken behaviors: this is why a suite covers more than one
scenario.

## 3. Push and open a pull request (~2 min)

```bash
git add -A
git commit -m "Introduce a bug on purpose for the CI demo"
git push -u origin break-the-build
gh pr create --fill
```

(No `gh`? Use the "Compare & pull request" banner your git host shows on
the repository page after the push.)

## 4. Watch the check fail (~2 min)

- Refresh the PR page: the check goes yellow (queued/running) → red, in
  about 10–20 seconds.
- **Details** on the failed check → same `pytest` output as local.
- **Merge** button: greyed out — *"Merging is blocked — Required statuses
  must pass before merging."* Applies to everyone, including repository
  admins — that's the branch protection rule on `main`.

## 5. Fix it and watch it go green (~2 min)

Uncomment the line:

```python
self._cash = self._cash.subtract(cost)
```

```bash
pytest -v
git add -A
git commit -m "Fix the cash balance bug"
git push
```

Refresh the PR: check turns green → **Merge** button active → merge
(`Squash and merge` is a fine default).

## 6. Recap (~1–2 min)

- This whole loop took minutes only because the suite is fast and
  infrastructure-free — a slow one trains people to stop waiting for it,
  which is how bugs like this reach `main` on real projects.
- Branch protection turns "please run the tests before merging" into "you
  cannot merge until they pass" — enforced, not requested.
- The entire pipeline is `.github/workflows/ci.yml` — versioned and
  reviewed like any other code.

## If something stalls

- Actions runs typically take 10–20s to go from "queued" to a result —
  that gap is normal, not a failure.
- Branch protection can be turned off from **Settings → Branches** if
  `main` needs to be unblocked for any reason.
- **Committed straight to `main` by mistake** (forgot to branch first,
  under time pressure — it happens to everyone)? Nothing is lost:
  branch protection blocked the *push*, so the commit only ever existed
  locally. Move it to a branch instead of losing it:
  ```bash
  git branch break-the-build      # snapshot the commit onto a new branch
  git reset --hard origin/main    # bring local main back in sync
  git checkout break-the-build    # keep working from here
  ```
  Then continue from step 3 (push the branch, open a PR) as normal. This
  is the same protection at work as the rest of this document, just
  catching a slip instead of a deliberate bad change — that's the point:
  it doesn't ask why the push happened, it just requires a PR either way.
- `pytest: command not found`? The virtual environment isn't active —
  re-run `source .venv/bin/activate` (macOS/Linux) or
  `.venv\Scripts\Activate.ps1` (Windows) from the "Install dependencies"
  step above.

## Corporate network access

If your git host is blocked on your corporate network, `git clone`,
`git push`, and friends may fail with a connection or timeout error. This
is a network-level restriction, unrelated to this repository — check
with your organization: many companies already document the exact proxy
configuration needed for `git` in an internal channel. Ask your IT/network
team or your training organizer if you're not sure where to find it.
````

---

## Recreating branch protection (do this after the first push)

Writing files can't do this part — it has to be done once, by hand, in
your git host's settings, after `.github/workflows/ci.yml` has run at
least once (push a commit first if the check isn't searchable yet).

**On GitHub** (classic branch protection):
1. Repository → **Settings → Branches**.
2. **Add branch protection rule** (or **Add rule**).
3. Branch name pattern: `main`.
4. Enable **Require status checks to pass before merging**.
5. Search for and select **Run domain tests** (this is the `name:` field
   of the job in `ci.yml` — only becomes searchable once the workflow has
   run at least once).
6. Enable **Do not allow bypassing the above settings** — this is what
   makes the rule apply to repository admins too, not just other
   contributors.
7. **Create** (or **Save changes**).

**On GitHub** (newer rulesets, `Settings → Rules → Rulesets`): create a
ruleset targeting `main` with the `pull_request` rule (blocks direct
pushes) and `required_status_checks` set to the `Run domain tests`
context, with no bypass actors.

**On GitLab**: **Settings → Repository → Protected branches**, protect
`main`, and combine with **Settings → CI/CD → General pipelines →
"Pipelines must succeed"** merge check under merge request settings.

**On Bitbucket**: **Repository settings → Branch permissions**, restrict
pushes to `main`, and enable **"Check build status" → require all builds
to be successful** on the pull request settings.

Confirm it worked before moving on: try `git push` directly to `main` —
it should be rejected. That rejection is the entire mechanism this demo
exists to teach.
