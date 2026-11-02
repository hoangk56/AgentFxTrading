"""Title parsing of the A2 Telegram push logger (round 73 TG, tg_push.py): which posts are KRW listings and which
coins get the KRW market. Titles are real @upbit_news posts (round73 TG/lag_upbit_news.csv)."""
import importlib.util
import os

import pytest

PATH = os.path.join(os.path.dirname(__file__), "..", "results", "portfolio", "round73_telegram_capture", "TG", "coord",
                    "tg_push.py")


@pytest.fixture(scope="module")
def push():
    spec = importlib.util.spec_from_file_location("tg_push", PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("title, tickers", [
    ("[거래] 퍼퍼(PUFFER) KRW 마켓 디지털 자산 추가 🔗 공지사항 확인하기", ["PUFFER"]),
    ("[거래] 콘크리트(CT) 신규 거래지원 안내 (KRW, BTC, USDT 마켓) 🔗 공지사항 확인하기", ["CT"]),
    ("[거래] 셀레스티아(TIA)(KRW, BTC, USDT 마켓), 아이오넷(IO)(BTC, USDT 마켓) 신규 거래지원 안내", ["TIA"]),
])
def test_krw_listing_tickers(push, title, tickers):
    assert push.krw_listing(title) == 1
    assert push.krw_tickers(title) == tickers


@pytest.mark.parametrize("title", [
    "[디지털 자산] 10월 5주차 GAS 에어드랍 지급 안내 🔗 공지사항 확인하기",
    "[거래] 아이오넷(IO) 신규 거래지원 안내 (BTC, USDT 마켓)",
    "[거래] 퍼퍼(PUFFER) KRW 마켓 거래지원 종료 안내",
    "[거래] 퍼퍼(PUFFER) 유의 종목 지정 안내 (KRW 마켓)",
])
def test_not_a_krw_listing(push, title):
    assert push.krw_listing(title) == 0
