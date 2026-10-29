/* Forward view: each research candidate against the stop and promotion rules it registered
 * (app/forward_status.py, /api/forward/status).
 *
 * Loaded with `defer`, after the dashboard script whose escapeHtml it uses. fsTableHtml is pure (data in, HTML out) so
 * tests/app/test_forward_status_ui.py can render it in node with hostile strings; the DOM and fetch live below it. */

function fsNum(v, digits, signed) {
    if (v === null || v === undefined || Number.isNaN(Number(v))) return '–';
    const n = Number(v);
    return (signed && n > 0 ? '+' : '') + n.toFixed(digits);
}

function fsListHtml(items) {
    if (!items || !items.length) return '';
    return `<ul class="fs-notes">${items.map(i => `<li>${escapeHtml(i)}</li>`).join('')}</ul>`;
}

// Displayed label of each verdict code (the code itself stays in the class and the tooltip)
function fsVerdictLabel(v) {
    return {NO_DATA: 'Chưa có dữ liệu', CONTINUE: 'Tiếp tục theo dõi', STOP: 'Dừng', PROMOTE_CHECK: 'Đủ điều kiện xét'}[v] || v;
}

function fsRowHtml(c) {
    const meanCls = c.mean === null || c.mean === undefined ? '' : (Number(c.mean) >= 0 ? 'pnl-positive' : 'pnl-negative');
    const why = c.verdict === 'STOP' ? 'Lý do dừng' : 'Còn thiếu';
    return '<tr>'
        + `<td>${escapeHtml(c.label)}<div class="td-dim">${escapeHtml(c.tier)} · ${escapeHtml(c.prereg)}</div></td>`
        + `<td><span class="fs-verdict fs-verdict--${escapeHtml(c.verdict)}" title="${escapeHtml(c.verdict)}">${escapeHtml(fsVerdictLabel(c.verdict))}</span></td>`
        + `<td>${escapeHtml(c.n)}</td>`
        + `<td class="${meanCls}">${fsNum(c.mean, 2, true)}</td>`
        + `<td>${fsNum(c.cum, 1, true)}</td>`
        + `<td>${fsNum(c.pooled_t, 2, true)} <span class="td-dim">(HOLD n ${escapeHtml(c.hold_n)})</span></td>`
        + `<td>${c.reasons && c.reasons.length ? `<div class="td-dim">${why}</div>${fsListHtml(c.reasons)}` : ''}`
        + `<div class="td-dim">Chưa kiểm ở đây</div>${fsListHtml(c.manual)}</td></tr>`;
}

function fsCalendarHtml(g) {
    if (!g) return '';
    const cls = g.days_left < 0 ? 'pnl-negative' : (g.days_left <= 21 ? 'pnl-negative' : 'td-dim');
    return `<p class="${cls}">Lịch mốc giá vàng: hiệu lực đến ${escapeHtml(g.valid_through)} `
        + `(còn ${escapeHtml(g.days_left)} ngày). Sau ngày đó bot ngừng đặt lệnh chờ; dựng lại khi biết kết quả funding tháng 12.</p>`;
}

function fsTableHtml(data) {
    if (!data || !data.candidates || !data.candidates.length) return '<p class="td-dim">Chưa có ứng viên.</p>';
    return fsCalendarHtml(data.gold_calendar) + '<div class="table-wrap"><table class="data-table"><thead><tr><th>Ứng viên</th><th>Kết luận</th>'
        + '<th>Số lệnh kiểm chứng</th><th>TB ròng (bp)</th><th>Tổng ròng (bp)</th><th>t gộp</th><th>Ghi chú</th></tr></thead>'
        + `<tbody>${data.candidates.map(fsRowHtml).join('')}</tbody></table></div>`;
}

// ---------- DOM, fetch ----------

let fsLoading = false;

async function fsLoad() {
    if (fsLoading) return;
    fsLoading = true;
    const body = document.getElementById('fs-body');
    try {
        const res = await fetch('/api/forward/status');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        body.innerHTML = fsTableHtml(await res.json());
    } catch (e) {
        body.innerHTML = `<p class="pnl-negative">Không tải được trạng thái kiểm chứng: ${escapeHtml(e.message)}</p>`;
    } finally {
        fsLoading = false;
    }
}

function fsOnShow() { fsLoad(); }

document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('fs-refresh-btn');
    if (btn) btn.addEventListener('click', fsLoad);
});
