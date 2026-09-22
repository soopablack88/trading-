# Strategy knowledge base

These are evidence-based strategies, ranked by strength of evidence for a small,
self-directed account. Nothing here is guaranteed. Every strategy below has
had multi-year stretches of underperformance.

## What the evidence says first

- **Most active retail traders lose money.** In Taiwan, 80%+ of day traders lost
  money after costs in a typical 6-month window. In Brazil, 97% of people who
  day traded futures for 300+ days lost money. Costs, spreads, and overtrading
  are what hurt them. **Default to lower turnover.**
- **A cheap diversified core is the benchmark to beat.** If a strategy can't beat
  just holding SPY/VTI after costs and taxes, don't run it.
- **Position sizing and cutting losers matter more than entry signals.**

## 1. Core + satellite allocation (default)

- Keep 60–80% of the account in broad, low-cost index ETFs (e.g. VTI/SPY, VXUS, BND).
  Rebalance when a sleeve drifts more than 5 percentage points from its target, or once a quarter.
- Run the active strategies below only with the remaining 20–40% "satellite" portion.

## 2. Trend filter / time-series momentum (strong evidence)

Moskowitz, Ooi & Pedersen (2012) found positive 1–12 month return persistence in 58
liquid futures markets. Being long when the trailing 12-month excess return
is positive is economically equivalent to staying above a long moving average.
- **Rule:** hold an index ETF only while it is above its 200-day SMA (or its
  12-month return beats T-bills). Otherwise move to short-term Treasuries/cash.
  Check at month-end only, to avoid whipsaw.
- It gives up some return in bull markets, and its payoff is cutting drawdowns in bear markets.

## 3. Cross-sectional momentum for single stocks (strong evidence, high crash risk)

- Rank liquid large caps by 12-month return, skipping the most recent month (12-1).
  Hold the top decile, rebalance monthly, equal-weight or volatility-weight.
- Only take longs when the broad market passes the trend filter in #2. Momentum
  crashes happen in sharp rebounds after bear markets.
- To find candidates, use `create_scan` / `run_scan` and confirm with `get_equity_historicals`.

## 4. Post-earnings announcement drift, PEAD (moderate evidence, weaker than it used to be)

- After a large positive earnings surprise with a gap up on high volume, prices
  tend to keep drifting in the same direction for weeks. The effect is smaller than
  in past decades but still documented in 2024–25 research.
- **Rule:** use `get_earnings_results` to find beats on both EPS and revenue with
  raised guidance. Enter on day 1–2 if the stock holds above the gap-day low.
  Stop below that low, and exit after about 40 trading days or when the stop is hit.
  Don't hold through the next earnings.

## 5. Quality / value tilt (moderate evidence, long horizon)

- Prefer high ROE, stable margins, low debt, and positive free cash flow at
  reasonable valuations (use `get_equity_fundamentals` / `get_financials`). Use this as a
  filter on #3/#4 candidates, not as a timing signal.

## 6. Option income: cash-secured puts, covered calls (moderate evidence)

Selling options captures the volatility risk premium. The CBOE PUT index
(S&P 500 cash-secured put writing) had risk-adjusted returns comparable to the
S&P 500 with lower volatility, and put writing has beaten covered calls by about 1%/yr.
- **Rule:** only on stocks/ETFs you'd be happy to own at the strike. Use a 30–45
  day expiry and about a 0.20–0.30 delta, and close at 50% of max profit. Size so
  assignment fits within rule 4 of CLAUDE.md.
- Upside is capped and losses are the full stock loss minus premium, so it's not "free income".
- **Status:** the agentic account currently has no options level. Call
  `get_option_level_upgrade_info` before proposing any options trade.

## Avoid

- Day trading, 0DTE options, buying far out-of-the-money options, averaging down
  on losers, trading on news headlines or politician-trade feeds alone, and any
  strategy you can't state in one sentence with an exit rule.

## Sources

- Moskowitz, Ooi, Pedersen, "Time Series Momentum," JFE 2012 — https://w4.stern.nyu.edu/facdir/lpederse/papers/TimeSeriesMomentum.pdf
- Barber, Lee, Liu, Odean, "The Cross-Section of Speculator Skill" — https://faculty.haas.berkeley.edu/odean/papers/day%20traders/The%20Cross-Section%20of%20Speculator%20Skill.pdf
- Chague, De-Losso, Giovannetti, "Day Trading for a Living?" — https://www.researchgate.net/publication/334630772_Day_Trading_for_a_Living
- CBOE PutWrite/BuyWrite research — https://www.cboe.com/insights/posts/generating-income-and-managing-risk-cash-secured-put-writing-in-a-low-equity-return-environment/
- WisdomTree, "Why Fear Pays" — https://www.wisdomtree.com/us/insights/blog/why-fear-pays-the-case-for-put-writing-over-call-writing
- PEAD persistence debate — https://anderson-review.ucla.edu/is-post-earnings-announcement-drift-a-thing-again/
