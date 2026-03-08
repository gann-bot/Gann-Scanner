#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║         WD GANN STOCK SCANNER v2.0                       ║
║   Real-time NSE Prices + 9 Mathematical Proofs           ║
║                                                          ║
║  HOW TO RUN:                                             ║
║  1. pip install yfinance pandas requests                 ║
║  2. python gann_scanner.py                               ║
║  3. Browser mein automatically khulega!                  ║
╚══════════════════════════════════════════════════════════╝
"""

import math
import json
import webbrowser
import os
import sys
import datetime
from pathlib import Path

# ─── Auto install required packages ───────────────────────
def install_packages():
    import subprocess
    pkgs = ["yfinance", "pandas", "requests"]
    for pkg in pkgs:
        try:
            __import__(pkg)
        except ImportError:
            print(f"  Installing {pkg}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

print("=" * 60)
print("  WD GANN STOCK SCANNER v2.0")
print("  Based on Original WD Gann Methodology")
print("=" * 60)
print("\n  Checking packages...")
install_packages()

import yfinance as yf
import pandas as pd
import requests

# ═══════════════════════════════════════════════════════════
# 20 NSE STOCKS — Edit this list as per your choice
# ═══════════════════════════════════════════════════════════
STOCKS = [
    "RELIANCE.NS",
    "TCS.NS",
    "HDFCBANK.NS",
    "INFY.NS",
    "ICICIBANK.NS",
    "WIPRO.NS",
    "SBIN.NS",
    "BAJFINANCE.NS",
    "TATASTEEL.NS",
    "ONGC.NS",
    "MARUTI.NS",
    "ADANIENT.NS",
    "POWERGRID.NS",
    "NTPC.NS",
    "HCLTECH.NS",
    "AXISBANK.NS",
    "SUNPHARMA.NS",
    "BHARTIARTL.NS",
    "LT.NS",
    "TITAN.NS",
]

# ═══════════════════════════════════════════════════════════
# FETCH REAL-TIME PRICES
# ═══════════════════════════════════════════════════════════
def fetch_prices(symbols):
    print(f"\n  Fetching real-time prices for {len(symbols)} stocks...")
    results = {}

    for sym in symbols:
        try:
            ticker = yf.Ticker(sym)
            hist   = ticker.history(period="5d", interval="1d")

            if hist.empty or len(hist) < 2:
                print(f"  ⚠  {sym}: No data — skipping")
                continue

            ltp      = round(float(hist['Close'].iloc[-1]), 2)
            prev     = round(float(hist['Close'].iloc[-2]), 2)
            high_52w = round(float(hist['High'].max()), 2)
            low_52w  = round(float(hist['Low'].min()),  2)
            vol      = int(hist['Volume'].iloc[-1])
            vol_avg  = int(hist['Volume'].mean())
            day_high = round(float(hist['High'].iloc[-1]),  2)
            day_low  = round(float(hist['Low'].iloc[-1]),   2)

            # Get 1-year data for 52-week range
            try:
                hist_1y   = ticker.history(period="1y", interval="1d")
                high_52w  = round(float(hist_1y['High'].max()), 2)
                low_52w   = round(float(hist_1y['Low'].min()),  2)
                vol_avg   = int(hist_1y['Volume'].mean())
                # Consecutive days
                closes    = hist_1y['Close'].tolist()
                consec_up = 0
                consec_dn = 0
                for k in range(len(closes)-1, 0, -1):
                    if closes[k] > closes[k-1]:
                        if consec_dn > 0: break
                        consec_up += 1
                    elif closes[k] < closes[k-1]:
                        if consec_up > 0: break
                        consec_dn += 1
                    else:
                        break
            except:
                consec_up = 1 if ltp > prev else 0
                consec_dn = 1 if ltp < prev else 0

            clean_sym = sym.replace(".NS", "")
            results[clean_sym] = {
                "sym":      clean_sym,
                "ltp":      ltp,
                "prev":     prev,
                "high_52w": high_52w,
                "low_52w":  low_52w,
                "day_high": day_high,
                "day_low":  day_low,
                "volume":   vol,
                "vol_avg":  vol_avg,
                "consec_up": consec_up,
                "consec_dn": consec_dn,
            }
            chg = round(((ltp - prev) / prev) * 100, 2)
            arrow = "▲" if chg >= 0 else "▼"
            print(f"  ✔  {clean_sym:<15} ₹{ltp:<10} {arrow}{abs(chg)}%")

        except Exception as e:
            print(f"  ✗  {sym}: Error — {e}")

    print(f"\n  ✔ Fetched {len(results)}/{len(symbols)} stocks successfully")
    return results

# ═══════════════════════════════════════════════════════════
# WD GANN — SQUARE OF 9
# ═══════════════════════════════════════════════════════════
def sq9_up(base, n):
    return round((math.sqrt(base) + n * 0.125) ** 2, 2)

def sq9_dn(base, n):
    val = math.sqrt(base) - n * 0.125
    if val <= 0: return 0.01
    return round(val ** 2, 2)

# ═══════════════════════════════════════════════════════════
# WD GANN — 9 PROOFS ENGINE
# ═══════════════════════════════════════════════════════════
def analyze_stock(data):
    sym      = data["sym"]
    ltp      = data["ltp"]
    prev     = data["prev"]
    high_52w = data["high_52w"]
    low_52w  = data["low_52w"]
    day_high = data["day_high"]
    day_low  = data["day_low"]
    volume   = data["volume"]
    vol_avg  = data["vol_avg"]
    consec_up= data["consec_up"]
    consec_dn= data["consec_dn"]

    chg     = round(((ltp - prev) / prev) * 100, 2)
    atr     = round(ltp * 0.012, 2)   # approx 1.2% as ATR
    tol     = atr * 0.8

    # ── Square of 9 levels ────────────────────────────────
    b1 = sq9_up(prev, 1);  b2 = sq9_up(prev, 3);  b3 = sq9_up(prev, 5)
    b4 = sq9_up(prev, 7);  b5 = sq9_up(prev, 9);  b6 = sq9_up(prev, 11)
    s1 = sq9_dn(prev, 1);  s2 = sq9_dn(prev, 3);  s3 = sq9_dn(prev, 5)
    s4 = sq9_dn(prev, 7);  s5 = sq9_dn(prev, 9);  s6 = sq9_dn(prev, 11)

    near_bull_sq9 = (abs(ltp - b1) <= tol or abs(ltp - b2) <= tol or abs(ltp - b3) <= tol)
    near_bear_sq9 = (abs(ltp - s1) <= tol or abs(ltp - s2) <= tol or abs(ltp - s3) <= tol)

    # ── Gann Angles ───────────────────────────────────────
    scale     = atr / 5.0
    up_1x1   = round(prev + scale * 1.0, 2)
    up_2x1   = round(prev + scale * 2.0, 2)
    up_1x2   = round(prev + scale * 0.5, 2)
    dn_1x1   = round(prev - scale * 1.0, 2)
    dn_2x1   = round(prev - scale * 2.0, 2)
    dn_1x2   = round(prev - scale * 0.5, 2)
    at_angle_bull = (abs(ltp - up_1x1) <= atr * 0.7 or
                     abs(ltp - up_2x1) <= atr * 0.7 or
                     abs(ltp - up_1x2) <= atr * 0.7)
    at_angle_bear = (abs(ltp - dn_1x1) <= atr * 0.7 or
                     abs(ltp - dn_2x1) <= atr * 0.7 or
                     abs(ltp - dn_1x2) <= atr * 0.7)

    # ── 50% Centre of Gravity ─────────────────────────────
    cog_50 = round((high_52w + low_52w) / 2, 2)
    cog_25 = round(low_52w  + (high_52w - low_52w) * 0.25, 2)
    cog_75 = round(low_52w  + (high_52w - low_52w) * 0.75, 2)
    near_50_bull = abs(ltp - cog_50) <= atr * 2.0 and ltp > cog_50
    near_50_bear = abs(ltp - cog_50) <= atr * 2.0 and ltp < cog_50

    # ── Time Cycles (days from Jan 1 this year) ───────────
    doy    = datetime.datetime.now().timetuple().tm_yday
    cycles = [30, 45, 60, 90, 135, 180, 270, 360]
    tc_active = False
    tc_cycle  = None
    for c in cycles:
        if doy % c <= 3 or doy % c >= c - 3:
            tc_active = True
            tc_cycle  = c
            break
    tc_bull = tc_active and ltp > prev
    tc_bear = tc_active and ltp < prev

    # ── Higher Bottom / Lower Top ─────────────────────────
    is_hb = ltp > prev and chg >  0.25
    is_lt = ltp < prev and chg < -0.25

    # ── Volume Spike ──────────────────────────────────────
    vol_ratio  = volume / vol_avg if vol_avg > 0 else 1.0
    vol_spike  = vol_ratio >= 1.8
    vol_bull   = vol_spike and ltp > prev
    vol_bear   = vol_spike and ltp < prev

    # ── Weekly Rule (Gann) ────────────────────────────────
    dow         = datetime.datetime.now().weekday()  # 0=Mon, 4=Fri
    is_friday   = dow == 4
    is_tuesday  = dow == 1
    week_bull   = (is_friday and ltp > prev) or (is_tuesday and ltp > prev and is_hb)
    week_bear   = is_friday and ltp < prev

    # ── 9:5 Ratio (consecutive days) ─────────────────────
    ratio_bull = consec_dn >= 5    # 5+ down days → rally likely
    ratio_bear = consec_up >= 9    # 9+ up days   → correction likely
    # Also: price near sq9 buy/sell after 5-day move
    near_sq9_after_move = (abs(ltp - b1) <= tol * 1.5 and consec_up >= 3)
    ratio_bull = ratio_bull or (consec_dn >= 3 and abs(ltp - s1) <= tol * 1.5)

    # ── Double Bottom / Top ───────────────────────────────
    tol_dbl = atr * 2.5
    dbl_bot = abs(day_low  - low_52w)  <= tol_dbl and ltp > prev
    dbl_top = abs(day_high - high_52w) <= tol_dbl and ltp < prev

    # ── 3rd Day Warning ───────────────────────────────────
    third_day_warn = (consec_up == 3 or consec_dn == 3)

    # ─── 9 PROOFS ─────────────────────────────────────────
    proofs_bull = [
        {"name": "1. Sq9 Level",     "active": near_bull_sq9 and ltp > prev, "desc": f"Near Sq9 Buy Level ₹{b1}"},
        {"name": "2. Gann Angle",    "active": at_angle_bull,                 "desc": f"At 1×1/2×1 Angle ₹{up_1x1}"},
        {"name": "3. 50% CoG",       "active": near_50_bull,                  "desc": f"Above 50% CoG ₹{cog_50}"},
        {"name": "4. Time Cycle",    "active": tc_bull,                        "desc": f"Cycle {tc_cycle}d Active" if tc_cycle else "Not active"},
        {"name": "5. Higher Bottom", "active": is_hb,                          "desc": f"LTP > Prev (+{chg}%)"},
        {"name": "6. Volume Spike",  "active": vol_bull,                       "desc": f"Vol {vol_ratio:.1f}x avg"},
        {"name": "7. Weekly Rule",   "active": week_bull,                      "desc": "Fri High / Tue Low Rule"},
        {"name": "8. 9:5 Ratio",     "active": ratio_bull,                     "desc": f"{consec_dn} consec down days"},
        {"name": "9. Dbl Bottom",    "active": dbl_bot,                        "desc": f"Near 52w Low ₹{low_52w}"},
    ]
    proofs_bear = [
        {"name": "1. Sq9 Level",     "active": near_bear_sq9 and ltp < prev, "desc": f"Near Sq9 Sell ₹{s1}"},
        {"name": "2. Gann Angle",    "active": at_angle_bear,                 "desc": f"At ↓1×1 Angle ₹{dn_1x1}"},
        {"name": "3. 50% CoG",       "active": near_50_bear,                  "desc": f"Below 50% CoG ₹{cog_50}"},
        {"name": "4. Time Cycle",    "active": tc_bear,                        "desc": f"Cycle {tc_cycle}d Active" if tc_cycle else "Not active"},
        {"name": "5. Lower Top",     "active": is_lt,                          "desc": f"LTP < Prev ({chg}%)"},
        {"name": "6. Volume Spike",  "active": vol_bear,                       "desc": f"Vol {vol_ratio:.1f}x avg"},
        {"name": "7. Weekly Rule",   "active": week_bear,                      "desc": "Friday Low Rule"},
        {"name": "8. 9:5 Ratio",     "active": ratio_bear,                     "desc": f"{consec_up} consec up days"},
        {"name": "9. Dbl Top",       "active": dbl_top,                        "desc": f"Near 52w High ₹{high_52w}"},
    ]

    bull_score = sum(1 for p in proofs_bull if p["active"])
    bear_score = sum(1 for p in proofs_bear if p["active"])

    if   bull_score >= 3:               signal = "BUY"
    elif bear_score >= 3:               signal = "SELL"
    elif bull_score >= 1 or bear_score >= 1: signal = "WATCH"
    else:                               signal = "NEUTRAL"

    # Targets
    t1_buy  = sq9_up(ltp, 3);   t2_buy  = sq9_up(ltp, 5);  t3_buy  = sq9_up(ltp, 9)
    t1_sell = sq9_dn(ltp, 3);   t2_sell = sq9_dn(ltp, 5);  t3_sell = sq9_dn(ltp, 9)
    sl_buy  = round(ltp * 0.985, 2)
    sl_sell = round(ltp * 1.015, 2)
    rr_buy  = round((t1_buy  - ltp) / (ltp - sl_buy),  2) if (ltp - sl_buy)  > 0 else 0
    rr_sell = round((ltp - t1_sell) / (sl_sell - ltp),  2) if (sl_sell - ltp) > 0 else 0

    return {
        "sym": sym, "ltp": ltp, "prev": prev, "chg": chg,
        "high_52w": high_52w, "low_52w": low_52w,
        "day_high": day_high, "day_low": day_low,
        "volume": volume, "vol_avg": vol_avg, "vol_ratio": round(vol_ratio, 1),
        "signal": signal, "bull_score": bull_score, "bear_score": bear_score,
        "proofs_bull": proofs_bull, "proofs_bear": proofs_bear,
        "b1": b1, "b2": b2, "b3": b3, "b4": b4, "b5": b5, "b6": b6,
        "s1": s1, "s2": s2, "s3": s3, "s4": s4, "s5": s5, "s6": s6,
        "cog_50": cog_50, "cog_25": cog_25, "cog_75": cog_75,
        "up_1x1": up_1x1, "up_2x1": up_2x1, "dn_1x1": dn_1x1,
        "tc_active": tc_active, "tc_cycle": tc_cycle,
        "t1_buy": t1_buy, "t2_buy": t2_buy, "t3_buy": t3_buy,
        "t1_sell": t1_sell, "t2_sell": t2_sell, "t3_sell": t3_sell,
        "sl_buy": sl_buy, "sl_sell": sl_sell,
        "rr_buy": rr_buy, "rr_sell": rr_sell,
        "consec_up": consec_up, "consec_dn": consec_dn,
        "third_day_warn": third_day_warn,
    }

# ═══════════════════════════════════════════════════════════
# GENERATE HTML DASHBOARD
# ═══════════════════════════════════════════════════════════
def generate_html(analyzed, scan_time):
    # Sort: BUY first, then SELL, then WATCH, then NEUTRAL; within each by score
    order = {"BUY": 0, "SELL": 1, "WATCH": 2, "NEUTRAL": 3}
    analyzed.sort(key=lambda x: (order.get(x["signal"], 3), -x["bull_score"]))

    data_json = json.dumps(analyzed)

    # Summary counts
    buys    = [r for r in analyzed if r["signal"] == "BUY"]
    sells   = [r for r in analyzed if r["signal"] == "SELL"]
    watches = [r for r in analyzed if r["signal"] == "WATCH"]
    neutral = [r for r in analyzed if r["signal"] == "NEUTRAL"]

    def fmt(n):
        return f"₹{n:,.2f}"

    def sig_badge(s):
        cls = {"BUY":"sig-buy","SELL":"sig-sell","WATCH":"sig-watch","NEUTRAL":"sig-neutral"}
        return f'<span class="{cls.get(s,"sig-neutral")}">{s}</span>'

    def tick(v):
        return '<span class="tick">✔</span>' if v else '<span class="cross">✗</span>'

    def score_col(sc, kind):
        if kind == "bull":
            return ("#00e676" if sc >= 3 else "#ff9800" if sc >= 1 else "#2a4060")
        return ("#ff1744" if sc >= 3 else "#ff9800" if sc >= 1 else "#2a4060")

    # Build table rows
    table_rows = ""
    for i, r in enumerate(analyzed):
        chg_col   = "#00e676" if r["chg"] >= 0 else "#ff1744"
        chg_arrow = "▲" if r["chg"] >= 0 else "▼"
        bull_chips = "".join(
            f'<span class="chip chip-bull">{p["name"].split(".")[1].strip()}</span>'
            for p in r["proofs_bull"] if p["active"]
        )
        bear_chips = "".join(
            f'<span class="chip chip-bear">{p["name"].split(".")[1].strip()}</span>'
            for p in r["proofs_bear"] if p["active"]
        )
        chips = bull_chips + bear_chips or '<span class="chip">—</span>'
        tc_badge = f'<span class="tc-badge">⏰{r["tc_cycle"]}d</span>' if r["tc_active"] else ""
        warn     = '<span class="warn-badge">⚠3rd</span>'  if r["third_day_warn"] else ""
        t1 = fmt(r["t1_buy"])  if r["signal"] in ("BUY","WATCH")  else fmt(r["t1_sell"])
        sl = fmt(r["sl_buy"])  if r["signal"] in ("BUY","WATCH")  else fmt(r["sl_sell"])
        rr = r["rr_buy"]       if r["signal"] in ("BUY","WATCH")  else r["rr_sell"]

        table_rows += f"""
        <tr onclick="toggleCard('{r['sym']}')" style="cursor:pointer">
          <td style="color:#4a6080;font-size:0.72rem">{i+1}</td>
          <td class="td-name">{r['sym']}{tc_badge}{warn}</td>
          <td class="td-price">{fmt(r['ltp'])}</td>
          <td style="color:{chg_col}">{chg_arrow}{abs(r['chg']):.2f}%</td>
          <td>{sig_badge(r['signal'])}</td>
          <td style="color:{score_col(r['bull_score'],'bull')};font-weight:bold">{r['bull_score']}/9</td>
          <td style="color:{score_col(r['bear_score'],'bear')};font-weight:bold">{r['bear_score']}/9</td>
          <td style="color:#00e676">{fmt(r['b1'])}</td>
          <td style="color:#ff1744">{fmt(r['s1'])}</td>
          <td style="color:#ffd700">{fmt(r['cog_50'])}</td>
          <td style="color:#00e5ff">{t1}</td>
          <td style="color:#ff9800">{sl}</td>
          <td style="color:{'#00e676' if rr >= 2 else '#ff9800' if rr >= 1 else '#4a6080'}">{rr:.1f}x</td>
          <td><div class="chips">{chips}</div></td>
        </tr>"""

    # Build detail cards
    detail_cards = ""
    for r in analyzed:
        sig_color = {"BUY":"#00e676","SELL":"#ff1744","WATCH":"#ff9800","NEUTRAL":"#4a6080"}.get(r["signal"],"#4a6080")
        chg_color = "#00e676" if r["chg"] >= 0 else "#ff1744"

        proof_rows = ""
        for pb, ps in zip(r["proofs_bull"], r["proofs_bear"]):
            proof_rows += f"""
            <div class="proof-row">
              <span class="p-name">{pb['name']}</span>
              <span class="p-val">{tick(pb['active'])}</span>
              <span class="p-val">{tick(ps['active'])}</span>
              <span class="p-desc">{'✔ ' + pb['desc'] if pb['active'] else ps['desc'] if ps['active'] else '—'}</span>
            </div>"""

        setup_html = ""
        if r["signal"] == "BUY":
            setup_html = f"""
            <div class="setup-box setup-bull">
              <div class="setup-title">📈 BUY SETUP</div>
              <div>Entry: <b>{fmt(r['ltp'])}</b></div>
              <div>T1: <b style="color:#00e676">{fmt(r['t1_buy'])}</b> &nbsp; T2: <b style="color:#00e676">{fmt(r['t2_buy'])}</b></div>
              <div>T3: <b style="color:#00e676">{fmt(r['t3_buy'])}</b></div>
              <div>SL: <b style="color:#ff9800">{fmt(r['sl_buy'])}</b> &nbsp; R:R = <b style="color:#00e5ff">{r['rr_buy']:.1f}x</b></div>
            </div>"""
        elif r["signal"] == "SELL":
            setup_html = f"""
            <div class="setup-box setup-bear">
              <div class="setup-title">📉 SELL SETUP</div>
              <div>Entry: <b>{fmt(r['ltp'])}</b></div>
              <div>T1: <b style="color:#ff1744">{fmt(r['t1_sell'])}</b> &nbsp; T2: <b style="color:#ff1744">{fmt(r['t2_sell'])}</b></div>
              <div>T3: <b style="color:#ff1744">{fmt(r['t3_sell'])}</b></div>
              <div>SL: <b style="color:#ff9800">{fmt(r['sl_sell'])}</b> &nbsp; R:R = <b style="color:#00e5ff">{r['rr_sell']:.1f}x</b></div>
            </div>"""
        else:
            setup_html = f'<div class="setup-box" style="color:#2a4060">No strong signal — wait for Sq9 level or angle confluence</div>'

        detail_cards += f"""
        <div class="dcard" id="card-{r['sym']}" style="display:none">
          <div class="dcard-header">
            <div>
              <span class="dcard-sym">{r['sym']}</span>
              <span class="dcard-ex">NSE</span>
            </div>
            <div style="text-align:right">
              <span class="dcard-price">{fmt(r['ltp'])}</span>
              <span style="color:{chg_color};font-size:0.8rem;margin-left:6px">{'▲' if r['chg']>=0 else '▼'}{abs(r['chg']):.2f}%</span><br>
              <span style="color:{sig_color};font-weight:bold">{r['signal']}</span>
              <span style="color:#4a6080;font-size:0.7rem;margin-left:5px">B:{r['bull_score']} / S:{r['bear_score']}</span>
            </div>
          </div>
          <div class="dcard-body">
            <div class="dcard-col">
              <div class="dc-section">
                <div class="dc-title">📐 GANN Sq9 LEVELS</div>
                <div class="sq9-grid">
                  <div class="sq9-row" style="color:#00e67644">B3 (T3)&nbsp; {fmt(r['b3'])}</div>
                  <div class="sq9-row" style="color:#00e67677">B2 (T2)&nbsp; {fmt(r['b2'])}</div>
                  <div class="sq9-row" style="color:#00e676">B1 (T1)&nbsp; {fmt(r['b1'])}</div>
                  <div class="sq9-row ltp-row">► LTP &nbsp; {fmt(r['ltp'])}</div>
                  <div class="sq9-row" style="color:#ff1744">S1 (T1)&nbsp; {fmt(r['s1'])}</div>
                  <div class="sq9-row" style="color:#ff174477">S2 (T2)&nbsp; {fmt(r['s2'])}</div>
                  <div class="sq9-row" style="color:#ff174444">S3 (T3)&nbsp; {fmt(r['s3'])}</div>
                </div>
                <div class="cog-row">
                  CoG 50%: <b style="color:#ffd700">{fmt(r['cog_50'])}</b> &nbsp;
                  25%: <b style="color:#00e5ff">{fmt(r['cog_25'])}</b> &nbsp;
                  75%: <b style="color:#00e5ff">{fmt(r['cog_75'])}</b>
                </div>
                <div class="cog-row" style="margin-top:4px">
                  52W H: <b style="color:#00e676">{fmt(r['high_52w'])}</b> &nbsp;
                  52W L: <b style="color:#ff1744">{fmt(r['low_52w'])}</b> &nbsp;
                  Vol: <b style="color:{'#00e676' if r['vol_ratio']>=1.8 else '#7a8fa8'}">{r['vol_ratio']:.1f}x avg</b>
                </div>
              </div>
              {setup_html}
            </div>
            <div class="dcard-col">
              <div class="dc-section">
                <div class="dc-title">🔢 9 PROOFS &nbsp;<span style="font-size:0.65rem;color:#4a6080">BULL | BEAR | REASON</span></div>
                {proof_rows}
                <div class="score-row">
                  <span>Bull: <b style="color:{score_col(r['bull_score'],'bull')}">{r['bull_score']}/9</b></span>
                  <span>Bear: <b style="color:{score_col(r['bear_score'],'bear')}">{r['bear_score']}/9</b></span>
                  {'<span class="tc-badge">⏰ Time Cycle ' + str(r["tc_cycle"]) + 'd</span>' if r["tc_active"] else ''}
                  {'<span class="warn-badge">⚠ 3rd Day</span>' if r["third_day_warn"] else ''}
                </div>
              </div>
            </div>
          </div>
        </div>"""

    # Top picks cards
    top_buys_html  = ""
    top_sells_html = ""
    for r in buys[:5]:
        top_buys_html += f"""
        <div class="pick buy-pick">
          <div class="pick-sym">▲ {r['sym']}</div>
          <div class="pick-price">{fmt(r['ltp'])}</div>
          <div style="color:#00e676;font-size:0.72rem">BUY • {r['bull_score']}/9 proofs</div>
          <div class="pick-targets">
            T1: {fmt(r['t1_buy'])} &nbsp; T2: {fmt(r['t2_buy'])}<br>
            SL: <span style="color:#ff9800">{fmt(r['sl_buy'])}</span> &nbsp; R:R {r['rr_buy']:.1f}x
          </div>
        </div>"""
    for r in sells[:5]:
        top_sells_html += f"""
        <div class="pick sell-pick">
          <div class="pick-sym">▼ {r['sym']}</div>
          <div class="pick-price">{fmt(r['ltp'])}</div>
          <div style="color:#ff1744;font-size:0.72rem">SELL • {r['bear_score']}/9 proofs</div>
          <div class="pick-targets">
            T1: {fmt(r['t1_sell'])} &nbsp; T2: {fmt(r['t2_sell'])}<br>
            SL: <span style="color:#ff9800">{fmt(r['sl_sell'])}</span> &nbsp; R:R {r['rr_sell']:.1f}x
          </div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>WD Gann Scanner v2.0 — {scan_time}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#030812;color:#ccd6f6;font-family:'Segoe UI',monospace;padding:14px;min-height:100vh}}
.hdr{{background:linear-gradient(135deg,#0a1628,#0d1f3c,#0a1628);border:1px solid #1e3a5f;border-top:3px solid #ffd700;border-radius:10px;padding:16px 22px;display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}}
.hdr h1{{font-size:1.4rem;color:#ffd700;letter-spacing:2px}}
.hdr h1 span{{color:#00e5ff;font-size:0.82rem;display:block;letter-spacing:1px;margin-top:2px}}
.hdr-right{{text-align:right;font-size:0.75rem;color:#7a8fa8;line-height:1.7}}
.hdr-right b{{color:#ffd700}}
.summary{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px}}
.sum-card{{background:#0a1628;border:1px solid #1e3a5f;border-radius:8px;padding:12px 16px;text-align:center}}
.sum-num{{font-size:1.8rem;font-weight:bold;line-height:1}}
.sum-lbl{{font-size:0.72rem;color:#4a6080;margin-top:4px;letter-spacing:1px}}
.rules-box{{background:#060e1c;border:1px solid #1a2f50;border-left:3px solid #ffd700;border-radius:0 8px 8px 0;padding:10px 16px;margin-bottom:14px;font-size:0.73rem;color:#7a8fa8;line-height:1.8}}
.rules-box h3{{color:#ffd700;font-size:0.8rem;margin-bottom:6px;letter-spacing:1px}}
.rules-box b{{color:#00e5ff}}
.top-section{{background:#0a1628;border:1px solid #ffd70033;border-radius:10px;padding:14px 18px;margin-bottom:14px}}
.top-section h2{{color:#ffd700;font-size:0.9rem;margin-bottom:10px;letter-spacing:1px}}
.picks-row{{display:flex;gap:10px;flex-wrap:wrap}}
.pick{{border-radius:8px;padding:10px 14px;min-width:155px;font-size:0.75rem}}
.buy-pick{{background:#0a2015;border-top:3px solid #00e676}}
.sell-pick{{background:#1f0a0e;border-top:3px solid #ff1744}}
.pick-sym{{font-weight:bold;font-size:0.9rem;color:#ccd6f6}}
.pick-price{{color:#00e5ff;font-size:0.82rem;margin:2px 0}}
.pick-targets{{margin-top:6px;color:#7a8fa8;line-height:1.7}}
.tbl-wrap{{background:#0a1628;border:1px solid #1e3a5f;border-radius:10px;overflow:hidden;margin-bottom:14px}}
.tbl-wrap h2{{color:#ffd700;font-size:0.9rem;padding:11px 18px;background:#0d1f3c;border-bottom:1px solid #1e3a5f;letter-spacing:1px}}
.tbl-scroll{{overflow-x:auto}}
table{{width:100%;border-collapse:collapse;font-size:0.75rem}}
thead th{{background:#0d1f3c;color:#7a8fa8;padding:8px 9px;text-align:center;border-bottom:1px solid #1a2f50;font-size:0.67rem;letter-spacing:0.5px;white-space:nowrap}}
tbody tr:nth-child(even){{background:#0b1a2e}}
tbody tr:nth-child(odd){{background:#091422}}
tbody tr:hover{{background:#0f2340}}
tbody td{{padding:7px 9px;text-align:center;border-bottom:1px solid #0f1f35;vertical-align:middle}}
.td-name{{text-align:left;font-weight:bold;color:#ccd6f6;white-space:nowrap}}
.td-price{{color:#00e5ff;font-weight:bold}}
.sig-buy{{background:#00e676;color:#000;border-radius:4px;padding:2px 8px;font-weight:bold;font-size:0.75rem}}
.sig-sell{{background:#ff1744;color:#fff;border-radius:4px;padding:2px 8px;font-weight:bold;font-size:0.75rem}}
.sig-watch{{background:#ff9800;color:#000;border-radius:4px;padding:2px 8px;font-weight:bold;font-size:0.75rem}}
.sig-neutral{{background:#1e3a5f;color:#7a8fa8;border-radius:4px;padding:2px 8px;font-size:0.75rem}}
.chips{{display:flex;flex-wrap:wrap;gap:3px;justify-content:center}}
.chip{{font-size:0.6rem;padding:1px 5px;border-radius:3px;background:#1e3a5f;color:#4a6080}}
.chip-bull{{background:#003d1f;color:#00e676;border:1px solid #00e67633}}
.chip-bear{{background:#3d0011;color:#ff1744;border:1px solid #ff174433}}
.tc-badge{{display:inline-block;font-size:0.62rem;padding:1px 5px;border-radius:3px;background:#1a0d3d;color:#b44fff;border:1px solid #4a1f8055;margin-left:3px}}
.warn-badge{{display:inline-block;font-size:0.62rem;padding:1px 5px;border-radius:3px;background:#3d2000;color:#ff9800;border:1px solid #ff980055;margin-left:3px}}
.tick{{color:#00e676}}
.cross{{color:#1a3050}}
.legend{{display:flex;gap:16px;flex-wrap:wrap;margin-bottom:12px;background:#0a1628;border:1px solid #1e3a5f;border-radius:8px;padding:9px 16px;font-size:0.73rem}}
.leg{{display:flex;align-items:center;gap:6px}}
.leg-dot{{width:9px;height:9px;border-radius:50%}}
/* Detail Cards */
.dcard{{background:#0a1628;border:1px solid #1e3a5f;border-radius:10px;margin-bottom:12px;overflow:hidden}}
.dcard-header{{padding:10px 14px;display:flex;align-items:center;justify-content:space-between;background:#0d1f3c;border-bottom:1px solid #1a2f50}}
.dcard-sym{{font-weight:bold;font-size:0.92rem;color:#ccd6f6}}
.dcard-ex{{font-size:0.68rem;color:#4a6080;margin-left:6px}}
.dcard-price{{color:#00e5ff;font-size:0.85rem;font-weight:bold}}
.dcard-body{{display:grid;grid-template-columns:1fr 1fr;gap:0}}
@media(max-width:700px){{.dcard-body{{grid-template-columns:1fr}}}}
.dcard-col{{padding:12px 14px;border-right:1px solid #0d1f3c}}
.dcard-col:last-child{{border-right:none}}
.dc-section{{margin-bottom:12px}}
.dc-title{{color:#00e5ff;font-size:0.7rem;margin-bottom:8px;letter-spacing:1px}}
.sq9-grid{{margin-bottom:6px}}
.sq9-row{{font-size:0.75rem;padding:3px 0;border-bottom:1px solid #0d1f3c}}
.ltp-row{{color:#00e5ff;font-weight:bold;background:#001a2a;padding:4px 6px;border-radius:4px;margin:2px 0}}
.cog-row{{font-size:0.68rem;color:#4a6080;margin-top:4px}}
.proof-row{{display:flex;align-items:center;gap:8px;padding:4px 0;border-bottom:1px solid #0d1f3c;font-size:0.72rem}}
.p-name{{width:120px;color:#7a8fa8;font-size:0.68rem}}
.p-val{{width:24px;text-align:center}}
.p-desc{{flex:1;color:#4a6080;font-size:0.65rem}}
.score-row{{display:flex;gap:12px;margin-top:8px;font-size:0.75rem;flex-wrap:wrap}}
.setup-box{{border-radius:7px;padding:10px 12px;font-size:0.75rem;line-height:1.8}}
.setup-bull{{background:#003d1f;border:1px solid #00e67633}}
.setup-bear{{background:#3d0011;border:1px solid #ff174433}}
.setup-title{{font-size:0.7rem;color:#4a6080;margin-bottom:4px;letter-spacing:1px}}
.refresh-btn{{background:linear-gradient(135deg,#ffd700,#ff9800);color:#000;border:none;border-radius:7px;padding:10px 28px;font-size:0.9rem;font-weight:bold;cursor:pointer;letter-spacing:1px;margin:0 6px}}
.refresh-btn:hover{{opacity:0.85}}
.note{{font-size:0.7rem;color:#4a6080;margin-top:6px;text-align:center}}
</style>
</head>
<body>

<!-- HEADER -->
<div class="hdr">
  <div>
    <h1>⚡ WD GANN STOCK SCANNER v2.0
      <span>Real-Time NSE Prices • 9 Mathematical Proofs • Square of 9 • Angles • Time Cycles</span>
    </h1>
  </div>
  <div class="hdr-right">
    <b>Based on WD Gann (1878–1955)</b><br>
    Scanned: {scan_time}<br>
    <button class="refresh-btn" onclick="window.location.reload()">🔄 Refresh</button>
    <div class="note">Re-run Python script for latest prices</div>
  </div>
</div>

<!-- SUMMARY -->
<div class="summary">
  <div class="sum-card" style="border-top:3px solid #00e676">
    <div class="sum-num" style="color:#00e676">{len(buys)}</div>
    <div class="sum-lbl">BUY SIGNALS</div>
  </div>
  <div class="sum-card" style="border-top:3px solid #ff1744">
    <div class="sum-num" style="color:#ff1744">{len(sells)}</div>
    <div class="sum-lbl">SELL SIGNALS</div>
  </div>
  <div class="sum-card" style="border-top:3px solid #ff9800">
    <div class="sum-num" style="color:#ff9800">{len(watches)}</div>
    <div class="sum-lbl">WATCH</div>
  </div>
  <div class="sum-card" style="border-top:3px solid #1e3a5f">
    <div class="sum-num" style="color:#4a6080">{len(neutral)}</div>
    <div class="sum-lbl">NEUTRAL</div>
  </div>
</div>

<!-- GANN RULES -->
<div class="rules-box">
  <h3>📜 WD GANN'S 9 MATHEMATICAL PROOFS</h3>
  <b>1. Sq9 Level</b> — √price ±0.125 = natural S/R &nbsp;|&nbsp;
  <b>2. Gann Angle</b> — 1×1 angle = price equilibrium &nbsp;|&nbsp;
  <b>3. 50% CoG</b> — Centre of 52W range = strongest level &nbsp;|&nbsp;
  <b>4. Time Cycle</b> — 30/45/60/90/180/360 days from pivot &nbsp;|&nbsp;
  <b>5. HB/LT</b> — Higher Bottom = bull, Lower Top = bear &nbsp;|&nbsp;
  <b>6. Vol Spike</b> — 1.8× avg volume = trend change signal &nbsp;|&nbsp;
  <b>7. Weekly Rule</b> — Friday High/Low + Tuesday Low rule &nbsp;|&nbsp;
  <b>8. 9:5 Ratio</b> — 9 up days → correction, 5 down → rally &nbsp;|&nbsp;
  <b>9. Dbl Bot/Top</b> — Same price level hit twice = reversal
</div>

<!-- TOP PICKS -->
{'<div class="top-section"><h2>🏆 TOP GANN PICKS</h2>' if buys or sells else ''}
{'<div style="margin-bottom:8px;font-size:0.75rem;color:#4a6080">▲ BUY PICKS</div><div class="picks-row">' + top_buys_html + '</div>' if buys else ''}
{'<div style="margin:10px 0 6px;font-size:0.75rem;color:#4a6080">▼ SELL PICKS</div><div class="picks-row">' + top_sells_html + '</div>' if sells else ''}
{'</div>' if buys or sells else ''}

<!-- LEGEND -->
<div class="legend">
  <div class="leg"><div class="leg-dot" style="background:#00e676"></div>BUY (≥3 bull proofs)</div>
  <div class="leg"><div class="leg-dot" style="background:#ff1744"></div>SELL (≥3 bear proofs)</div>
  <div class="leg"><div class="leg-dot" style="background:#ff9800"></div>WATCH (1-2 proofs)</div>
  <div class="leg"><div class="leg-dot" style="background:#1e3a5f"></div>NEUTRAL</div>
  <div class="leg"><div class="leg-dot" style="background:#b44fff"></div>Time Cycle Active</div>
  <div class="leg" style="color:#4a6080;font-size:0.7rem">👆 Click row for detail card</div>
</div>

<!-- TABLE -->
<div class="tbl-wrap">
  <h2>📊 SCAN RESULTS — {len(analyzed)} Stocks — WD GANN ANALYSIS</h2>
  <div class="tbl-scroll">
  <table>
    <thead><tr>
      <th>#</th><th>STOCK</th><th>LTP</th><th>CHG%</th>
      <th>SIGNAL</th><th>BULL</th><th>BEAR</th>
      <th>Sq9 BUY</th><th>Sq9 SELL</th><th>50% CoG</th>
      <th>T1 TARGET</th><th>STOP LOSS</th><th>R:R</th>
      <th>ACTIVE PROOFS</th>
    </tr></thead>
    <tbody>{table_rows}</tbody>
  </table>
  </div>
</div>

<!-- DETAIL CARDS -->
<div id="detail-section">
  {detail_cards}
</div>

<script>
function toggleCard(sym) {{
  const card = document.getElementById('card-' + sym);
  if (!card) return;
  card.style.display = card.style.display === 'none' ? 'block' : 'none';
}}
</script>
</body>
</html>"""
    return html

# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════
def main():
    scan_time = datetime.datetime.now().strftime("%d %b %Y  %I:%M %p")

    # Fetch prices
    prices = fetch_prices(STOCKS)

    if not prices:
        print("\n  ✗ No data fetched! Check your internet connection.")
        sys.exit(1)

    # Analyze
    print(f"\n  Running WD Gann 9-Proof analysis...")
    analyzed = []
    for sym, data in prices.items():
        result = analyze_stock(data)
        analyzed.append(result)

    # Print summary to terminal
    buys    = [r for r in analyzed if r["signal"] == "BUY"]
    sells   = [r for r in analyzed if r["signal"] == "SELL"]
    watches = [r for r in analyzed if r["signal"] == "WATCH"]

    print(f"\n{'='*60}")
    print(f"  SCAN COMPLETE — {scan_time}")
    print(f"{'='*60}")
    print(f"  ▲ BUY  : {len(buys)} stocks  — {', '.join(r['sym'] for r in buys)}")
    print(f"  ▼ SELL : {len(sells)} stocks  — {', '.join(r['sym'] for r in sells)}")
    print(f"  ◆ WATCH: {len(watches)} stocks")
    print(f"{'='*60}")

    if buys:
        print(f"\n  🏆 TOP BUY PICKS:")
        for r in sorted(buys, key=lambda x: -x['bull_score'])[:5]:
            print(f"     {r['sym']:<15} ₹{r['ltp']:<10} Score:{r['bull_score']}/9  T1:₹{r['t1_buy']}  SL:₹{r['sl_buy']}")

    if sells:
        print(f"\n  🔻 TOP SELL PICKS:")
        for r in sorted(sells, key=lambda x: -x['bear_score'])[:5]:
            print(f"     {r['sym']:<15} ₹{r['ltp']:<10} Score:{r['bear_score']}/9  T1:₹{r['t1_sell']}  SL:₹{r['sl_sell']}")

    # Generate HTML
    print(f"\n  Generating dashboard...")
    html = generate_html(analyzed, scan_time)

    out_path = Path(__file__).parent / "WD_Gann_Dashboard.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  ✔ Dashboard saved: {out_path}")
    print(f"\n  Opening browser...")
    webbrowser.open(f"file://{out_path.absolute()}")
    print(f"\n  ✔ Done! Browser mein dashboard khul gaya.")
    print(f"  ℹ  Latest prices ke liye script dobara run karein.\n")

if __name__ == "__main__":
    main()
