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
    if (!cov || !cov.analysts || !cov.analysts.length) return '<p class="td-dim">No calls recorded yet.</p>';
    const rows = cov.analysts.map(a => '<tr>'
        + `<td>${escapeHtml(a.analyst)}</td><td>${escapeHtml(a.calls)}</td>`
        + `<td>${escapeHtml(a.traded)} <span class="td-dim">(${escapeHtml(a.long)} long, ${escapeHtml(a.short)} short)</span></td>`
        + `<td>${pdPct(a.directional_rate)}</td>`
        + `<td class="${a.errors ? 'pnl-negative' : ''}">${escapeHtml(a.errors)}</td></tr>`).join('');
    const days = cov.recent_days.slice().reverse().map(d => '<tr>'
        + `<td>${escapeHtml(d.date)}</td><td>${escapeHtml(d.symbols)} / ${escapeHtml(cov.symbols.length)}</td>`
        + `<td>${escapeHtml(d.calls)}</td><td>${escapeHtml(d.traded)}</td>`
        + `<td class="${d.errors ? 'pnl-negative' : ''}">${escapeHtml(d.errors)}</td></tr>`).join('');
    const missing = cov.days_missing.length
        ? `<p class="pnl-negative">Weekdays without any call: ${cov.days_missing.map(escapeHtml).join(', ')}</p>`
        : '<p class="td-dim">No weekday missed since the first call.</p>';
    return `<h4 class="pd-h">Coverage</h4>${missing}`
        + '<div class="table-wrap"><table class="data-table"><thead><tr><th>Analyst</th><th>Calls</th><th>Took a side</th>'
        + `<th>Share</th><th>Failed</th></tr></thead><tbody>${rows}</tbody></table></div>`
        + `<h4 class="pd-h">Last ${escapeHtml(cov.recent_days.length)} days (${escapeHtml(cov.days_with_calls)} with calls)</h4>`
        + '<div class="table-wrap"><table class="data-table"><thead><tr><th>Day</th><th>Symbols</th><th>Calls</th>'
        + `<th>Took a side</th><th>Failed</th></tr></thead><tbody>${days}</tbody></table></div>`;
}

function pdScoreHtml(score, minTraded) {
    if (!score) return '<p class="td-dim">No score yet: `python -m app.paper_desk_runner score` has not run.</p>';
    const row = (name, s) => '<tr>'
        + `<td>${escapeHtml(name)}</td><td>${escapeHtml(s.n)}</td><td>${pdPct(s.hit)}</td>`
        + `<td class="${s.mean === null || s.mean === undefined ? '' : (Number(s.mean) >= 0 ? 'pnl-positive' : 'pnl-negative')}">${pdNum(s.mean, 2, true)}</td>`
        + `<td>${pdNum(s.t, 2, true)}</td><td><span class="fs-verdict fs-verdict--${escapeHtml(s.verdict === 'PASS' ? 'PROMOTE_CHECK' : s.verdict === 'FAIL' ? 'STOP' : 'CONTINUE')}">${escapeHtml(s.verdict)}</span></td></tr>`;
    const rows = Object.entries(score.analysts).map(([n, s]) => row(n, s)).join('')
        + Object.entries(score.baselines).map(([n, s]) => row(n, s)).join('');
    return `<h4 class="pd-h">Score</h4><p class="td-dim">Scored ${escapeHtml(score.scored_at)}: ${escapeHtml(score.scored_cells)} of `
        + `${escapeHtml(score.cells)} day-symbol cells have an exit price yet. A verdict needs ${escapeHtml(minTraded)} calls `
        + 'that took a side; until then it reads TOO_FEW.</p>'
        + '<div class="table-wrap"><table class="data-table"><thead><tr><th>Name</th><th>Traded n</th><th>Hit</th>'
        + `<th>Mean net bp</th><th>Clustered t</th><th>Verdict</th></tr></thead><tbody>${rows}</tbody></table></div>`;
}

function pdHtml(data) {
    if (!data) return '<p class="td-dim">No data.</p>';
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
        body.innerHTML = `<p class="pnl-negative">Could not load the paper desk: ${escapeHtml(e.message)}</p>`;
    } finally {
        pdLoading = false;
    }
}

function pdOnShow() { pdLoad(); }

document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('pd-refresh-btn');
    if (btn) btn.addEventListener('click', pdLoad);
});
