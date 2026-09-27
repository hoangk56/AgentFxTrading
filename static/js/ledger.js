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
        + lgStatHtml('Deposits', lgMoney(a.deposits))
        + lgStatHtml('Withdrawals', lgMoney(a.withdrawals))
        + lgStatHtml(`Closed P&L (${Number(a.closed_trades) || 0})`, lgMoney(a.closed_pnl, true),
                     Number(a.closed_pnl) >= 0 ? 'kpi-value--profit' : 'kpi-value--loss')
        + lgStatHtml('Expected balance', lgMoney(a.expected_balance), '', '0 + deposits - withdrawals + closed P&L')
        + lgStatHtml('Broker balance', lgMoney(a.broker_balance), '',
                     noBalance ? 'No balance received yet' : `Reported ${a.broker_balance_at_vn || ''}`)
        + lgStatHtml('Discrepancy', lgMoney(a.discrepancy, true), discCls,
                     `Broker - expected; within ±${tolerance} is rounding`)
        + '</div>'
        + (noBalance ? '<p class="td-dim lg-hint">No balance received from this account yet: the broker balance and '
                       + 'the discrepancy appear once a bot reports one.</p>' : '');

    const unexplainedRows = a.unexplained || [];
    const unexplained = unexplainedRows.map(u => {
        const kind = Number(u.delta) >= 0 ? 'deposit' : 'withdrawal';
        const nearby = u.opening
            ? `${Number(u.earlier_closes) || 0} earlier closes: ${lgMoney(u.earlier_pnl, true)}`
            : ((u.nearby_closes || []).length ? u.nearby_closes.map(x => escapeHtml(x)).join(', ') : 'none');
        const balance = u.opening ? `First balance seen: ${lgMoney(u.balance)}`
            : `${lgMoney(u.balance_before)} → ${lgMoney(u.balance)}`;
        return `<tr><td class="td-mono">${escapeHtml(u.recorded_at_vn || u.recorded_at)}</td>`
            + `<td class="td-mono">${balance}</td>`
            + `<td class="td-mono ${Number(u.delta) >= 0 ? 'pnl-positive' : 'pnl-negative'}">${lgMoney(u.delta, true)}</td>`
            + `<td class="td-dim">${nearby}</td>`
            + `<td><button class="log-btn lg-confirm" data-account="${id}" data-log="${escapeHtml(u.log_id)}"`
            + `${u.opening ? ' data-opening="1"' : ''}>Record as ${kind}</button></td></tr>`;
    }).join('');
    const openingHint = unexplainedRows.some(u => u.opening)
        ? '<p class="td-dim lg-hint">The ledger starts from 0. "First balance seen" is the money already in the account '
          + 'when the server started logging its balance, less the P&amp;L of the closes booked before then: record it '
          + 'as one deposit, or enter the real deposits and withdrawals by hand with their dates.</p>'
        : '';
    const unexplainedHtml = '<h4 class="lg-subtitle">Balance changes no closed trade explains</h4>'
        + (unexplained
            ? '<div class="table-wrap"><table class="data-table"><thead><tr><th>Time (GMT+7)</th><th>Balance</th>'
              + '<th>Change</th><th>Closes nearby</th><th></th></tr></thead><tbody>' + unexplained + '</tbody></table></div>'
              + '<p class="td-dim lg-hint">A deposit or a withdrawal: record it. Otherwise a trade whose report was lost: check the bot\'s log.</p>'
              + openingHint
            : '<p class="td-dim lg-hint">None.</p>');

    const movements = (a.movements || []).map(m => {
        const source = m.balance_log_id !== null && m.balance_log_id !== undefined ? 'confirmed' : 'manual';
        return `<tr><td class="td-mono">${escapeHtml(m.occurred_at_vn || m.occurred_at)}</td>`
            + `<td class="td-mono ${Number(m.amount) >= 0 ? 'pnl-positive' : 'pnl-negative'}">${lgMoney(m.amount, true)}</td>`
            + `<td>${escapeHtml(m.note || '')}</td><td class="td-dim">${source}</td>`
            + `<td><button class="log-btn lg-delete" data-id="${escapeHtml(m.id)}" title="Delete this entry">✕</button></td></tr>`;
    }).join('');
    const movementsHtml = '<h4 class="lg-subtitle">Deposits and withdrawals</h4>'
        + (movements
            ? '<div class="table-wrap"><table class="data-table"><thead><tr><th>Time (GMT+7)</th><th>Amount</th>'
              + '<th>Note</th><th>Source</th><th></th></tr></thead><tbody>' + movements + '</tbody></table></div>'
            : '<p class="td-dim lg-hint">None recorded.</p>');

    const form = `<form class="lg-form" data-account="${id}">`
        + '<input type="datetime-local" class="log-input lg-when" title="Time (your browser\'s time zone); empty = now">'
        + '<input type="number" step="0.01" class="log-input lg-amount" placeholder="Amount: +deposit / -withdrawal" required>'
        + '<input type="text" maxlength="200" class="log-input lg-note" placeholder="Note (optional)">'
        + '<button type="submit" class="log-btn">Add</button><span class="lg-msg"></span></form>';

    return `<section class="panel lg-account">${head}<div class="panel-body">${stats}${unexplainedHtml}${movementsHtml}${form}</div></section>`;
}

function lgPageHtml(data) {
    const accounts = (data && data.accounts) || [];
    if (!accounts.length) return '<p class="td-dim">No account in this view. Create one on Docker Bot Management → Setup Instances.</p>';
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
        body.innerHTML = `<p class="pnl-negative">Could not load the ledger: ${escapeHtml(e.message)}</p>`;
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
                          note: confirmBtn.dataset.opening ? 'In the account before the balance log started'
                                                           : 'Confirmed from a balance change'}, null);
            confirmBtn.disabled = false;
            return;
        }
        const del = e.target.closest('.lg-delete');
        if (del && confirm('Delete this deposit / withdrawal entry?')) {
            del.disabled = true;
            const res = await fetch(`/api/ledger/movements/${encodeURIComponent(del.dataset.id)}`, {method: 'DELETE'});
            if (!res.ok) alert(`Could not delete: HTTP ${res.status}`);
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
