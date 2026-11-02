"""Đọc tối thiểu file .xls (OLE2 + BIFF8) chỉ bằng thư viện chuẩn: trả về list sheet, mỗi sheet là dict (row, col) -> giá trị.
Viết tay vì venv chỉ có numpy (không xlrd). Chỉ đọc các bản ghi ô cần cho báo cáo giao dịch CBBC của nhà phát hành."""
import struct


def _ole_stream(data, want=("Workbook", "Book")):
    hdr = data[:512]
    if hdr[:8] != b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
        raise ValueError("not OLE2")
    ssz = 1 << struct.unpack_from("<H", hdr, 30)[0]
    mssz = 1 << struct.unpack_from("<H", hdr, 32)[0]
    nfat = struct.unpack_from("<I", hdr, 44)[0]
    dir0 = struct.unpack_from("<i", hdr, 48)[0]
    cutoff = struct.unpack_from("<I", hdr, 56)[0]
    mfat0 = struct.unpack_from("<i", hdr, 60)[0]
    difat0 = struct.unpack_from("<i", hdr, 68)[0]
    ndifat = struct.unpack_from("<I", hdr, 72)[0]

    def sec(i):
        o = 512 + i * ssz
        return data[o:o + ssz]

    fatsecs = list(struct.unpack_from("<109i", hdr, 76))
    d = difat0
    for _ in range(ndifat):
        if d < 0:
            break
        s = sec(d)
        n = ssz // 4 - 1
        fatsecs += list(struct.unpack_from("<%di" % n, s, 0))
        d = struct.unpack_from("<i", s, n * 4)[0]
    fatsecs = [x for x in fatsecs if x >= 0][:nfat]
    fat = []
    for f in fatsecs:
        fat += list(struct.unpack("<%di" % (ssz // 4), sec(f)))

    def chain(start, table):
        out, i, seen = [], start, 0
        while i >= 0 and seen < 10 ** 7:
            out.append(i)
            i = table[i] if i < len(table) else -2
            seen += 1
        return out

    dirdata = b"".join(sec(i) for i in chain(dir0, fat))
    entries = []
    for k in range(len(dirdata) // 128):
        e = dirdata[k * 128:(k + 1) * 128]
        nl = struct.unpack_from("<H", e, 64)[0]
        name = e[:max(nl - 2, 0)].decode("utf-16-le", "replace")
        typ = e[66]
        start = struct.unpack_from("<i", e, 116)[0]
        size = struct.unpack_from("<I", e, 120)[0]
        entries.append((name, typ, start, size))
    root = entries[0]
    for name, typ, start, size in entries:
        if name in want and typ == 2:
            if size >= cutoff:
                return b"".join(sec(i) for i in chain(start, fat))[:size]
            mfat = []
            for f in chain(mfat0, fat):
                mfat += list(struct.unpack("<%di" % (ssz // 4), sec(f)))
            ministream = b"".join(sec(i) for i in chain(root[2], fat))
            return b"".join(ministream[i * mssz:(i + 1) * mssz] for i in chain(start, mfat))[:size]
    raise ValueError("no workbook stream")


def _rk(v):
    if v & 2:
        x = float(struct.unpack("<i", struct.pack("<I", v))[0] >> 2)
    else:
        x = struct.unpack("<d", struct.pack("<Q", (v & 0xFFFFFFFC) << 32))[0]
    return x / 100.0 if v & 1 else x


def _uni(buf, pos, nchars, continues=None):
    """Đọc chuỗi BIFF8 (có cờ nén) bắt đầu ở pos; trả (str, pos mới). Bỏ qua rich text / phonetic."""
    flags = buf[pos]; pos += 1
    rt = sz = 0
    if flags & 8:
        rt = struct.unpack_from("<H", buf, pos)[0]; pos += 2
    if flags & 4:
        sz = struct.unpack_from("<I", buf, pos)[0]; pos += 4
    if flags & 1:
        s = buf[pos:pos + 2 * nchars].decode("utf-16-le", "replace"); pos += 2 * nchars
    else:
        s = buf[pos:pos + nchars].decode("latin-1"); pos += nchars
    pos += 4 * rt + sz
    return s, pos


def read(path):
    wb = _ole_stream(open(path, "rb").read())
    recs = []
    p = 0
    while p + 4 <= len(wb):
        t, n = struct.unpack_from("<HH", wb, p)
        recs.append((t, wb[p + 4:p + 4 + n]))
        p += 4 + n
    sst = []
    sheets = []
    cur = None
    i = 0
    while i < len(recs):
        t, b = recs[i]
        if t == 0x00FC:  # SST, ghép CONTINUE với xử lý cờ nén ở đầu mỗi đoạn
            parts = [b]
            j = i + 1
            while j < len(recs) and recs[j][0] == 0x003C:
                parts.append(recs[j][1]); j += 1
            sst = _parse_sst(parts)
            i = j
            continue
        if t == 0x0809:  # BOF
            bt = struct.unpack_from("<H", b, 2)[0]
            if bt == 0x10:
                cur = {}
                sheets.append(cur)
        elif cur is not None:
            if t == 0x00FD:
                r, c, _, k = struct.unpack_from("<HHHI", b, 0)
                cur[(r, c)] = sst[k] if k < len(sst) else ""
            elif t == 0x0203:
                r, c, _ = struct.unpack_from("<HHH", b, 0)
                cur[(r, c)] = struct.unpack_from("<d", b, 6)[0]
            elif t == 0x027E:
                r, c, _, v = struct.unpack_from("<HHHI", b, 0)
                cur[(r, c)] = _rk(v)
            elif t == 0x00BD:
                r, c0 = struct.unpack_from("<HH", b, 0)
                nn = (len(b) - 6) // 6
                for k in range(nn):
                    _, v = struct.unpack_from("<HI", b, 4 + 6 * k)
                    cur[(r, c0 + k)] = _rk(v)
            elif t == 0x0204:
                r, c, _, ln = struct.unpack_from("<HHHH", b, 0)
                s, _ = _uni(b, 8, ln)
                cur[(r, c)] = s
            elif t == 0x0006:  # FORMULA: chỉ lấy kết quả số
                r, c, _ = struct.unpack_from("<HHH", b, 0)
                if b[12:14] != b"\xff\xff":
                    cur[(r, c)] = struct.unpack_from("<d", b, 6)[0]
        i += 1
    return sheets


def _parse_sst(parts):
    out = []
    total = struct.unpack_from("<I", parts[0], 4)[0]
    pi, pos = 0, 8
    buf = parts[0]
    while len(out) < total:
        if pos >= len(buf):
            pi += 1
            if pi >= len(parts):
                break
            buf, pos = parts[pi], 0
        nch = struct.unpack_from("<H", buf, pos)[0]; pos += 2
        flags = buf[pos]; pos += 1
        rt = sz = 0
        if flags & 8:
            rt = struct.unpack_from("<H", buf, pos)[0]; pos += 2
        if flags & 4:
            sz = struct.unpack_from("<I", buf, pos)[0]; pos += 4
        wide = flags & 1
        s = []
        left = nch
        while left > 0:
            avail = (len(buf) - pos) // (2 if wide else 1)
            take = min(left, avail)
            if wide:
                s.append(buf[pos:pos + 2 * take].decode("utf-16-le", "replace")); pos += 2 * take
            else:
                s.append(buf[pos:pos + take].decode("latin-1")); pos += take
            left -= take
            if left > 0:
                pi += 1
                buf = parts[pi]
                wide = buf[0] & 1
                pos = 1
        skip = 4 * rt + sz
        while skip > 0:
            a = min(skip, len(buf) - pos)
            pos += a; skip -= a
            if skip > 0:
                pi += 1; buf = parts[pi]; pos = 0
        out.append("".join(s))
    return out


def rows(sheet):
    if not sheet:
        return []
    nr = max(r for r, _ in sheet) + 1
    nc = max(c for _, c in sheet) + 1
    return [[sheet.get((r, c), "") for c in range(nc)] for r in range(nr)]


if __name__ == "__main__":
    import sys
    for sh in read(sys.argv[1]):
        for row in rows(sh)[: int(sys.argv[2]) if len(sys.argv) > 2 else 30]:
            print(row)
