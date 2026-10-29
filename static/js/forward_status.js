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

function fsRowHtml(c) {
    const meanCls = c.mean === null || c.mean === undefined ? '' : (Number(c.mean) >= 0 ? 'pnl-positive' : 'pnl-negative');
    const why = c.verdict === 'STOP' ? 'Why stopped' : 'Still needed';
    return '<tr>'
        + `<td>${escapeHtml(c.label)}<div class="td-dim">${escapeHtml(c.tier)} · ${escapeHtml(c.prereg)}</div></td>`
        + `<td><span class="fs-verdict fs-verdict--${escapeHtml(c.verdict)}">${escapeHtml(c.verdict)}</span></td>`
        + `<td>${escapeHtml(c.n)}</td>`
        + `<td class="${meanCls}">${fsNum(c.mean, 2, true)}</td>`
        + `<td>${fsNum(c.cum, 1, true)}</td>`
        + `<td>${fsNum(c.pooled_t, 2, true)} <span class="td-dim">(HOLD n ${escapeHtml(c.hold_n)})</span></td>`
        + `<td>${c.reasons && c.reasons.length ? `<div class="td-dim">${why}</div>${fsListHtml(c.reasons)}` : ''}`
        + `<div class="td-dim">Not checked here</div>${fsListHtml(c.manual)}</td></tr>`;
}

function fsCalendarHtml(g) {
    if (!g) return '';
    const cls = g.days_left < 0 ? 'pnl-negative' : (g.days_left <= 21 ? 'pnl-negative' : 'td-dim');
    return `<p class="${cls}">Gold level calendar seed: valid through ${escapeHtml(g.valid_through)} `
        + `(${escapeHtml(g.days_left)} days left). The bot stops arming after it; rebuild once the December funding outcome is known.</p>`;
}

function fsTableHtml(data) {
    if (!data || !data.candidates || !data.candidates.length) return '<p class="td-dim">No candidates.</p>';
    return fsCalendarHtml(data.gold_calendar) + '<div class="table-wrap"><table class="data-table"><thead><tr><th>Candidate</th><th>Verdict</th>'
        + '<th>Forward trades</th><th>Mean net bp</th><th>Sum net bp</th><th>Pooled t</th><th>Notes</th></tr></thead>'
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
        body.innerHTML = `<p class="pnl-negative">Could not load the forward status: ${escapeHtml(e.message)}</p>`;
    } finally {
        fsLoading = false;
    }
}

function fsOnShow() { fsLoad(); }

document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('fs-refresh-btn');
    if (btn) btn.addEventListener('click', fsLoad);
});
