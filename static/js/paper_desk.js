/* Paper desk view: how the LLM analysts are doing and whether the desk ran
 * (app/paper_desk_status.py, /api/paper-desk/status, docs/paper-desk.md).
 *
 * Loaded with `defer`, after the dashboard script whose escapeHtml it uses. pdHtml is pure (data in, HTML out) so
 * tests/app/test_paper_desk_ui.py can render it in node with hostile strings; the DOM and fetch live below it. */

function pdNum(v, digits, signed) {
    if (v === null || v === undefined || Number.isNaN(Number(v))) return '–';
    const n = Number(v);
    return (signed && n > 0 ? '+' : '') + n.toFixed(digits);
}

function pdPct(v) {
    return v === null || v === undefined ? '–' : `${(Number(v) * 100).toFixed(0)}%`;
}

function pdCoverageHtml(cov) {
    if (!cov || !cov.analysts || !cov.analysts.length) return '<p class="td-dim">Chưa có lượt dự đoán nào.</p>';
    const rows = cov.analysts.map(a => '<tr>'
        + `<td>${escapeHtml(a.analyst)}</td><td>${escapeHtml(a.calls)}</td>`
        + `<td>${escapeHtml(a.traded)} <span class="td-dim">(${escapeHtml(a.long)} mua, ${escapeHtml(a.short)} bán)</span></td>`
        + `<td>${pdPct(a.directional_rate)}</td>`
        + `<td class="${a.errors ? 'pnl-negative' : ''}">${escapeHtml(a.errors)}</td></tr>`).join('');
    const days = cov.recent_days.slice().reverse().map(d => '<tr>'
        + `<td>${escapeHtml(d.date)}</td><td>${escapeHtml(d.symbols)} / ${escapeHtml(cov.symbols.length)}</td>`
        + `<td>${escapeHtml(d.calls)}</td><td>${escapeHtml(d.traded)}</td>`
        + `<td class="${d.errors ? 'pnl-negative' : ''}">${escapeHtml(d.errors)}</td></tr>`).join('');
    const missing = cov.days_missing.length
        ? `<p class="pnl-negative">Ngày trong tuần không có lượt dự đoán nào: ${cov.days_missing.map(escapeHtml).join(', ')}</p>`
        : '<p class="td-dim">Không sót ngày trong tuần nào kể từ lượt dự đoán đầu tiên.</p>';
    return `<h4 class="pd-h">Độ đầy đủ</h4>${missing}`
        + '<div class="table-wrap"><table class="data-table"><thead><tr><th>AI phân tích</th><th>Lượt dự đoán</th><th>Có chọn hướng</th>'
        + `<th>Tỷ lệ</th><th>Thất bại</th></tr></thead><tbody>${rows}</tbody></table></div>`
        + `<h4 class="pd-h">${escapeHtml(cov.recent_days.length)} ngày gần nhất (${escapeHtml(cov.days_with_calls)} ngày có dự đoán)</h4>`
        + '<div class="table-wrap"><table class="data-table"><thead><tr><th>Ngày</th><th>Cặp/Mã</th><th>Lượt dự đoán</th>'
        + `<th>Có chọn hướng</th><th>Thất bại</th></tr></thead><tbody>${days}</tbody></table></div>`;
}

// Displayed label of each verdict code (the code itself stays in the tooltip)
function pdVerdictLabel(v) {
    return {PASS: 'Đạt', FAIL: 'Không đạt', TOO_FEW: 'Chưa đủ', BASELINE: 'Mốc so sánh'}[v] || v;
}

function pdScoreHtml(score, minTraded) {
    if (!score) return '<p class="td-dim">Chưa có điểm: `python -m app.paper_desk_runner score` chưa chạy.</p>';
    const row = (name, s) => '<tr>'
        + `<td>${escapeHtml(name)}</td><td>${escapeHtml(s.n)}</td><td>${pdPct(s.hit)}</td>`
        + `<td class="${s.mean === null || s.mean === undefined ? '' : (Number(s.mean) >= 0 ? 'pnl-positive' : 'pnl-negative')}">${pdNum(s.mean, 2, true)}</td>`
        + `<td>${pdNum(s.t, 2, true)}</td><td><span class="fs-verdict fs-verdict--${escapeHtml(s.verdict === 'PASS' ? 'PROMOTE_CHECK' : s.verdict === 'FAIL' ? 'STOP' : 'CONTINUE')}" title="${escapeHtml(s.verdict)}">${escapeHtml(pdVerdictLabel(s.verdict))}</span></td></tr>`;
    const rows = Object.entries(score.analysts).map(([n, s]) => row(n, s)).join('')
        + Object.entries(score.baselines).map(([n, s]) => row(n, s)).join('');
    return `<h4 class="pd-h">Điểm</h4><p class="td-dim">Chấm lúc ${escapeHtml(score.scored_at)}: ${escapeHtml(score.scored_cells)} / `
        + `${escapeHtml(score.cells)} ô ngày × mã đã có giá ra. Cần ${escapeHtml(minTraded)} lượt dự đoán có chọn hướng `
        + 'mới có kết luận; trước đó cột Kết luận ghi "Chưa đủ".</p>'
        + '<div class="table-wrap"><table class="data-table"><thead><tr><th>Tên</th><th>Số lệnh có hướng</th><th>Tỷ lệ đúng</th>'
        + `<th>TB ròng (bp)</th><th>t (gom cụm)</th><th>Kết luận</th></tr></thead><tbody>${rows}</tbody></table></div>`;
}

function pdHtml(data) {
    if (!data) return '<p class="td-dim">Không có dữ liệu.</p>';
    return pdCoverageHtml(data.coverage) + pdScoreHtml(data.score, data.coverage ? data.coverage.min_traded_for_verdict : '');
}

// ---------- DOM, fetch ----------

let pdLoading = false;

async function pdLoad() {
    if (pdLoading) return;
    pdLoading = true;
    const body = document.getElementById('pd-body');
    try {
        const res = await fetch('/api/paper-desk/status');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        body.innerHTML = pdHtml(await res.json());
    } catch (e) {
        body.innerHTML = `<p class="pnl-negative">Không tải được Dự đoán AI: ${escapeHtml(e.message)}</p>`;
    } finally {
        pdLoading = false;
    }
}

function pdOnShow() { pdLoad(); }

document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('pd-refresh-btn');
    if (btn) btn.addEventListener('click', pdLoad);
});
