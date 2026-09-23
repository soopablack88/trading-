# Autopilot: SPY / SGOV trend switch

This is the unattended procedure for the scheduled trading Routine. The
account owner authorized it in writing on 2026-09-23: these runs place orders
**without per-trade approval**, as an exception to CLAUDE.md rule 2. No other
session may use this exception.

Every scheduled run follows every step below, in order. When a step says
**stop**, write the log row (step 9), push it, and end the run. Never place an
order after a stop.

## How this relates to CLAUDE.md

CLAUDE.md rules 1, 3, 7, 9, and 10 apply as written. The market orders here
are regular-hours only and have a spread check, so they meet rule 3. For
rule 5, the exit plan for every position is the band: SPY is sold when a run finds it below the lower band, and SGOV is
sold when a run finds SPY above the upper band.

The owner gave these runs exceptions (2026-09-23) to three rules:

- Rule 2: orders are placed without per-trade approval.
- Rule 4: sizing and the 10% position cap are replaced by Step 7, which puts
  up to 100% of investable cash in SPY or SGOV.
- Rule 6: the -3% daily and -10% from peak halts are replaced by Step 5's
  5% intraday and 20% since-last-run halts.

If CLAUDE.md no longer has any one of these exceptions, a **LIVE** run that
would place an order stops with status `blocked-rules` before placing
anything. DRY_RUN is unaffected.

## Fixed parameters

| Parameter | Value |
|---|---|
| Account | Agentic account `••••7879` only. Confirm with `get_accounts` that the account ending `7879` exists and is the one with `agentic_allowed = true`. Every other account is read-only. |
| Symbols | `SPY` (risk-on) and `SGOV` (risk-off). Never trade anything else. Never sell other positions in the account. |
| Schedule | Weekdays, 15:45 America/New_York |
| Signal | SPY last price vs the 200-day SMA of SPY daily closes, with a ±1% band |
| Order types | Buys: `type=market`, `dollar_amount`. Sells: `type=market`, `quantity` (shares). Always `market_hours=regular_hours`, `time_in_force=gfd`. |
| Pre-trade check | `review_equity_order` before every order. **Any alert aborts the run.** |
| Max orders | 2 per run (placed in live mode, or would-place in dry-run mode) |
| Mode | **DRY_RUN** while the ET date is on or before 2026-09-30. **LIVE** from 2026-10-01 on. |
| Kill switch | A file named `PAUSE` at the repo root |
| Log | `logs/trades.md`, committed and pushed every run |

## Step 0: Clock and duplicate guard

The Routine fires at both 19:45 and 20:45 UTC, so one firing is 15:45 ET
whether daylight saving time is in effect or not.

1. Get the current time in `America/New_York` (`TZ=America/New_York date`).
2. If it is Saturday or Sunday, or the time is outside 15:40–15:55 ET, this
   is the off-hour firing. End the run **without** logging or pushing
   anything. The final message says `Off-hour firing, no action.`
3. If `logs/trades.md` already has a row for today's ET date with a status
   other than `off-hour`, a run already happened today. End without trading.
   Log a `duplicate` row.

## Step 1: Kill switch

Run `git fetch origin main` and check for `PAUSE` both in the working branch
and on `origin/main` (`git cat-file -e origin/main:PAUSE`). If either one has
it, **stop** with status `paused`. The contents of `PAUSE` don't matter. Write
them in the notes if they're short.

## Step 2: Market open / holiday

**Stop** with status `holiday` if any of these are true:

- Today is on the NYSE closure list below.
- The SPY quote's `venue_last_trade_time` is not today's ET date, or it is
  more than 5 minutes old. (This also covers early-close days, like the day
  after Thanksgiving, when the market is already closed at 15:45.)

NYSE full-day closures (this list is a backup; the live quote check above
wins, and if either one says closed, skip):

- 2026: Nov 26, Dec 25
- 2027: Jan 1, Jan 18, Feb 15, Mar 26, May 31, Jun 18, Jul 5, Sep 6, Nov 25, Dec 24

Update this list every December from the NYSE calendar.

## Step 3: Gather data

Use the Robinhood connector tools only:

1. `get_accounts`: confirm the ••••7879 account (see Fixed parameters).
2. `get_portfolio(account)`: `total_value`, `cash`, `buying_power.unleveraged_buying_power`.
3. `get_equity_positions(account)`: SPY and SGOV quantity and `shares_available_for_sells`.
4. `get_equity_orders(account)`: any open or pending orders.
5. `get_equity_quotes(["SPY","SGOV"])`: last price, bid/ask, previous close, timestamps, state.
6. `get_equity_technical_indicators(symbol="SPY", type="sma", period=200, interval="day", start_time=<~15 months ago>, output="last:2")`: `SMA200`.
7. `get_equity_historicals(symbols=["SPY"], interval="day", start_time=<~15 months ago>)`:
   daily bars for the cross-check, plus today's open.

## Step 4: Bad-data checks

**Stop** with status `bad-data` and name the failed check if any of these are true:

- A tool call above errored or returned empty or missing fields after one retry.
- The ••••7879 account is missing, or it isn't the agentic account.
- For SPY or SGOV: `state` isn't `active`, `has_traded` is false, the price is
  ≤ 0, bid > ask, or the spread is more than 0.5% of the price.
- There are fewer than 200 non-`interpolated` completed daily SPY bars.
- An SMA200 recomputed from the last 200 non-interpolated completed daily
  closes differs from the indicator's `SMA200` by more than 0.5%.
- SGOV's last price is more than 1% from its previous close. SGOV is a T-bill
  ETF, so a move like that means the data is wrong. It only drops by about the
  size of its dividend on its monthly ex-dividend date.
- There are open or pending SPY or SGOV orders from an earlier run.
- `total_value` is ≤ 0, or it is far from cash + positions × prices (more than 2% off).

## Step 5: Circuit breakers

**Stop** with status `halted` if either of these is true:

- **Intraday move:** SPY's last price is more than 5% from its
  `adjusted_previous_close`, or more than 5% from today's open.
- **Account drawdown:** `total_value` is more than 20% below the account value
  recorded in the most recent earlier log row that has one. On the first run,
  there's no baseline, so this check passes. A deposit or withdrawal can trip
  this check or hide a real drop. If you know one happened, say so in the notes.

## Step 6: Signal

```
upper = SMA200 × 1.01
lower = SMA200 × 0.99
if SPY_last > upper: target = SPY
elif SPY_last < lower: target = SGOV
else: target = current holding
```

**Current holding** is whichever of SPY and SGOV has the larger market value
in the account. If the account holds neither (cash only), the current holding
is `SGOV`, because SGOV is the cash-like side of the strategy. So a cash-only
account inside the band buys SGOV.

## Step 7: Plan the orders

The strategy only uses **investable cash**:
`min(cash, unleveraged_buying_power)`. It never uses margin or other positions.

1. **Sell the non-target:** If the account holds the non-target symbol (SPY or
   SGOV), sell all of it: `side=sell`, `type=market`,
   `quantity=<shares_available_for_sells>`, up to 6 decimals.
2. **Buy the target:** Buy `dollar_amount = floor_to_cents(investable_cash × 0.995)`
   of the target. Skip the buy if that amount is under max($5, 2% of `total_value`).
   The 0.5% buffer covers price movement on the market order.

If there's nothing to sell and nothing worth buying, the result is `hold`: no
orders.

This plan never has more than 2 orders. If a plan somehow has more, **stop**
with status `bad-data`.

## Step 8: Execute

For each planned order, sell first, then buy:

1. Call `review_equity_order` with exactly the parameters above. If the
   response has **any** alert or warning (buying power, PDT, halt, anything
   else), **stop** with status `aborted` and quote the alert. Don't place this
   order or any order after it.
2. **DRY_RUN:** don't call `place_equity_order`. Record the order as
   `would place`. For the buy that follows a sell, review it with the cash
   available now. If that is under the minimum, write "buy funded by sell
   proceeds, reviewed after sell fills in live mode" instead of reviewing it.
   It still counts toward the 2-order limit.
3. **LIVE:** call `place_equity_order` with the same parameters and a fresh
   UUID `ref_id`. On a transport error, retry once with the **same** `ref_id`.
4. **LIVE, sell then buy:** after the sell, check `get_equity_orders` about
   every 20 s until it is `filled`. Stop waiting at 15:57 ET. If it isn't
   filled by then, **don't buy**: end with status `partial` (the account
   stays in cash until the next run). Once it fills, re-read `get_portfolio`
   and recompute the buy amount from the new investable cash before reviewing
   the buy.
5. After a live buy, check once that it filled and record the fill price and
   quantity.

## Step 9: Log and push

Append one row to the table in `logs/trades.md`:

| Column | Content |
|---|---|
| Date (ET) | `YYYY-MM-DD` |
| Time (ET) | `HH:MM` |
| Mode | `DRY_RUN` or `LIVE` |
| Status | `traded`, `dry-run`, `hold`, `paused`, `holiday`, `bad-data`, `halted`, `aborted`, `partial`, `duplicate`, `blocked-rules` |
| SPY | last price |
| SMA200 | value |
| Band | `lower–upper` |
| Signal | `SPY`, `SGOV`, or `inside→<holding>` |
| Before | holdings before the run, e.g. `SGOV 1.98 sh, $2.10 cash` |
| Orders | each order: `sell SGOV 1.98 sh` / `buy SPY $199.00`, with the fill or `would place` |
| Account value | `total_value` at the start of the run |
| Notes | reason for a stop, alerts, anything unusual |

Fill in what you have. Use `—` for values you didn't get to. Always record
`Account value` when it was read, because the next run's drawdown check uses it.

Then commit on the working branch (see the Routine prompt) with the message
`autopilot: <date> <status>` and push with `git push -u origin <branch>`. If
the push fails, run `git pull --rebase origin <branch>` and retry up to 4
times, waiting 2 s, 4 s, 8 s, then 16 s. Never force-push.

## Step 10: Report

End the run with a short summary: mode, status, signal, orders (with fills),
and account value. Mask the account as `••••7879`. Anything other than
`hold` or `dry-run` counts as noteworthy for notifications.

## Owner controls

- **Pause:** add a file named `PAUSE` at the repo root on `main` or on the
  autopilot branch. It works from the GitHub web UI. Delete it to resume.
- **Stop for good:** delete or disable the Routine.
- **Change the rules:** edit this file. The Routine reads it fresh every run.
