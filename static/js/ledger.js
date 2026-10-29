/* Ledger view: per account, the balance its closed trades and the recorded deposits / withdrawals explain (starting
 * from 0), against the broker's, and the balance changes nothing explains yet (app/ledger.py, /api/ledger).
 *
 * Loaded with `defer`, after the dashboard script whose escapeHtml, formatMoney and selectedAccountId it uses.
 * The lg*Html functions are pure (data in, HTML out) so tests/app/test_ledger_ui.py can render them in node with
 * hostile strings; everything that touches the DOM or fetch lives below them. */

function lgMoney(v, signed = false) {
    if (v === null || v === undefined) return '—';
    const n = Number(v) || 0;
    return (signed && n > 0 ? '+' : '') + formatMoney(n);
}

function lgStatHtml(label, value, cls = '', title = '') {
    return `<div class="kpi-card"${title ? ` title="${escapeHtml(title)}"` : ''}><div class="kpi-label">${escapeHtml(label)}</div>`
        + `<div class="kpi-value kpi-value--mono ${cls}">${value}</div></div>`;
}

function lgAccountHtml(a, tolerance) {
    const id = escapeHtml(a.account_id);
    const badge = accountBadge(a.account_type);
    const head = `<div class="panel-header"><div class="panel-header-left">${badge}`
        + `<span class="panel-title">${escapeHtml(a.label || a.account_id)}</span>`
        + `<span class="td-dim">${id}</span></div></div>`;
    const noBalance = a.broker_balance === null || a.broker_balance === undefined;
    const discCls = noBalance ? '' : (a.balanced ? 'kpi-value--profit' : 'kpi-value--warn');
    const stats = '<div class="kpi-grid lg-stats">'
        + lgStatHtml('Nạp', lgMoney(a.deposits))
        + lgStatHtml('Rút', lgMoney(a.withdrawals))
        + lgStatHtml(`Lời/lỗ đã chốt (${Number(a.closed_trades) || 0})`, lgMoney(a.closed_pnl, true),
                     Number(a.closed_pnl) >= 0 ? 'kpi-value--profit' : 'kpi-value--loss')
        + lgStatHtml('Số dư dự kiến', lgMoney(a.expected_balance), '', '0 + nạp - rút + lời/lỗ đã chốt')
        + lgStatHtml('Số dư bên sàn', lgMoney(a.broker_balance), '',
                     noBalance ? 'Chưa nhận được số dư' : `Báo lúc ${a.broker_balance_at_vn || ''}`)
        + lgStatHtml('Chênh lệch', lgMoney(a.discrepancy, true), discCls,
                     `Sàn - dự kiến; trong ±${tolerance} là do làm tròn`)
        + '</div>'
        + (noBalance ? '<p class="td-dim lg-hint">Chưa nhận được số dư từ tài khoản này: số dư bên sàn và '
                       + 'chênh lệch sẽ hiện khi có bot báo về.</p>' : '');

    const unexplainedRows = a.unexplained || [];
    const unexplained = unexplainedRows.map(u => {
        const kind = Number(u.delta) >= 0 ? 'nạp' : 'rút';
        const nearby = u.opening
            ? `${Number(u.earlier_closes) || 0} lệnh đóng trước đó: ${lgMoney(u.earlier_pnl, true)}`
            : ((u.nearby_closes || []).length ? u.nearby_closes.map(x => escapeHtml(x)).join(', ') : 'không có');
        const balance = u.opening ? `Số dư ghi nhận đầu tiên: ${lgMoney(u.balance)}`
            : `${lgMoney(u.balance_before)} → ${lgMoney(u.balance)}`;
        return `<tr><td class="td-mono">${escapeHtml(u.recorded_at_vn || u.recorded_at)}</td>`
            + `<td class="td-mono">${balance}</td>`
            + `<td class="td-mono ${Number(u.delta) >= 0 ? 'pnl-positive' : 'pnl-negative'}">${lgMoney(u.delta, true)}</td>`
            + `<td class="td-dim">${nearby}</td>`
            + `<td><button class="log-btn lg-confirm" data-account="${id}" data-log="${escapeHtml(u.log_id)}"`
            + `${u.opening ? ' data-opening="1"' : ''}>Ghi là khoản ${kind}</button></td></tr>`;
    }).join('');
    const openingHint = unexplainedRows.some(u => u.opening)
        ? '<p class="td-dim lg-hint">Sổ tiền bắt đầu từ 0. "Số dư ghi nhận đầu tiên" là tiền đã có sẵn trong tài khoản '
          + 'khi server bắt đầu ghi số dư, trừ lời/lỗ của các lệnh đã đóng trước đó: ghi nó thành một khoản nạp, '
          + 'hoặc tự nhập các khoản nạp và rút thật kèm ngày của chúng.</p>'
        : '';
    const unexplainedHtml = '<h4 class="lg-subtitle">Thay đổi số dư mà không lệnh đã đóng nào giải thích được</h4>'
        + (unexplained
            ? '<div class="table-wrap"><table class="data-table"><thead><tr><th>Thời gian (GMT+7)</th><th>Số dư</th>'
              + '<th>Thay đổi</th><th>Lệnh đóng gần đó</th><th></th></tr></thead><tbody>' + unexplained + '</tbody></table></div>'
              + '<p class="td-dim lg-hint">Nếu là khoản nạp hoặc rút: hãy ghi lại. Nếu không, có thể là một lệnh bị mất báo cáo: xem nhật ký của bot.</p>'
              + openingHint
            : '<p class="td-dim lg-hint">Không có.</p>');

    const movements = (a.movements || []).map(m => {
        const source = m.balance_log_id !== null && m.balance_log_id !== undefined ? 'đã xác nhận' : 'nhập tay';
        return `<tr><td class="td-mono">${escapeHtml(m.occurred_at_vn || m.occurred_at)}</td>`
            + `<td class="td-mono ${Number(m.amount) >= 0 ? 'pnl-positive' : 'pnl-negative'}">${lgMoney(m.amount, true)}</td>`
            + `<td>${escapeHtml(m.note || '')}</td><td class="td-dim">${source}</td>`
            + `<td><button class="log-btn lg-delete" data-id="${escapeHtml(m.id)}" title="Xoá khoản này">✕</button></td></tr>`;
    }).join('');
    const movementsHtml = '<h4 class="lg-subtitle">Nạp và rút</h4>'
        + (movements
            ? '<div class="table-wrap"><table class="data-table"><thead><tr><th>Thời gian (GMT+7)</th><th>Số tiền</th>'
              + '<th>Ghi chú</th><th>Nguồn</th><th></th></tr></thead><tbody>' + movements + '</tbody></table></div>'
            : '<p class="td-dim lg-hint">Chưa ghi khoản nào.</p>');

    const form = `<form class="lg-form" data-account="${id}">`
        + '<input type="datetime-local" class="log-input lg-when" title="Thời gian (theo múi giờ trình duyệt); để trống = bây giờ">'
        + '<input type="number" step="0.01" class="log-input lg-amount" placeholder="Số tiền: + nạp / - rút" required>'
        + '<input type="text" maxlength="200" class="log-input lg-note" placeholder="Ghi chú (không bắt buộc)">'
        + '<button type="submit" class="log-btn">Thêm</button><span class="lg-msg"></span></form>';

    return `<section class="panel lg-account">${head}<div class="panel-body">${stats}${unexplainedHtml}${movementsHtml}${form}</div></section>`;
}

function lgPageHtml(data) {
    const accounts = (data && data.accounts) || [];
    if (!accounts.length) return '<p class="td-dim">Chưa có tài khoản nào trong mục này. Tạo ở màn Bot → Cài bot từ mẫu.</p>';
    return accounts.map(a => lgAccountHtml(a, data.tolerance)).join('');
}

// ---------- DOM, fetch ----------

let lgLoading = false;

function lgScope() {
    return typeof selectedAccountId !== 'undefined' && selectedAccountId ? selectedAccountId : 'all';
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
        body.innerHTML = lgPageHtml(await res.json());
    } catch (e) {
        body.innerHTML = `<p class="pnl-negative">Không tải được sổ tiền: ${escapeHtml(e.message)}</p>`;
    } finally {
        lgLoading = false;
    }
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
        else alert(detail);
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
            confirmBtn.disabled = true;
            await lgPost({account_id: confirmBtn.dataset.account, balance_log_id: Number(confirmBtn.dataset.log),
                          note: confirmBtn.dataset.opening ? 'Có sẵn trong tài khoản trước khi bắt đầu ghi số dư'
                                                           : 'Xác nhận từ một thay đổi số dư'}, null);
            confirmBtn.disabled = false;
            return;
        }
        const del = e.target.closest('.lg-delete');
        if (del && confirm('Xoá khoản nạp / rút này?')) {
            del.disabled = true;
            const res = await fetch(`/api/ledger/movements/${encodeURIComponent(del.dataset.id)}`, {method: 'DELETE'});
            if (!res.ok) alert(`Không xoá được: HTTP ${res.status}`);
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
            note: form.querySelector('.lg-note').value || null,
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
