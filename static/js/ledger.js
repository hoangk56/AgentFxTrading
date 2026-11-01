/* Ledger view: per account, the balance its closed trades and the recorded deposits / withdrawals explain (starting
 * from 0), against the broker's, and the balance changes nothing explains yet (app/ledger.py, /api/ledger).
 *
 * Loaded with `defer`, after the dashboard script whose escapeHtml, formatMoney (and bindModeSeg) it uses.
 * The lg*Html functions are pure (data in, HTML out) so tests/app/test_ledger_ui.py can render them in node with
 * hostile strings; everything that touches the DOM or fetch lives below them. */

function lgMoney(v, signed = false) {
    if (v === null || v === undefined) return '—';
    const n = Number(v) || 0;
    return (signed && n > 0 ? '+' : '') + formatMoney(n);
}

function lgStatHtml(label, value, cls = '', sub = '', title = '') {
    return `<div class="ov-stat"${title ? ` title="${escapeHtml(title)}"` : ''}><div class="ov-label">${escapeHtml(label)}</div>`
        + `<div class="ov-stat-num ${cls}">${value}</div>${sub ? `<div class="ov-stat-sub">${sub}</div>` : ''}</div>`;
}

const LG_SHOWN_ROWS = 8;   // unexplained changes shown before "Hiện thêm"

/** The account's answer: does the book match the broker? [css modifier, words]. */
function lgVerdict(a) {
    if (a.broker_balance === null || a.broker_balance === undefined) return ['', 'chưa có số dư bên sàn'];
    if (a.balanced) return ['ok', 'khớp với sàn'];
    const d = Number(a.discrepancy) || 0;
    return ['warn', `sàn ${d > 0 ? 'nhiều' : 'ít'} hơn sổ ${lgMoney(Math.abs(d))}`];
}

/** Indexes of unexplained changes that cancel the one next to them (+12.54 then −12.54): a broker correction,
 *  not money in or out, so they are dimmed and say so. */
function lgCancelling(rows) {
    const out = new Set();
    for (let i = 0; i + 1 < rows.length; i++) {
        if (out.has(i) || rows[i].opening || rows[i + 1].opening) continue;
        if (Math.abs((Number(rows[i].delta) || 0) + (Number(rows[i + 1].delta) || 0)) < 0.005) { out.add(i); out.add(i + 1); }
    }
    return out;
}

function lgAccountHtml(a, tolerance) {
    const id = escapeHtml(a.account_id);
    const noBalance = a.broker_balance === null || a.broker_balance === undefined;
    const head = `<div class="lg-head"><h3 class="lg-name">${escapeHtml(a.label || a.account_id)} <span class="td-dim">${id}</span></h3></div>`;
    const closed = `${Number(a.closed_trades) || 0} lệnh`;
    const stats = '<div class="ov-hero ov-hero--auto lg-stats">'
        + lgStatHtml('Chênh lệch', lgMoney(a.discrepancy, true),
                     noBalance ? '' : (a.balanced ? 'kpi-value--profit' : 'kpi-value--warn'),
                     noBalance ? 'chờ bot báo số dư' : `${escapeHtml(lgVerdict(a)[1])}; trong ±${escapeHtml(tolerance)} là làm tròn`)
        + lgStatHtml('Số dư bên sàn', lgMoney(a.broker_balance), '',
                     noBalance ? 'Chưa nhận được số dư' : `báo lúc ${escapeHtml(a.broker_balance_at_vn || '')}`)
        + lgStatHtml('Số dư dự kiến', lgMoney(a.expected_balance), '',
                     `nạp ${lgMoney(a.deposits)} − rút ${lgMoney(a.withdrawals)} ${Number(a.closed_pnl) < 0 ? '−' : '+'} `
                     + `đã chốt ${lgMoney(Math.abs(Number(a.closed_pnl) || 0))} (${closed})`,
                     'Sổ bắt đầu từ 0: nạp − rút + lời/lỗ các lệnh bot đã đóng')
        + '</div>'
        + (noBalance ? '<p class="lg-note">Chưa nhận được số dư từ tài khoản này: số dư bên sàn và '
                       + 'chênh lệch sẽ hiện khi có bot báo về.</p>' : '');

    const unexplainedRows = a.unexplained || [];
    const cancels = lgCancelling(unexplainedRows);
    const unexplained = unexplainedRows.map((u, i) => {
        const kind = Number(u.delta) >= 0 ? 'nạp' : 'rút';
        const pair = cancels.has(i);
        const nearby = u.opening
            ? `${Number(u.earlier_closes) || 0} lệnh đóng trước đó: ${lgMoney(u.earlier_pnl, true)}`
            : ((u.nearby_closes || []).length ? u.nearby_closes.map(x => escapeHtml(x)).join(', ') : 'không có');
        const balance = u.opening ? `Số dư ghi nhận đầu tiên: ${lgMoney(u.balance)}`
            : `${lgMoney(u.balance_before)} → ${lgMoney(u.balance)}`;
        const cls = [i >= LG_SHOWN_ROWS ? 'lg-more' : '', pair ? 'lg-pair' : ''].filter(Boolean).join(' ');
        return `<tr${cls ? ` class="${cls}"` : ''}><td class="td-mono">${escapeHtml(u.recorded_at_vn || u.recorded_at)}</td>`
            + `<td class="num ${Number(u.delta) >= 0 ? 'pnl-positive' : 'pnl-negative'}">${lgMoney(u.delta, true)}</td>`
            + `<td class="td-mono lg-balance">${balance}</td>`
            + `<td class="td-dim">${pair ? 'bù trừ với dòng kế bên: sàn tự điều chỉnh, thường không phải nạp / rút' : nearby}</td>`
            + `<td class="lg-act"><button class="log-btn lg-confirm" data-account="${id}" data-log="${escapeHtml(u.log_id)}"`
            + ` data-kind="${kind}" data-amount="${escapeHtml(lgMoney(u.delta, true))}" data-when="${escapeHtml(u.recorded_at_vn || u.recorded_at)}"`
            + ` data-balance="${escapeHtml(u.opening ? lgMoney(u.balance) : `${lgMoney(u.balance_before)} → ${lgMoney(u.balance)}`)}"`
            + `${u.opening ? ' data-opening="1"' : ''} aria-label="Ghi là khoản ${kind}">Ghi<span class="lg-wide"> là khoản</span> ${kind}</button></td></tr>`;
    }).join('');
    const openingHint = unexplainedRows.some(u => u.opening)
        ? '<p class="lg-note">Sổ tiền bắt đầu từ 0. "Số dư ghi nhận đầu tiên" là tiền đã có sẵn trong tài khoản '
          + 'khi server bắt đầu ghi số dư, trừ lời/lỗ của các lệnh đã đóng trước đó: ghi nó thành một khoản nạp, '
          + 'hoặc tự nhập các khoản nạp và rút thật kèm ngày của chúng.</p>'
        : '';
    const more = unexplainedRows.length - LG_SHOWN_ROWS;
    const unexplainedSum = unexplainedRows.reduce((sum, u) => sum + (Number(u.delta) || 0), 0);
    const unexplainedHtml = `<h4 class="lg-subtitle">Số dư đổi mà không có lệnh nào giải thích <span class="td-dim">${unexplainedRows.length} dòng`
        + `${unexplainedRows.length ? ` · cộng lại ${lgMoney(unexplainedSum, true)}` : ''}${cancels.size ? ` · ${cancels.size} dòng bù trừ nhau` : ''}</span></h4>`
        + (unexplained
            ? '<div class="table-wrap lg-unexp"><table class="data-table"><thead><tr><th>Lúc (GMT+7)</th><th class="num">Thay đổi</th>'
              + '<th>Số dư</th><th>Lệnh đóng gần đó</th><th><span class="sr-only">Ghi lại</span></th></tr></thead><tbody>' + unexplained + '</tbody></table></div>'
              + (more > 0 ? `<button type="button" class="log-btn lg-show-more" aria-expanded="false">Hiện thêm ${more} dòng</button>` : '')
              + '<p class="lg-note">Nếu là khoản nạp hoặc rút: bấm ghi lại. Nếu không, có thể một lệnh bị mất báo cáo: xem nhật ký của bot.</p>'
              + openingHint
            : '<p class="lg-note">Không có: mọi thay đổi số dư đều có lệnh đóng hoặc khoản nạp / rút giải thích.</p>');

    const movementRows = a.movements || [];
    const movements = movementRows.map(m => {
        const source = m.balance_log_id !== null && m.balance_log_id !== undefined ? 'đã xác nhận' : 'nhập tay';
        return `<tr><td class="td-mono">${escapeHtml(m.occurred_at_vn || m.occurred_at)}</td>`
            + `<td class="num ${Number(m.amount) >= 0 ? 'pnl-positive' : 'pnl-negative'}">${lgMoney(m.amount, true)}</td>`
            + `<td>${escapeHtml(m.note || '')}</td><td class="td-dim">${source}</td>`
            + `<td class="lg-act"><button class="log-btn lg-delete" data-id="${escapeHtml(m.id)}" aria-label="Xoá khoản ${lgMoney(m.amount, true)}">Xoá</button></td></tr>`;
    }).join('');
    const form = `<form class="lg-form" data-account="${id}">`
        + '<label class="lg-field">Lúc<input type="datetime-local" class="log-input lg-when" title="Theo múi giờ trình duyệt; để trống = bây giờ"></label>'
        + '<label class="lg-field">Số tiền<input type="number" step="0.01" class="log-input lg-amount" placeholder="+ nạp / − rút" required></label>'
        + '<label class="lg-field lg-field--wide">Ghi chú<input type="text" maxlength="200" class="log-input lg-note-input" placeholder="không bắt buộc"></label>'
        + '<button type="submit" class="log-btn">Thêm</button><span class="lg-msg" role="alert"></span></form>';
    const movementsHtml = `<details class="lg-moves"><summary>Nạp và rút đã ghi <span class="td-dim">${movementRows.length} khoản`
        + ` · nạp ${lgMoney(a.deposits)} · rút ${lgMoney(a.withdrawals)}</span></summary>`
        + (movements
            ? '<div class="table-wrap"><table class="data-table"><thead><tr><th>Lúc (GMT+7)</th><th class="num">Số tiền</th>'
              + '<th>Ghi chú</th><th>Nguồn</th><th><span class="sr-only">Xoá</span></th></tr></thead><tbody>' + movements + '</tbody></table></div>'
            : '<p class="lg-note">Chưa ghi khoản nào.</p>')
        + form + '</details>';

    return `<section class="lg-account">${head}${stats}${unexplainedHtml}${movementsHtml}</section>`;
}

/** The title line: the real accounts' verdicts, the demo ones as a trailing note. */
function lgStatusOf(data) {
    const accounts = (data && data.accounts) || [];
    if (!accounts.length) return ['', 'Chưa có tài khoản nào'];
    const real = accounts.filter(a => a.account_type === 'live');
    const off = real.filter(a => lgVerdict(a)[0] === 'warn');
    const todo = real.reduce((n, a) => n + (a.unexplained || []).length, 0);
    const todoNote = todo ? ` · ${todo} thay đổi số dư chưa ghi` : '';
    if (!real.length) return ['', 'Chưa có tài khoản tiền thật'];
    if (off.length) return ['warn', `Tiền thật: ${off.length === 1 && real.length === 1 ? lgVerdict(off[0])[1] : `${off.length} tài khoản lệch so với sàn`}${todoNote}`];
    return [todo ? 'warn' : 'ok', `Tiền thật khớp với sàn${todoNote}`];
}

/** Every account (redesign D): the live ones in full, the demo ones folded under one row. */
function lgPageHtml(data) {
    const accounts = (data && data.accounts) || [];
    if (!accounts.length) return '<p class="td-dim">Chưa có tài khoản nào. Tạo ở màn Bot → Cài bot từ mẫu.</p>';
    const real = accounts.filter(a => a.account_type === 'live'), demo = accounts.filter(a => a.account_type !== 'live');
    const realHtml = real.length ? real.map(a => lgAccountHtml(a, data.tolerance)).join('')
        : '<p class="td-dim">Chưa có tài khoản thật nào.</p>';
    const demoOff = demo.filter(a => lgVerdict(a)[0] === 'warn').length;
    const demoHtml = demo.length ? `<details class="ov-demo lg-demo"><summary class="ov-demo-row">`
        + `<span class="mode-chip mode-chip--demo">Demo</span><span class="ov-demo-figs"><span><b>${escapeHtml(demo.length)}</b> tài khoản demo</span>`
        + `${demoOff ? `<span>${demoOff} lệch so với sàn</span>` : ''}</span>`
        + `<span class="ov-demo-toggle"><span class="when-closed">Mở</span><span class="when-open">Thu gọn</span></span></summary>`
        + `<div class="ov-demo-body">${demo.map(a => lgAccountHtml(a, data.tolerance)).join('')}</div></details>` : '';
    return `<section class="ov-real lg-real" aria-label="Tiền thật"><h2 class="ov-real-head">Tiền thật <span>${escapeHtml(real.length)} tài khoản</span></h2>${realHtml}</section>${demoHtml}`;
}

// ---------- DOM, fetch ----------

let lgLoading = false;

function lgScope() {
    return 'all';   // every account; lgPageHtml puts the live ones first
}

function lgShown() {
    const view = document.getElementById('view-ledger');
    return view && view.classList.contains('active');
}

async function lgLoad() {
    if (lgLoading) return;
    lgLoading = true;
    const body = document.getElementById('lg-body');
    try {
        const res = await fetch(`/api/ledger?account_id=${encodeURIComponent(lgScope())}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        // A reload must not close what the owner opened (the demo fold, a "Nạp và rút" list, the long table).
        const opened = new Set([...body.querySelectorAll('details[open]')].map(lgFoldKey));
        const expanded = new Set([...body.querySelectorAll('.lg-unexp.lg-all')].map(lgFoldKey));
        body.innerHTML = lgPageHtml(data);
        body.querySelectorAll('details').forEach(d => { if (opened.has(lgFoldKey(d))) d.open = true; });
        body.querySelectorAll('.lg-unexp').forEach(t => { if (expanded.has(lgFoldKey(t))) lgExpand(t); });
        const [cls, text] = lgStatusOf(data);
        lgSay(cls, text);
    } catch (e) {
        body.innerHTML = `<p class="pnl-negative">Không tải được sổ tiền: ${escapeHtml(e.message)}</p>`;
        lgSay('warn', 'Không tải được sổ tiền');
    } finally {
        lgLoading = false;
    }
}

function lgSay(cls, text) {
    const el = document.getElementById('lg-status');
    if (!el) return;
    el.textContent = text;
    el.className = `ov-status${cls ? ` ov-status--${cls}` : ''}`;
}
/** Which fold this is, stable across a re-render: its class and the account it belongs to. */
function lgFoldKey(el) {
    const acc = el.closest('.lg-account');
    const form = acc && acc.querySelector('.lg-form');
    return `${el.className.replace(/\s*lg-all/, '')}|${form ? form.dataset.account : ''}`;
}
function lgExpand(wrap) {
    wrap.classList.add('lg-all');
    const btn = wrap.parentElement.querySelector('.lg-show-more');
    if (btn) btn.remove();
}

function ledgerOnShow() { lgLoad(); }

function ledgerRefreshIfShown() { if (lgShown()) lgLoad(); }

async function lgPost(payload, msgEl) {
    const res = await fetch('/api/ledger/movements', {
        method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)});
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
        const detail = data.message || (Array.isArray(data.detail) ? data.detail.map(d => d.msg).join('; ') : `HTTP ${res.status}`);
        if (msgEl) msgEl.textContent = detail;
        else lgSay('warn', `Không ghi được: ${detail}`);
        return false;
    }
    await lgLoad();
    return true;
}

document.addEventListener('DOMContentLoaded', () => {
    const body = document.getElementById('lg-body');
    if (!body) return;
    body.addEventListener('click', async e => {
        const confirmBtn = e.target.closest('.lg-confirm');
        if (confirmBtn) {
            const d = confirmBtn.dataset;
            const ok = await askConfirm({
                title: `Ghi ${d.amount} là khoản ${d.kind}?`,
                body: `Lúc ${d.when}, số dư ${d.balance}. Ghi xong, khoản này cộng vào số dư dự kiến và rời danh sách chưa ghi. `
                    + 'Nếu đây là sàn tự điều chỉnh hoặc một lệnh bị mất báo cáo thì đừng ghi: xem nhật ký của bot.',
                ok: `Ghi là khoản ${d.kind}`});
            if (!ok) return;
            confirmBtn.disabled = true;
            await lgPost({account_id: confirmBtn.dataset.account, balance_log_id: Number(confirmBtn.dataset.log),
                          note: confirmBtn.dataset.opening ? 'Có sẵn trong tài khoản trước khi bắt đầu ghi số dư'
                                                           : 'Xác nhận từ một thay đổi số dư'}, null);
            confirmBtn.disabled = false;
            return;
        }
        const more = e.target.closest('.lg-show-more');
        if (more) {
            const wrap = more.parentElement.querySelector('.lg-unexp');
            if (wrap) lgExpand(wrap);
            return;
        }
        const del = e.target.closest('.lg-delete');
        if (del && await askConfirm({title: 'Xoá khoản nạp / rút này?',
                                     body: 'Số dư dự kiến và chênh lệch sẽ tính lại không có khoản này. Thay đổi số dư gốc (nếu có) quay lại danh sách chưa ghi.',
                                     ok: 'Xoá'})) {
            del.disabled = true;
            const res = await fetch(`/api/ledger/movements/${encodeURIComponent(del.dataset.id)}`, {method: 'DELETE'});
            if (!res.ok) lgSay('warn', `Không xoá được: HTTP ${res.status}`);
            await lgLoad();
        }
    });
    body.addEventListener('submit', async e => {
        const form = e.target.closest('.lg-form');
        if (!form) return;
        e.preventDefault();
        const when = form.querySelector('.lg-when').value;
        const msg = form.querySelector('.lg-msg');
        msg.textContent = '';
        await lgPost({
            account_id: form.dataset.account,
            amount: Number(form.querySelector('.lg-amount').value),
            occurred_at: when ? new Date(when).toISOString() : null,
            note: form.querySelector('.lg-note-input').value || null,
        }, msg);
    });
    const refresh = document.getElementById('lg-refresh-btn');
    if (refresh) refresh.addEventListener('click', lgLoad);
    // Refresh while shown, unless the user is typing into a form (a re-render would wipe it)
    setInterval(() => {
        const typing = [...body.querySelectorAll('.lg-form input')].some(i => i.value || i === document.activeElement);
        if (lgShown() && !document.hidden && !typing) lgLoad();
    }, 30000);
});
