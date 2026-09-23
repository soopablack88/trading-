"""Rough backtest of the autopilot rules. Daily closes, signal and trade at the close."""
# Inputs are the raw MCP tool results saved during the 2026-09-23 session
# (Robinhood get_equity_historicals for SPY, Alpha Vantage DIGITAL_CURRENCY_DAILY
# for BTC). Re-fetch them and point R and the file names at your copies to rerun.
import json, math, statistics as st
from datetime import date

R = "/root/.claude/projects/-home-user-trading-/d75d4a8f-5dac-5073-aef2-fdcd26a875a6/tool-results/"
RH = ["mcp-My_Connector-get_equity_historicals-1790139862971.txt", "mcp-My_Connector-get_equity_historicals-1790139863817.txt"]
BTC = "mcp-Alpha_Vantage_MCP_Server-DIGITAL_CURRENCY_DAILY-1790139887952.txt"

# Annual average 3-month T-bill yield (%), from Alpha Vantage monthly data.
TBILL = {1993:3.0,1994:4.3,1995:5.5,1996:5.0,1997:5.1,1998:4.8,1999:4.6,2000:5.9,2001:3.4,2002:1.6,2003:1.0,
         2004:1.4,2005:3.1,2006:4.8,2007:4.4,2008:1.4,2009:.15,2010:.14,2011:.05,2012:.09,2013:.06,2014:.03,
         2015:.05,2016:.32,2017:.93,2018:1.94,2019:2.06,2020:.37,2021:.05,2022:2.02,2023:5.1,2024:5.1,2025:4.1,2026:3.75}
# Approximate SPY dividend yield (%) by era; the price series is split-adjusted only.
def divy(y): return 1.5 if y<2000 else 1.6 if y<2009 else 2.0 if y<2013 else 1.9 if y<2020 else 1.4
COST = 0.0005      # per trade, spread + slippage
SGOV_FEE = 0.0009  # annual
IBIT_FEE = 0.0025  # annual

def load_spy():
    seen = {}
    for f in RH:
        for b in json.load(open(R+f))["data"]["results"][0]["bars"]:
            if b.get("interpolated"): continue
            seen[b["begins_at"][:10]] = float(b["close_price"])
    return sorted(seen.items())

def load_btc():
    rows = json.load(open(R+BTC))["result"].strip().split("\n")[1:]
    out = []
    for r in rows:
        t, o, h, l, c, v = r.strip().split(",")
        d = date.fromisoformat(t)
        if d.weekday() < 5 and d >= date(2013, 1, 1):   # weekdays only, like IBIT
            out.append((t, float(c)))
    return sorted(out)

def sim(series, band=0.01, sma_n=200, vol_target=None, vol_n=20, step=0.25, monthly=False,
        income=lambda y: 0.0, fee=0.0, halt=None, halt_sells=False, start=None):
    """Returns dict of daily equity values and stats. Off position earns T-bill minus SGOV fee."""
    px = [p for _, p in series]; ds = [d for d, _ in series]
    eq, w, trades = 1.0, 0.0, 0
    curve, in_mkt = [], 0
    first = max(sma_n, vol_n + 1)
    for i in range(first, len(px)):
        y = int(ds[i][:4])
        # return from yesterday's close to today's close at yesterday's weight
        r_asset = px[i]/px[i-1] - 1 + income(y)/100/252 - fee/252
        r_cash = TBILL.get(y, 2.0)/100/252 - SGOV_FEE/252
        if start is None or ds[i] >= start:
            eq *= 1 + w*r_asset + (1-w)*r_cash
            curve.append((ds[i], eq)); in_mkt += w
        # decide at today's close
        sma = sum(px[i-sma_n+1:i+1]) / sma_n
        dev = px[i]/sma - 1
        on_prev = w > 0
        if monthly and ds[i][:7] == (ds[i+1][:7] if i+1 < len(ds) else "x"): continue
        on = True if dev > band else False if dev < -band else on_prev
        tgt = 1.0 if on else 0.0
        if on and vol_target:
            rets = [math.log(px[j]/px[j-1]) for j in range(i-vol_n+1, i+1)]
            vol = st.pstdev(rets) * math.sqrt(252)
            m = min(1.0, vol_target/vol) if vol > 0 else 1.0
            tgt = math.floor(m/step)*step if step else m
        if halt is not None:
            move = abs(px[i]/px[i-1] - 1)
            if move > halt:
                if not (halt_sells and tgt < w): continue   # blocked; keep yesterday's weight
        if abs(tgt - w) > 0.05 or (tgt == 0 and w > 0):
            if start is None or ds[i] >= start:
                eq *= 1 - COST*abs(tgt-w); trades += 1
            w = tgt
    return stats(curve, trades, in_mkt)

def stats(curve, trades, in_mkt):
    v = [e for _, e in curve]; n = len(v); yrs = n/252
    cagr = (v[-1]/v[0])**(1/yrs) - 1
    peak, mdd = v[0], 0
    for e in v:
        peak = max(peak, e); mdd = min(mdd, e/peak - 1)
    rets = [v[i]/v[i-1]-1 for i in range(1, n)]
    vol = st.pstdev(rets)*math.sqrt(252)
    years = {}
    for d, e in curve: years.setdefault(d[:4], []).append(e)
    ks = sorted(years); yr = []
    prev = v[0]
    for k in ks:
        yr.append((k, years[k][-1]/prev - 1)); prev = years[k][-1]
    worst = min(yr, key=lambda x: x[1])
    return dict(start=curve[0][0], end=curve[-1][0], cagr=cagr, mdd=mdd, vol=vol,
                ratio=cagr/abs(mdd) if mdd else 0, worst=worst, trades_yr=trades/yrs, in_mkt=in_mkt/n,
                years=dict(yr), curve=curve)

def fmt(name, s):
    return (f"{name:<34} {s['cagr']*100:6.2f}% {s['mdd']*100:7.1f}% {s['vol']*100:6.1f}% "
            f"{s['worst'][0]} {s['worst'][1]*100:6.1f}%  {s['trades_yr']:5.1f}  {s['in_mkt']*100:4.0f}%")

HDR = f"{'strategy':<34} {'CAGR':>7} {'max DD':>8} {'vol':>7} {'worst year':>15}  {'tr/yr':>5}  {'inv':>4}"

if __name__ == "__main__":
    spy = load_spy(); btc = load_btc()
    inc = divy
    S0 = "2000-01-01"
    print(f"SPY daily bars: {len(spy)} ({spy[0][0]} to {spy[-1][0]}); BTC weekday bars: {len(btc)}")
    print("\n=== SPY sleeve, 2000 to now (first 200 days warm up the average) ===\n" + HDR)
    res = {}
    # buy-and-hold: weight 1 always
    def hold(series, income=lambda y:0, fee=0.0, start=None):
        eq=1.0; curve=[]; px=[p for _,p in series]; ds=[d for d,_ in series]
        for i in range(200, len(px)):
            y=int(ds[i][:4]); eq*=1+px[i]/px[i-1]-1+income(y)/100/252-fee/252
            if start is None or ds[i]>=start: curve.append((ds[i],eq))
        return stats(curve, 0, len(curve))
    res["hold"] = hold(spy, inc, start=S0)
    rows = [
        ("Buy and hold SPY", res["hold"]),
        ("Current: SMA200 ±1%, daily", sim(spy, 0.01, income=inc, start=S0)),
        ("No band (0%)", sim(spy, 0.0, income=inc, start=S0)),
        ("Band ±2%", sim(spy, 0.02, income=inc, start=S0)),
        ("Monthly check, no band", sim(spy, 0.0, income=inc, monthly=True, start=S0)),
        ("Current + vol target 16%", sim(spy, 0.01, income=inc, vol_target=.16, start=S0)),
        ("Current + vol target 20%", sim(spy, 0.01, income=inc, vol_target=.20, start=S0)),
        ("Current, 5% halt blocks all", sim(spy, 0.01, income=inc, halt=.05, start=S0)),
        ("Current, 5% halt allows sells", sim(spy, 0.01, income=inc, halt=.05, halt_sells=True, start=S0)),
    ]
    for n, s in rows: print(fmt(n, s))
    S1 = "2015-01-01"
    print(f"\n=== Bitcoin sleeve (BTC weekday closes as IBIT stand-in), 2015 to now ===\n" + HDR)
    brows = [
        ("Buy and hold BTC", hold(btc, fee=IBIT_FEE, start=S1)),
        ("Current: SMA200 ±3%", sim(btc, 0.03, fee=IBIT_FEE, start=S1)),
        ("Band ±1%", sim(btc, 0.01, fee=IBIT_FEE, start=S1)),
        ("Band ±5%", sim(btc, 0.05, fee=IBIT_FEE, start=S1)),
        ("Current + vol target 60%", sim(btc, 0.03, fee=IBIT_FEE, vol_target=.60, start=S1)),
        ("Current + vol target 50%", sim(btc, 0.03, fee=IBIT_FEE, vol_target=.50, start=S1)),
        ("Current, 10% halt allows sells", sim(btc, 0.03, fee=IBIT_FEE, halt=.10, halt_sells=True, start=S1)),
    ]
    for n, s in brows: print(fmt(n, s))
    json.dump({"spy": {n: {k: v for k, v in s.items() if k != "curve"} for n, s in rows},
               "btc": {n: {k: v for k, v in s.items() if k != "curve"} for n, s in brows}},
              open("bt_sleeves.json", "w"), default=str)
