# Autopilot backtest (rough)

Run on 2026-09-23 to check the rules in [AUTOPILOT.md](AUTOPILOT.md) before
live trading. Scripts: [research/backtest.py](../research/backtest.py) and
[research/combined.py](../research/combined.py).

**Read this as a sanity check, not a forecast.** It shows how the rules would
have behaved in past markets. It says nothing reliable about future returns.

## Data and assumptions

- SPY: Robinhood daily closes, split-adjusted, 1999-09 to 2026-09. Dividends
  are added back as an approximate yield by era (1.4–2.0%/yr), not the actual
  payments.
- Bitcoin: Alpha Vantage BTC-USD daily closes, weekdays only, standing in for
  IBIT (IBIT only launched in 2024). An IBIT fee of 0.25%/yr is subtracted.
- SGOV: annual-average 3-month T-bill yield minus a 0.09%/yr fee.
- Signals and trades both happen at the daily close (the real runs trade at
  15:45 ET). Every trade costs 0.05% of the amount traded. No taxes.
- The 5% and 10% halts use close-to-close moves; the real rule also checks
  against the day's open.

## SPY sleeve alone, 2000 to 2026

| Rules | Yearly return | Worst drop | Worst year | Trades/yr | Time invested |
|---|---|---|---|---|---|
| Buy and hold SPY | 8.5% | −55.4% | 2008: −37.3% | 0 | 100% |
| **Current: SMA200, ±1% band, daily** | **8.1%** | **−21.2%** | 2022: −11.9% | 2.9 | 71% |
| No band | 7.2% | −19.8% | 2022: −14.4% | 6.6 | 72% |
| ±2% band | 8.2% | −19.7% | 2022: −15.0% | 1.8 | 71% |
| Monthly check, no band | 9.4% | −24.3% | 2022: −20.1% | 1.3 | 72% |
| Current + volatility target 16% | 7.4% | −15.6% | 2022: −10.9% | 8.9 | 68% |
| Current + volatility target 20% | 7.8% | −18.7% | 2022: −11.1% | 5.0 | 70% |
| Current, halts allow sells | 8.1% | −21.2% | 2022: −11.9% | 2.9 | 71% |

The trend filter gave up about 0.4 points a year against buy-and-hold and cut
the worst drop from −55% to −21%. The band width barely matters between 1% and
2%, which suggests the result isn't fragile to that setting.

## Bitcoin sleeve alone, 2015 to 2026

| Rules | Yearly return | Worst drop | Worst year | Trades/yr | Time invested |
|---|---|---|---|---|---|
| Buy and hold | 58.4% | −82.9% | 2018: −74.4% | 0 | 100% |
| **Current: SMA200, ±3% band** | **64.7%** | **−63.5%** | 2018: −49.9% | 2.2 | 65% |
| ±1% band | 61.0% | −64.2% | 2018: −50.9% | 3.9 | 65% |
| ±5% band | 58.1% | −66.8% | 2018: −54.4% | 1.7 | 65% |
| Current + volatility target 60% | 53.5% | −56.9% | 2018: −34.4% | 12.8 | 56% |
| Current + volatility target 50% | 46.3% | −50.3% | 2018: −28.8% | 14.7 | 50% |

Bitcoin's 2015–2026 run was exceptional and is unlikely to repeat at that
pace. Even with the filter, the sleeve fell 63% at its worst.

## Whole account (80% SPY sleeve + 20% bitcoin sleeve), 2016 to 2026

| Rules | Yearly return | Worst drop | Worst year | Trades/yr |
|---|---|---|---|---|
| Buy and hold 80/20, rebalanced | 28.2% | −35.6% | 2022: −29.0% | 0 |
| Hold 100% SPY | 15.3% | −34.0% | 2022: −18.3% | 0 |
| **Current rules** | **23.7%** | **−22.9%** | 2018: −12.5% | 10.6 |
| + volatility scaling 20% / 60% | 20.1% | −21.5% | 2018: −11.1% | 16.6 |
| + volatility scaling 16% / 50% | 18.9% | −19.5% | 2022: −10.0% | 22.2 |

## Decisions

- **Kept:** both trend filters and bands as they are.
- **Not adopted: volatility scaling.** For the whole account it cost 3.6–4.8
  points a year to make the worst drop only 1.4–3.4 points smaller, with more
  trades. The trend filters already do most of the loss prevention.
- **Adopted: halts allow risk-reducing sells.** It changed nothing in this
  history, but it closes a real gap: before, a crash day could block the sell
  the trend rule called for.
