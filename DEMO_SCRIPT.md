# Demo Script

A condensed, copy-paste-ready run sheet for the live walkthrough — same
content as [docs/WALKTHROUGH.md](docs/WALKTHROUGH.md), formatted for
scanning quickly while presenting or following along. About 10 minutes
end to end.

## Before starting

- [ ] On `main`, terminal open, the repository's **Actions** tab open in a
      browser tab.
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

(No `gh`? Use the "Compare & pull request" banner GitHub shows on the
repository page after the push.)

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
pytest -v          # confirm 15 passed locally first
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

---

For every step explained in full, with diagrams, see
[docs/WALKTHROUGH.md](docs/WALKTHROUGH.md). To repeat this same exercise
on your own fork afterwards, see its
["Try it yourself"](docs/WALKTHROUGH.md#6-try-it-yourself) section.
