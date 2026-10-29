"""Vietnamese wording of the close reasons the cBots report (cBot/*.cs CloseWithReason / OnPositionClosed).

The bots keep sending English and the DB keeps it; only the dashboard shows this translation, so old rows read the same
as new ones and no bot needs a rebuild. A reason that matches no rule is shown as sent.
"""
import re
from typing import Callable, List, Optional, Tuple

DECOY_PREFIX = "Decoy: "

_RULES: List[Tuple[re.Pattern, Callable[[re.Match], str]]] = [(re.compile(p, re.IGNORECASE), f) for p, f in (
    (r"^Fix exit \((\d{1,2}:\d{2}) Tokyo\)$", lambda m: f"Thoát lúc fix ({m[1]} Tokyo)"),
    (r"^Session exit \((\d{1,2}:\d{2}) Tokyo\)$", lambda m: f"Hết phiên ({m[1]} Tokyo)"),
    (r"^Window exit \((\d{1,2}:\d{2}) London\)$", lambda m: f"Hết khung giờ ({m[1]} London)"),
    (r"^Hold exit \((\d+) min after the trigger\)$", lambda m: f"Hết thời gian giữ ({m[1]} phút sau tín hiệu)"),
    (r"^Max hold \((\d+) h\)$", lambda m: f"Giữ quá lâu (tối đa {m[1]} giờ)"),
    (r"^Max hold \((\d+) min\)$", lambda m: f"Giữ quá lâu (tối đa {m[1]} phút)"),
    (r"^StopLoss \(virtual, (.+)\)$", lambda m: f"Chạm stop ảo ({m[1]})"),
    (r"^StopLoss \(broker guard, (.+)\)$", lambda m: f"Chạm stop bảo vệ ở sàn ({m[1]})"),
    (r"^StopLoss \(broker, ([\d.]+)-([\d.]+) x the (.+) stop\)$",
     lambda m: f"Chạm stop ở sàn ({m[1]}–{m[2]} x stop {m[3]})"),
    (r"^Stop ?Loss \(Trailing / Break-Even\)$", lambda m: "Chạm stop đã dời (khoá lời / hoà vốn)"),
    (r"^StopLoss \((.+)\)$", lambda m: f"Chạm stop ({m[1]})"),
    (r"^Stop ?Loss$", lambda m: "Chạm stop (SL)"),
    (r"^Take ?Profit$", lambda m: "Chạm chốt lời (TP)"),
    (r"^Stop ?Out$", lambda m: "Sàn tự đóng (thiếu ký quỹ)"),
    (r"^Closed outside the bot(?: \(cTrader\))?$", lambda m: "Đóng ngoài bot (trong cTrader)"),
    (r"^Manual close \(dashboard\)$", lambda m: "Đóng tay (từ dashboard)"),
    (r"^Closed$", lambda m: "Đã đóng"),
)]


def close_reason_vi(reason: Optional[str]) -> Optional[str]:
    """The Vietnamese text for a bot's close reason; None stays None, an unknown reason comes back unchanged."""
    if not reason:
        return reason
    text = reason.strip()
    decoy = text.startswith(DECOY_PREFIX)
    if decoy:
        text = text[len(DECOY_PREFIX):]
    for pattern, render in _RULES:
        m = pattern.match(text)
        if m:
            text = render(m)
            break
    else:
        return reason
    return f"Nguỵ trang: {text}" if decoy else text
