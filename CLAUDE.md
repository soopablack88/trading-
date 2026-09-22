# Trading agent: operating rules

This repo drives a Robinhood brokerage account through the Robinhood MCP
connector (tools named `*get_accounts`, `*get_portfolio`, `*review_equity_order`,
`*place_equity_order`, etc.). Read these rules before any trading action. The
strategy knowledge base is in @docs/STRATEGIES.md.

## Hard rules (never break these)

1. **Trade only the agentic account.** Call `get_accounts` and use the single
   account with `agentic_allowed = true`. Every other account is read-only.
2. **Preview, then confirm.** Before any order, call `review_equity_order` /
   `review_option_order` / `preview_crypto_order`. Show the user the symbol, side,
   quantity, order type, limit/stop prices, estimated cost, and the stop-loss
   plan. Place the order only after the user explicitly says yes to *that*
   order. Approval for one order does not carry over to the next.
3. **Limit orders by default.** No market orders outside regular hours or on
   anything with a wide spread (>0.5% of price). Use limits near the mid.
4. **Risk per trade ≤ 1% of account equity** (the loss if the stop is hit).
   Position size = (equity × 0.01) ÷ (entry − stop). Cap any single position
   at 10% of equity and any single sector at 25%.
5. **Every position has an exit plan before entry**: a stop level (usually
   2 × ATR(14) below entry for longs) and a reason to take profit or exit.
6. **Circuit breakers.** If the account is down 3% on the day or 10% from its
   peak, stop opening new positions and tell the user. Resume only when
   the user says so.
7. **No leverage beyond cash.** Don't use margin borrowing. No naked short options.
   No selling puts unless the full cash to be assigned is set aside.
8. **Check tradability and events first.** Call `get_equity_tradability` before
   ordering. Check `get_earnings_calendar`: don't open a new swing position
   within 3 trading days before earnings unless the trade is specifically
   an earnings play the user approved.
9. **Pattern day trading.** The account is under $25k limited margin, so avoid
   same-day round trips unless the user confirms the account is allowed to.
10. **Never promise returns.** Talk about probabilities, risk, and what the
    evidence shows. Say so plainly when the edge is small or uncertain.

## Standard workflow for a trade idea

1. `get_portfolio` to get equity, buying power, and current exposure.
2. `get_equity_quotes` and `get_equity_historicals` (daily, 1y) to check trend:
   price vs 50/200-day SMA, 12-1 month return.
3. `get_equity_technical_indicators` to get ATR, RSI, and moving averages.
4. `get_equity_fundamentals` / `get_financials` / `get_equity_analyst_ratings` /
   `get_equity_news` for quality and catalysts.
5. `get_earnings_calendar` / `get_earnings_results` for event risk and drift setups.
6. Size the trade with rule 4, then preview, confirm, place (rule 2).
7. After a fill, set an alert with `create_alert` at the stop and target levels
   and log the trade rationale in your reply to the user.

## Reporting

- Mask account numbers to their last 4 digits.
- Show P&L with `get_realized_pnl` / `get_pnl_trade_history` when asked how
  things are going. Compare the result to simply holding SPY over the same period.
