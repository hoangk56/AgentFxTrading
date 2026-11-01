"""Round 63 stream M, pre-registration arithmetic. Uses ONLY numbers already published in
round24_relaxed/STREAM_C.md (IC M1, IS 2016-21 / VAL 2022-24) and the venue cost model of HYPOTHESES_M.md at
typical era prices. No price file is read. Output: expected venue net, t and VAL-size HOLD power per row.

SE = (mid - net) ... per era: SE = net / t (t day-clustered), so t at a new cost c = (mid - c) / SE.
Power at VAL size = VAL t x sqrt(1.73 / 3) (keeps the clustering)."""
import math

# id: (IS n, IS mid, IS net, IS t, VAL n, VAL mid, VAL net, VAL t, IC cost IS, IC cost VAL, venue)
R = {
    "F2": (1525, 2.46, 1.82, 3.57, 765, 2.48, 1.85, 2.34, .64, .63, "ECN:EURUSD"),
    "F4": (1509, 1.11, .44, 2.41, 757, 1.14, .52, 2.09, .66, .62, "ECN:EURUSD"),
    "F7": (1526, 1.02, .08, .23, 764, 1.08, .19, .39, .94, .89, "ECN:USDCHF"),
    "F8": (470, 1.94, 1.02, 1.64, 265, 1.84, .97, 1.12, .92, .88, "ECN:USDCHF"),
    "F9": (1525, .69, -.62, -3.12, 765, .58, -.72, -1.97, 1.31, 1.30, "ECN:USDCHF"),
    "F10": (1525, .88, .14, .44, 765, .95, .25, .44, .73, .69, "ECN:USDJPY"),
    "F11": (1525, .92, .06, .16, 765, 1.01, .12, .18, .85, .89, "ECN:EURJPY"),
    "F12": (1418, 1.65, .41, .82, 714, 1.43, .34, .46, 1.24, 1.09, "ECN:GBPJPY"),
    "F13": (1218, 2.12, .94, 1.39, 611, 1.72, .63, .68, 1.18, 1.09, "ECN:GBPJPY"),
    "F14": (1526, 1.76, .90, 1.86, 765, 1.06, .17, .23, .86, .89, "ECN:EURJPY"),
    "F15": (18, 8.65, 7.58, 2.80, 9, 9.55, 8.47, 1.51, 1.07, 1.08, "ECN:EURJPY"),
    "F16": (66, 9.71, 8.84, 2.43, 33, 1.87, 1.09, .26, .87, .78, "ECN:GBPUSD"),
    "F23": (1526, 1.24, .20, .44, 765, 2.07, 1.05, 1.29, 1.04, 1.02, "ECN:USDCNH"),
    "F24": (1526, .24, -.50, -3.83, 765, .93, .23, .98, .74, .70, "ECN:USDJPY"),
    "M2": (255, 1.82, .17, .56, 149, 1.44, .39, .92, 1.65, 1.04, "GC"),
    "M4": (1448, .93, -.59, -1.87, 720, .96, -.06, -.13, 1.52, 1.03, "GC"),
    "M7": (1505, .44, -1.00, -6.11, 753, .38, -.61, -3.14, 1.44, 1.00, "GC"),
    "M11": (1480, 1.03, -.71, -2.30, 739, .88, -.32, -.75, 1.74, 1.19, "GC"),
    "M12": (26, 6.73, 4.84, 1.79, 16, 1.46, .41, .08, 1.89, 1.04, "GC"),
    "I1": (1463, 1.53, -.15, -.26, 734, .92, .27, .41, 1.68, .65, "NQ"),
    "I3": (1434, .57, -.35, -1.47, 728, 1.05, .74, 2.91, .93, .31, "YM"),
    "I4": (1469, .94, -.65, -1.55, 734, 1.68, 1.20, 1.64, 1.59, .49, "ES"),
    "I5": (1492, 1.63, -1.41, -5.62, 740, 1.15, -.89, -3.02, 3.04, 2.03, "Z"),
    "I6": (1485, .75, -1.36, -4.14, 740, .67, -.90, -3.69, 2.10, 1.57, "SPI"),
    "I8": (1437, 2.03, -1.26, -3.86, 722, .29, -2.52, -3.38, 3.29, 2.81, "HSI"),
    "I10": (1523, 1.08, -.13, -.34, 766, 1.02, .49, 1.26, 1.21, .52, "FDAX"),
    "E1x": (987, 5.59, -1.80, -.67, 744, 2.03, -1.30, -.99, 7.39, 3.33, "CL"),
    "E2x": (987, 1.59, -5.94, -9.53, 744, .65, -2.65, -7.75, 7.53, 3.30, "CL"),
    "C1": (1127, 5.72, -7.80, -4.59, 855, 2.05, -1.19, -1.05, 13.52, 3.24, "BTC"),
    "N1a": (3791, .96, -2.24, -17.51, 2166, 2.01, -3.07, -29.18, 3.19, 5.09, "ECN:6USD"),
    "N1b": (4035, .65, -2.26, -18.70, 2272, 1.30, -3.07, -33.92, 2.90, 4.36, "ECN:6USD"),
    "N1c": (2196, 1.18, -2.34, -11.45, 1503, 2.50, -2.92, -24.83, 3.53, 5.41, "ECN:6USD"),
    "F25": (4345, 1.70, .41, .63, 2176, 1.90, .67, .77, 1.29, 1.23, "ECN:10FX"),
    "F27": (306, .69, -.35, -.58, 153, .97, .01, .01, 1.04, .96, "ECN:10FX"),
}
# typical era prices (IS, VAL) and contract specs: (tick in price units, multiplier (units per contract),
# commission per side in contract currency, FX of contract currency to USD (IS, VAL))
PX = {"XAU": (1450, 2000), "US30": (26000, 36000), "US500": (3000, 4400), "USTEC": (9000, 15000),
      "UK100": (7000, 7600), "AUS200": (6200, 7300), "HK50": (26000, 19000), "DE40": (12500, 15500),
      "XTI": (55, 80), "BTC": (20000, 35000)}
FUT = {"GC": ("XAU", .10, 100, 2.5, (1, 1)), "YM": ("US30", 1.0, 5, 2.5, (1, 1)),
       "ES": ("US500", .25, 50, 2.5, (1, 1)), "NQ": ("USTEC", .25, 20, 2.5, (1, 1)),
       "Z": ("UK100", .5, 10, 2.0, (1.3, 1.25)), "SPI": ("AUS200", 1.0, 25, 4.0, (.74, .67)),
       "HSI": ("HK50", 1.0, 50, 40.0, (1 / 7.8, 1 / 7.8)), "FDAX": ("DE40", 1.0, 25, 2.5, (1.15, 1.08)),
       "CL": ("XTI", .01, 1000, 2.5, (1, 1)), "BTC": ("BTC", 5.0, 5, 11.0, (1, 1))}
ECN_FLOOR = {"EURUSD": .09, "USDJPY": .08, "USDCHF": .11, "GBPUSD": .08, "EURJPY": .2, "GBPJPY": .2,
             "USDCNH": .14, "6USD": .12, "10FX": .2}
COMM_FXMET = 0.6  # IC's round-trip commission for FX and metals


def venue_cost(v, ic_cost, era):
    """(lower, upper) round trip bp at typical era prices. ic spread part = IC cost minus IC commission."""
    if v.startswith("ECN:"):
        floor = ECN_FLOOR[v[4:]]
        ic_spr = max(ic_cost - COMM_FXMET, 0)
        return 0.4 + floor, 0.4 + max(floor, ic_spr)
    sym, tick, mult, comm, fx = FUT[v]
    p = PX[sym][era]
    tick_bp = tick / p * 1e4
    comm_bp = 2 * comm * fx[era] / (mult * p) * 1e4
    ic_spr = ic_cost - (COMM_FXMET if sym == "XAU" else 0)
    return tick_bp + comm_bp, max(tick_bp, ic_spr) + comm_bp


print("| id | venue | IC cost IS/VAL | venue cost IS lo-up | venue cost VAL lo-up | IS t at venue up (lo) "
      "| VAL net up | VAL t up (lo) | VAL-size power up (lo) | LIVE cost rt |")
print("|" + "---|" * 10)
for k, (n1, m1, e1, t1, n2, m2, e2, t2, c1, c2, v) in R.items():
    se1 = (e1 / t1) if t1 else float("nan")
    se2 = (e2 / t2) if t2 else float("nan")
    lo1, up1 = venue_cost(v, c1, 0)
    lo2, up2 = venue_cost(v, c2, 1)
    ti_u, ti_l = (m1 - up1) / se1, (m1 - lo1) / se1
    tv_u, tv_l = (m2 - up2) / se2, (m2 - lo2) / se2
    f = math.sqrt(1.73 / 3)
    sd2 = se2 * math.sqrt(n2)
    live = min(m1 - 2.5 * se1, m2 - 1.5 * se2, m2 - 3 * sd2 / math.sqrt(1.73 * n2 / 3))
    print(f"| {k} | {v} | {c1:.2f}/{c2:.2f} | {lo1:.2f}-{up1:.2f} | {lo2:.2f}-{up2:.2f} | {ti_u:+.2f} ({ti_l:+.2f}) "
          f"| {m2 - up2:+.2f} | {tv_u:+.2f} ({tv_l:+.2f}) | {tv_u * f:+.2f} ({tv_l * f:+.2f}) | {live:+.2f} |")
