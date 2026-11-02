"""Stream UC: reason of a deposit / withdrawal suspension notice from its body (declared in HYPOTHESES_UC.md,
addendum 2). The reason sentence = the LAST Korean sentence before the English part that announces the suspension
(updates are posted above the original text, so the last one is the original notice). Boilerplate ("업데이트 일자",
"서비스 재개를 업데이트", the 유의사항 list) is not used."""
import re
SUSP = re.compile(r"(중단|지연|제한)(합니다|됩니다|하오니|할 예정|되고 있|되어|하고 있|중입니다)")
PLANNED = re.compile(r"업그레이드|하드포크|메인넷|마이그레이션|스왑|에어드[랍롭]|스냅샷|전환|합병|노드\s*(업데이트|업그레이드)|네트워크\s*업데이트|소프트포크|분할")
CHAIN = re.compile(r"불안정|장애|이슈|혼잡|지연|멈춤|중단\s*현상|정지|보안|해킹|취약|공격|오류|문제|이상|불안|비정상|생성\s*중단|블록\s*생성")
WALLET = re.compile(r"월렛\s*(시스템)?\s*점검|지갑\s*(시스템)?\s*점검|시스템\s*점검|정기\s*점검|노드\s*점검|서버\s*점검")


def sentence(body):
    b = body.replace("\r", "")
    k = min([i for i in (b.find("[Notice]"), b.find("Dear Upbit")) if i >= 0] or [len(b)])
    ko = b[:k]
    ss = [s.strip() for s in re.split(r"(?<=다\.)|\n", ko) if s.strip()]
    ss = [s for s in ss if SUSP.search(s) and not s.startswith("-") and "반환" not in s and "본 공지" not in s]
    return ss[-1] if ss else ""


def reason(body):
    s = sentence(body)
    if not s:
        return "UNKNOWN", s
    if PLANNED.search(s):
        return "PLANNED", s
    if WALLET.search(s) and not CHAIN.search(s.replace("점검", "")):
        return "WALLET", s
    if CHAIN.search(s):
        return "CHAIN", s
    return "UNKNOWN", s
