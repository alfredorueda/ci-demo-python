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

- [DEMO_SCRIPT.md](DEMO_SCRIPT.md) — short cheat-sheet for the instructor to
  follow while presenting.
- [docs/WALKTHROUGH.md](docs/WALKTHROUGH.md) — the full, illustrated,
  step-by-step guide (with diagrams), for both the instructor and for
  students who want to reproduce the whole exercise on their own fork
  afterwards.

## License

MIT — see [LICENSE](LICENSE).
