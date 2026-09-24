# Autopilot trade log

One row per scheduled run. See [docs/AUTOPILOT.md](../docs/AUTOPILOT.md) for
the procedure and what each column means. Account: ••••7879.

| Date (ET) | Time (ET) | Mode | Status | SPY / SMA200 | IBIT / SMA200 | Signals | Before | Orders | Account value | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-23 | 15:45 | DRY_RUN | dry-run | 767.64 / 717.19 | 47.82 / 42.07 | core ON · crypto ON | SPY 0 sh, IBIT 0 sh, SGOV 0 sh, $700.00 cash | buy SPY $557.20 (would place); buy IBIT $139.30 (would place) | 700.00 | First run, no drawdown baseline. Control panel readable (paused=false, forceDryRun=false); DRY_RUN because ET date ≤ 2026-09-30. review_equity_order clean (no alerts) for both orders. No open/pending orders found. |
| 2026-09-24 | 15:45 | DRY_RUN | dry-run | 767.62 / 717.61 | 47.81 / 42.05 | core ON · crypto ON | SPY 0 sh, IBIT 0 sh, SGOV 0 sh, $700.00 cash | buy SPY $557.20 (would place); buy IBIT $139.30 (would place) | 700.00 | No drawdown (baseline 700.00 from 2026-09-23, current 700.00). No intraday/crypto circuit breaker triggered (SPY and IBIT both within 1% of prev close). Control panel readable (paused=false, forceDryRun=false); DRY_RUN because ET date ≤ 2026-09-30. SMA200 cross-check within 0.5% for both symbols (315 non-interpolated daily bars each). review_equity_order clean (no alerts) for both orders. No open/pending orders found. |
