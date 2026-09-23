import math, statistics as st
from backtest import load_spy, load_btc, TBILL, SGOV_FEE, IBIT_FEE, COST, divy, stats, fmt, HDR

spy = dict(load_spy()); btc = dict(load_btc())
days = sorted(d for d in spy if d in btc)
sp = [spy[d] for d in days]; bt = [btc[d] for d in days]

def expo(px, i, band, on_prev, vt, n=20, step=.25):
    sma = sum(px[i-199:i+1])/200; dev = px[i]/sma-1
    on = True if dev > band else False if dev < -band else on_prev
    if not on: return on, 0.0
    if not vt: return on, 1.0
    r = [math.log(px[j]/px[j-1]) for j in range(i-n+1, i+1)]
    v = st.pstdev(r)*math.sqrt(252); m = min(1, vt/v) if v else 1
    return on, math.floor(m/step)*step

def run(vt_spy=None, vt_btc=None, w_spy=.8, w_btc=.2, start="2016-01-01", thr=.05):
    eq=1.0; ws=wb=0.0; on_s=on_b=False; curve=[]; trades=0; inv=0
    for i in range(220, len(days)):
        y=int(days[i][:4]); cash=TBILL.get(y,2)/100/252-SGOV_FEE/252
        rs=sp[i]/sp[i-1]-1+divy(y)/100/252; rb=bt[i]/bt[i-1]-1-IBIT_FEE/252
        if days[i]>=start:
            eq*=1+ws*rs+wb*rb+(1-ws-wb)*cash; curve.append((days[i],eq)); inv+=ws+wb
        # drift
        tot=1+ws*rs+wb*rb+(1-ws-wb)*cash; ws=ws*(1+rs)/tot; wb=wb*(1+rb)/tot
        on_s,es=expo(sp,i,.01,on_s,vt_spy); on_b,eb=expo(bt,i,.03,on_b,vt_btc)
        ts, tb = w_spy*es, w_btc*eb
        for cur,tgt,k in ((ws,ts,'s'),(wb,tb,'b')):
            if (tgt==0 and cur>0) or abs(tgt-cur)>thr:
                if days[i]>=start: eq*=1-COST*abs(tgt-cur); trades+=1
                if k=='s': ws=tgt
                else: wb=tgt
    return stats(curve,trades,inv)

def hold(w_spy=.8,w_btc=.2,start="2016-01-01"):
    eq=1.0; curve=[]; ws,wb=w_spy,w_btc
    for i in range(220,len(days)):
        y=int(days[i][:4]); rs=sp[i]/sp[i-1]-1+divy(y)/100/252; rb=bt[i]/bt[i-1]-1-IBIT_FEE/252
        if days[i]>=start: eq*=1+ws*rs+wb*rb; curve.append((days[i],eq))
        tot=1+ws*rs+wb*rb; ws=ws*(1+rs)/tot; wb=wb*(1+rb)/tot
        if abs(ws-w_spy)>.05: ws,wb=w_spy,w_btc
    return stats(curve,0,len(curve))

print(f"=== Whole account, 80% SPY sleeve + 20% bitcoin sleeve, {days[220] if days[220]>'2016' else '2016-01-01'} to now ===\n"+HDR)
rows=[("Buy and hold 80/20, rebalanced",hold()),
      ("Hold 100% SPY",hold(1.0,0.0)),
      ("Current rules",run()),
      ("Current + vol 20% SPY / 60% BTC",run(.20,.60)),
      ("Current + vol 16% SPY / 50% BTC",run(.16,.50)),
      ("Current + vol 20% SPY / 80% BTC",run(.20,.80))]
for n,s in rows: print(fmt(n,s))
print("\nYear by year (current rules vs buy-and-hold 80/20 vs vol 20%/60%):")
a,b,c=rows[2][1]['years'],rows[0][1]['years'],rows[3][1]['years']
for y in sorted(a): print(f"  {y}: {a[y]*100:7.1f}%  {b[y]*100:7.1f}%  {c[y]*100:7.1f}%")
