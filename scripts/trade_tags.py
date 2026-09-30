"""Read the Label and Comment the cBots put on their orders once the tag key is on (cBot "Trade tags" region).

With the key file ($CTRADER_HOME/ctrader_data/trade_tag_key) a live or demo bot labels its orders with an opaque id
derived from its BotId and encrypts the comment, so the broker sees neither the bot nor the strategy. This is the
same scheme in Python, for reading positions and history in cTrader by hand:

    python scripts/trade_tags.py --key-file /home/forge/ctrader/ctrader_data/trade_tag_key label cbot-demo-usdjpy-fix-gotobi
    python scripts/trade_tags.py --key-file /home/forge/ctrader/ctrader_data/trade_tag_key unseal <comment> [<comment> ...]
    python scripts/trade_tags.py new-key > trade_tag_key      # a fresh key (then chmod 600)
"""
import argparse
import base64
import hashlib
import hmac
import os
import secrets
import struct
import sys

NONCE_BYTES = 8     # cBot TagNonceBytes
MIN_KEY_CHARS = 16


def read_key(path: str) -> bytes:
    secret = open(path, encoding="utf-8").read().strip()
    if len(secret) < MIN_KEY_CHARS:
        raise ValueError(f"the key in {path} is shorter than {MIN_KEY_CHARS} characters; the bots ignore it")
    return secret.encode("utf-8")


def _mac(key: bytes, data: bytes) -> bytes:
    return hmac.new(key, data, hashlib.sha256).digest()


def label(key: bytes, bot_id: str) -> str:
    """The Label a bot with `bot_id` trades under (cBot InitTradeTags)."""
    return "t" + _mac(key, b"label|" + bot_id.encode("utf-8"))[:6].hex()


def _keystream(key: bytes, nonce: bytes, length: int) -> bytes:
    """HMAC-SHA256(key, nonce || counter) blocks, the counter a little-endian int32 (C# BitConverter)."""
    out = b"".join(_mac(key, nonce + struct.pack("<i", i)) for i in range((length + 31) // 32))
    return out[:length]


def seal(key: bytes, tag: str, nonce: bytes = None) -> str:
    """The comment an order carries for `tag` (cBot Seal)."""
    plain = tag.encode("utf-8")
    nonce = secrets.token_bytes(NONCE_BYTES) if nonce is None else nonce
    cipher = bytes(p ^ s for p, s in zip(plain, _keystream(key, nonce, len(plain))))
    return base64.urlsafe_b64encode(nonce + cipher).decode("ascii").rstrip("=")


def unseal(key: bytes, comment: str) -> str:
    """The tag behind a comment; a plain one (contains a space, or not base64url) comes back unchanged (cBot Unseal)."""
    if not comment or " " in comment:
        return comment
    try:
        raw = base64.urlsafe_b64decode(comment + "=" * (-len(comment) % 4))
    except (ValueError, TypeError):
        return comment
    if len(raw) <= NONCE_BYTES:
        return comment
    nonce, cipher = raw[:NONCE_BYTES], raw[NONCE_BYTES:]
    plain = bytes(c ^ s for c, s in zip(cipher, _keystream(key, nonce, len(cipher))))
    return plain.decode("utf-8", errors="replace")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--key-file", default=os.path.join(os.environ.get("CTRADER_HOME", "/root"), "ctrader_data", "trade_tag_key"))
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("new-key", help="print a fresh random key")
    p_label = sub.add_parser("label", help="the Label of each BotId")
    p_label.add_argument("bot_ids", nargs="+")
    p_unseal = sub.add_parser("unseal", help="the tag behind each comment")
    p_unseal.add_argument("comments", nargs="+")
    args = parser.parse_args(argv)

    if args.cmd == "new-key":
        print(secrets.token_urlsafe(32))
        return 0
    key = read_key(args.key_file)
    if args.cmd == "label":
        for bot_id in args.bot_ids:
            print(f"{label(key, bot_id)}  {bot_id}")
    else:
        for comment in args.comments:
            print(f"{unseal(key, comment)}  <- {comment}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
