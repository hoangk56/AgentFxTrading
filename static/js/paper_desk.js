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
        + `<td>${pdNameHtml(a.analyst)}</td><td class="num">${escapeHtml(a.calls)}</td>`
        + `<td class="num">${escapeHtml(a.traded)} <span class="td-dim">(${escapeHtml(a.long)} mua, ${escapeHtml(a.short)} bán)</span></td>`
        + `<td class="num">${pdPct(a.directional_rate)}</td>`
        + `<td class="num ${a.errors ? 'pnl-negative' : ''}">${escapeHtml(a.errors)}</td></tr>`).join('');
    const days = cov.recent_days.slice().reverse().map(d => '<tr>'
        + `<td>${escapeHtml(d.date)}</td><td class="num">${escapeHtml(d.symbols)} / ${escapeHtml(cov.symbols.length)}</td>`
        + `<td class="num">${escapeHtml(d.calls)}</td><td class="num">${escapeHtml(d.traded)}</td>`
        + `<td class="num ${d.errors ? 'pnl-negative' : ''}">${escapeHtml(d.errors)}</td></tr>`).join('');
    const missing = cov.days_missing.length
        ? `<p class="pd-note pnl-negative">Ngày làm việc không có lượt dự đoán nào: ${cov.days_missing.map(escapeHtml).join(', ')}</p>`
        : '';
    return `<h4 class="pd-h">Từng AI</h4>${missing}`
        + '<div class="table-wrap"><table class="data-table"><thead><tr><th>AI phân tích</th><th class="num">Lượt dự đoán</th><th class="num">Có chọn hướng</th>'
        + `<th class="num">% có chọn hướng</th><th class="num" title="Lượt gọi AI bị lỗi, không phải đoán sai">Lỗi gọi AI</th></tr></thead><tbody>${rows}</tbody></table></div>`
        + `<details class="pd-days"><summary>${escapeHtml(cov.recent_days.length)} ngày gần nhất `
        + `<span class="td-dim">${escapeHtml(cov.days_with_calls)} ngày có dự đoán</span></summary>`
        + '<div class="table-wrap"><table class="data-table"><thead><tr><th>Ngày</th><th class="num">Cặp/Mã</th><th class="num">Lượt dự đoán</th>'
        + `<th class="num">Có chọn hướng</th><th class="num">Lỗi gọi AI</th></tr></thead><tbody>${days}</tbody></table></div></details>`;
}

/** "11:30 30/10/2026" in Vietnam time (UTC+7, no DST) whatever the browser's zone, or the raw value when it is not a
 *  date. */
function pdWhen(iso) {
    const t = iso ? Date.parse(iso) : NaN;
    if (Number.isNaN(t)) return escapeHtml(iso || '–');
    const at = new Date(t + 7 * 3600 * 1000);
    const p = n => String(n).padStart(2, '0');
    return `${p(at.getUTCHours())}:${p(at.getUTCMinutes())} ${p(at.getUTCDate())}/${p(at.getUTCMonth() + 1)}/${at.getUTCFullYear()}`;
}

// Plain names for the analysts (docs/paper-desk.md: trend, meanrev, risk and a chief who reads their answers) and the
// two baselines; the raw id ("trend@deepseek-chat") stays as the second line, since it names the model too.
const PD_NAMES = {trend: 'Theo xu hướng', meanrev: 'Bắt đảo chiều', risk: 'Soát rủi ro', chief: 'Trưởng nhóm (đọc 3 AI kia)',
                  always_long: 'Mốc: luôn mua', prev_day_momentum: 'Mốc: theo hướng hôm qua'};
function pdNameHtml(raw) {
    const role = String(raw || '').split('@')[0];
    const plain = PD_NAMES[role];
    return plain ? `${escapeHtml(plain)}<div class="td-dim pd-raw">${escapeHtml(raw)}</div>` : escapeHtml(raw);
}

// Displayed label of each verdict code (the code itself stays in the tooltip)
function pdVerdictLabel(v) {
    return {PASS: 'Đạt', FAIL: 'Không đạt', TOO_FEW: 'Chưa đủ', BASELINE: 'Mốc so sánh'}[v] || v;
}

function pdScoreHtml(score, minTraded) {
    if (!score) return '<p class="td-dim">Chưa có điểm: `python -m app.paper_desk_runner score` chưa chạy.</p>';
    const row = (name, s) => '<tr>'
        + `<td>${pdNameHtml(name)}</td><td class="num">${escapeHtml(s.n)}</td><td class="num">${pdPct(s.hit)}</td>`
        + `<td class="num ${s.mean === null || s.mean === undefined ? '' : (Number(s.mean) >= 0 ? 'pnl-positive' : 'pnl-negative')}">${pdNum(s.mean, 2, true)}</td>`
        + `<td class="num">${pdNum(s.t, 2, true)}</td><td><span class="fs-verdict fs-verdict--${escapeHtml(s.verdict === 'PASS' ? 'PROMOTE_CHECK' : s.verdict === 'FAIL' ? 'STOP' : 'CONTINUE')}" title="${escapeHtml(s.verdict)}">${escapeHtml(pdVerdictLabel(s.verdict))}</span></td></tr>`;
    const stale = Date.now() - Date.parse(score.scored_at) > 36 * 3600 * 1000;
    const none = !Object.keys(score.analysts || {}).length;
    const rows = Object.entries(score.analysts).map(([n, s]) => row(n, s)).join('')
        + Object.entries(score.baselines).map(([n, s]) => row(n, s)).join('');
    return `<h4 class="pd-h">Điểm</h4><p class="pd-note${stale ? ' pd-stale' : ''}">Chấm lúc ${pdWhen(score.scored_at)} giờ VN`
        + `${stale ? ' (đã cũ: lần chấm sau chưa chạy)' : ''}. Cần ${escapeHtml(minTraded)} lượt `
        + 'dự đoán có chọn hướng mới có kết luận; trước đó cột Kết luận ghi "Chưa đủ".'
        + `${none ? ' Chưa có ô ngày × mã nào có giá ra nên chưa AI nào được chấm; bảng chỉ có hai mốc so sánh.' : ''}</p>`
        + '<div class="table-wrap"><table class="data-table"><thead><tr><th>Tên</th><th class="num">Số lệnh có hướng</th><th class="num">Tỷ lệ đúng</th>'
        + '<th class="num" title="Lời/lỗ trung bình mỗi lệnh sau chi phí, tính bằng phần vạn giá (1 bp = 0,01 %)">TB ròng (bp)</th>'
        + '<th class="num" title="Độ tin cậy của trung bình, đã gộp các lệnh cùng ngày; từ khoảng 2 trở lên mới khó là do may">t (gom cụm)</th>'
        + `<th>Kết luận</th></tr></thead><tbody>${rows}</tbody></table></div>`;
}

/** Directional calls so far, against the count a verdict needs. */
function pdProgress(data) {
    const cov = (data && data.coverage) || {};
    const traded = (cov.analysts || []).reduce((sum, a) => sum + (Number(a.traded) || 0), 0);
    return {traded, need: Number(cov.min_traded_for_verdict) || 0};
}

/** The title line: is there a verdict yet, and did the desk run every weekday. [css modifier, text]. */
function pdStatusOf(data) {
    if (!data) return ['warn', 'Không có dữ liệu'];
    const cov = data.coverage || {};
    if (!(cov.analysts || []).length) return ['', 'Chưa có lượt dự đoán nào'];
    const {traded, need} = pdProgress(data);
    const verdicts = Object.values((data.score && data.score.analysts) || {}).map(s => s.verdict);
    const missing = (cov.days_missing || []).length;
    const run = missing ? `thiếu ${missing} ngày làm việc` : `chạy đủ ${Number(cov.days_with_calls) || 0} ngày`;
    if (verdicts.includes('PASS')) return ['ok', `Có AI đạt: chỉ được thử trên demo một quy tắc đã cố định · ${run}`];
    if (need && traded < need) {
        // At the pace so far (directional calls per day that ran), roughly when the verdict can come.
        const perDay = traded / Math.max(1, Number(cov.days_with_calls) || 0);
        const days = perDay > 0 ? Math.ceil((need - traded) / perDay) : 0;
        const eta = days ? ` · với nhịp hiện tại cần thêm khoảng ${days > 14 ? `${Math.round(days / 5)} tuần` : `${days} ngày`} làm việc` : '';
        return [missing ? 'warn' : '', `Chưa đủ để kết luận: ${traded} / ${need} lượt có chọn hướng${eta} · ${run}`];
    }
    if (verdicts.length && verdicts.every(v => v === 'FAIL')) return ['', `Chưa AI nào hơn mốc so sánh · ${run}`];
    return [missing ? 'warn' : '', `Đã đủ lượt, chờ chấm điểm · ${run}`];
}

function pdSummaryHtml(data) {
    const cov = (data && data.coverage) || {};
    const {traded, need} = pdProgress(data);
    const pct = need ? Math.min(100, Math.round(traded / need * 100)) : 0;
    const score = data && data.score;
    const missing = (cov.days_missing || []).length;
    return '<div class="ov-hero ov-hero--auto pd-stats">'
        + `<div class="ov-stat"><div class="ov-label">Lượt có chọn hướng</div><div class="ov-stat-num">${escapeHtml(traded)}`
        + `<span class="pd-of"> / ${escapeHtml(need)}</span></div>`
        + `<div class="pd-bar" role="img" aria-label="${pct}% số lượt cần để có kết luận"><span style="width:${pct}%"></span></div></div>`
        + `<div class="ov-stat"><div class="ov-label">Ngày đã chạy</div><div class="ov-stat-num">${escapeHtml(cov.days_with_calls || 0)}</div>`
        + `<div class="ov-stat-sub ${missing ? 'pnl-negative' : ''}">${missing ? `thiếu ${missing} ngày làm việc` : 'không sót ngày làm việc nào'}</div></div>`
        + `<div class="ov-stat"><div class="ov-label">Ô đã chấm</div><div class="ov-stat-num">${score ? escapeHtml(score.scored_cells) : '–'}`
        + `<span class="pd-of"> / ${score ? escapeHtml(score.cells) : '–'}</span></div>`
        + `<div class="ov-stat-sub">ngày × mã đã có giá ra</div></div>`
        + '</div>';
}

function pdHtml(data) {
    if (!data) return '<p class="td-dim">Không có dữ liệu.</p>';
    return pdSummaryHtml(data) + pdScoreHtml(data.score, data.coverage ? data.coverage.min_traded_for_verdict : '')
        + pdCoverageHtml(data.coverage);
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
        const data = await res.json();
        body.innerHTML = pdHtml(data);
        pdSay(...pdStatusOf(data));
    } catch (e) {
        body.innerHTML = `<p class="pnl-negative">Không tải được Dự đoán AI: ${escapeHtml(e.message)}</p>`;
        pdSay('warn', 'Không tải được Dự đoán AI');
    } finally {
        pdLoading = false;
    }
}

function pdSay(cls, text) {
    const el = document.getElementById('pd-status');
    if (!el) return;
    el.textContent = text;
    el.className = `ov-status${cls ? ` ov-status--${cls}` : ''}`;
}

function pdOnShow() { pdLoad(); }

document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('pd-refresh-btn');
    if (btn) btn.addEventListener('click', pdLoad);
});
