"""Indicators computed the way the cTrader built-ins used by FlowRsiBot compute them."""
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view


def ema(x: np.ndarray, n: int) -> np.ndarray:
    """cTrader ExponentialMovingAverage: k = 2 / (n + 1), seeded with the first value."""
    k = 2.0 / (n + 1)
    out = np.empty(len(x))
    acc = 0.0
    for i, v in enumerate(x):
        acc = v if i == 0 else v * k + acc * (1.0 - k)
        out[i] = acc
    return out


def rsi(close: np.ndarray, n: int) -> np.ndarray:
    """cTrader RelativeStrengthIndex: EMA(2n - 1) of gains and losses, i.e. Wilder smoothing."""
    d = np.diff(close, prepend=close[0])
    gain = ema(np.maximum(d, 0.0), 2 * n - 1)
    loss = ema(np.maximum(-d, 0.0), 2 * n - 1)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = 100.0 - 100.0 / (1.0 + gain / loss)
    out[loss == 0] = 100.0
    return out


def sma(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    if len(x) >= n:
        cs = np.cumsum(np.r_[0.0, x])
        out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out


def true_range(h: np.ndarray, l: np.ndarray, c: np.ndarray) -> np.ndarray:
    prev = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(np.abs(h - prev), np.abs(l - prev)))
    tr[0] = h[0] - l[0]
    return tr


def atr_sma(h: np.ndarray, l: np.ndarray, c: np.ndarray, n: int) -> np.ndarray:
    """AverageTrueRange(n, MovingAverageType.Simple), FlowRsiBot.cs:532."""
    return sma(true_range(h, l, c), n)


def bollinger(c: np.ndarray, n: int = 20, k: float = 2.0):
    mid = sma(c, n)
    sd = np.full(len(c), np.nan)
    if len(c) >= n:
        sd[n - 1:] = sliding_window_view(c, n).std(axis=1)
    return mid - k * sd, mid, mid + k * sd


def _wilder(x: np.ndarray, n: int) -> np.ndarray:
    return ema(x, 2 * n - 1)


def adx(h: np.ndarray, l: np.ndarray, c: np.ndarray, n: int = 14) -> np.ndarray:
    up = np.diff(h, prepend=h[0])
    down = -np.diff(l, prepend=l[0])
    plus = np.where((up > down) & (up > 0), up, 0.0)
    minus = np.where((down > up) & (down > 0), down, 0.0)
    tr = _wilder(true_range(h, l, c), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        pdi = 100.0 * _wilder(plus, n) / tr
        mdi = 100.0 * _wilder(minus, n) / tr
        dx = 100.0 * np.abs(pdi - mdi) / (pdi + mdi)
    return _wilder(np.nan_to_num(dx), n)


def prior_max(x: np.ndarray, n: int) -> np.ndarray:
    """out[i] = max(x[i-n .. i-1]); NaN for i < n."""
    out = np.full(len(x), np.nan)
    if len(x) > n:
        out[n:] = sliding_window_view(x, n).max(axis=1)[:-1]
    return out


def prior_min(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    if len(x) > n:
        out[n:] = sliding_window_view(x, n).min(axis=1)[:-1]
    return out


def heikin_ashi(o: np.ndarray, h: np.ndarray, l: np.ndarray, c: np.ndarray):
    """(ha_open, ha_close): ha_close = (O+H+L+C)/4, ha_open = mean of the previous HA open and close, seeded with
    (O0+C0)/2."""
    hc = (o + h + l + c) / 4.0
    ho = np.empty(len(o))
    if len(o):
        ho[0] = (o[0] + c[0]) / 2.0
        for i in range(1, len(o)):
            ho[i] = (ho[i - 1] + hc[i - 1]) / 2.0
    return ho, hc


def tdi(close: np.ndarray, rsi_n: int = 13, green_n: int = 2, red_n: int = 7):
    """Traders Dynamic Index lines TMS trades on: green = SMA(green_n) of RSI(rsi_n), red = SMA(red_n) of it."""
    r = rsi(close, rsi_n)
    return sma(r, green_n), sma(r, red_n)


def _rolling_mean(x: np.ndarray, n: int) -> np.ndarray:
    """Mean of each n-window; a NaN only spoils the windows that contain it (unlike sma's running sum)."""
    out = np.full(len(x), np.nan)
    if len(x) >= n:
        out[n - 1:] = sliding_window_view(x, n).mean(axis=1)
    return out


def stoch(h: np.ndarray, l: np.ndarray, c: np.ndarray, k_n: int = 8, slow_n: int = 3, d_n: int = 3):
    """(slow %K, %D): raw %K = 100 (C - LL) / (HH - LL) over k_n bars, slow %K = its SMA(slow_n), %D = SMA(d_n) of
    that. NaN during warm-up and where the k_n-bar range is zero."""
    raw = np.full(len(c), np.nan)
    if len(c) >= k_n:
        hh = sliding_window_view(h, k_n).max(axis=1)
        ll = sliding_window_view(l, k_n).min(axis=1)
        rng = hh - ll
        with np.errstate(divide="ignore", invalid="ignore"):
            raw[k_n - 1:] = np.where(rng > 0, 100.0 * (c[k_n - 1:] - ll) / rng, np.nan)
    k = _rolling_mean(raw, slow_n)
    return k, _rolling_mean(k, d_n)
