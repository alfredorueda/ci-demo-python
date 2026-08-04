# Demo script — Continuous Integration in ~10 minutes

Audience: 45 junior engineers, no prior GitHub Actions experience, Python +
VS Code only. This is an **instructor-led demo** — with this many people and
this little time, don't try to get everyone coding along; narrate what you do
and let them watch the PR turn red/green on the shared screen. Point them to
this repo afterwards if they want to repeat it themselves.

Budget: ~10-12 min for the mechanics below, leaving the rest of the 30 min
for framing (why CI matters, test pyramid, cost) and questions.

## 0. Before the session

- Have the repo already cloned and open in VS Code.
- Have the GitHub repo page open in a browser tab, on the **Actions** tab.
- Confirm `main` is green (all checks passing) before you start.

## 1. Show it green (1 min)

```bash
pytest -v
```

15 tests, all passing, in ~0.02s. Say out loud: *"no Docker, no database, no
network — this is why it's instant."*

## 2. Create a branch and introduce a bug (2 min)

```bash
git checkout -b break-the-build
```

In `portfolio_domain/portfolio.py`, inside `buy(...)`, comment out this line:

```python
self._cash = self._cash.subtract(cost)
```

Run locally first, so they see the red before it even leaves your laptop:

```bash
pytest -v
```

Two tests fail: `test_buy_deducts_cash_balance` and
`test_sell_increases_cash_balance`. Good talking point: *"one small bug, two
broken behaviors — this is why a good test suite matters, not just one big
test."*

## 3. Push and open a pull request (2 min)

```bash
git add -A
git commit -m "Introduce a bug on purpose for the CI demo"
git push -u origin break-the-build
```

Open the PR against `main` on GitHub (or `gh pr create --fill`). Switch to
the browser.

## 4. Watch it fail in Actions (2 min)

- Refresh the PR page. The **Run domain tests** check goes from yellow
  (running) to red (failed) in a few seconds.
- Click into the failed check, show the actual `pytest` output — the same
  assertion errors they'd see locally.
- Point at the **Merge** button: it's disabled. *"main is protected — this
  PR cannot be merged while the check is red, no matter who you are."*

## 5. Fix it and watch it go green (2 min)

Back in VS Code, uncomment the line:

```python
self._cash = self._cash.subtract(cost)
```

```bash
git add -A
git commit -m "Fix the cash balance bug"
git push
```

Refresh the PR page. The check reruns, turns green, **Merge** becomes
available. Merge it live if you have time.

## 6. Wrap-up talking points (1-2 min)

- This whole loop — write code, push, get feedback — took minutes because
  the test suite is fast and infrastructure-free. A slow suite (databases,
  containers, external services) makes people stop waiting for it, which is
  how bugs like this slip into `main` in real teams.
- Branch protection turns "please run the tests before merging" (a request
  people forget) into "you cannot merge until they pass" (a rule the
  platform enforces).
- Everything you just saw is defined as code: `.github/workflows/ci.yml`.
  It's reviewed and versioned exactly like the application code.

## If something goes wrong live

- Actions run usually takes 10-20s to go from "queued" to a visible result.
  Don't panic during that gap — narrate what's happening instead of waiting
  in silence.
- If you need to unblock `main` for any reason mid-demo, branch protection
  can be turned off from **Settings → Branches** in a few clicks.
