/* Overview Demo block (redesign D, 2026-11-01): one folded row under the Real block with today's result, the month,
 * equity and how many positions are open; opening it shows the same four figures, the open positions (with Close),
 * what comes next and the last closed trades of the demo accounts.
 *
 * Loaded with `defer`, after dashboard.js, whose formatMoney, signedMoney, pnlClass, positionCardHtml, closedRowHtml
 * and closePosition it reuses. It opens itself when a Demo alert appears (overview_alerts.js fires 'ov:alerts');
 * otherwise it keeps the open / folded state the owner left it in. ovDemoFigsHtml is pure for the node tests. */

const OV_DEMO_POLL_MS = 30000;
const OV_DEMO_HISTORY = 5;

function ovDemoFigsHtml(summary, positionCount) {
    if (!summary) return 'Chưa tải được số liệu demo';
    const today = Number(summary.daily_pnl) || 0;
    const month = Number(summary.month_pnl) || 0;
    return `<span>Hôm nay <b class="${pnlClass(today)}">${signedMoney(today)}</b></span>`
        + `<span>Tháng này <b class="${pnlClass(month)}">${signedMoney(month)}</b></span>`
        + `<span>Tính cả lệnh mở <b>${formatMoney(Number(summary.account_equity) || 0)}</b></span>`
        + `<span>Đang giữ <b>${positionCount}</b> lệnh</span>`;
}

(function () {
    const box = document.getElementById('ov-demo');
    if (!box) return;
    const KEY = 'ov_demo_open';
    const el = id => document.getElementById(id);
    let lastDemoAlerts = 0;
    let restoring = true;

    try { box.open = localStorage.getItem(KEY) === '1'; } catch (e) { /* storage blocked: start folded */ }
    restoring = false;
    box.addEventListener('toggle', () => {
        if (restoring) return;
        try { localStorage.setItem(KEY, box.open ? '1' : '0'); } catch (e) { /* not essential */ }
    });

    function setMoney(id, v, signed) {
        const node = el(id);
        if (!node) return;
        const n = Number(v) || 0;
        node.textContent = signed ? signedMoney(n) : formatMoney(n);
        node.className = `ov-stat-num${signed ? ' ' + pnlClass(n) : ''}`;
    }

    async function refresh() {
        try {
            const [sR, pR, hR] = await Promise.all([
                fetch('/api/dashboard/summary?account_id=demo'),
                fetch('/api/dashboard/positions?account_id=demo'),
                fetch(`/api/dashboard/history?account_id=demo&page=1&page_size=${OV_DEMO_HISTORY}`),
            ]);
            if (!sR.ok || !pR.ok || !hR.ok) throw new Error('demo fetch');
            const summary = await sR.json(), positions = await pR.json(), history = await hR.json();
            el('ov-demo-figs').innerHTML = ovDemoFigsHtml(summary, positions.length);
            setMoney('demo-daily-pnl', summary.daily_pnl, true);
            setMoney('demo-month-pnl', summary.month_pnl, true);
            setMoney('demo-balance', summary.account_balance, false);
            setMoney('demo-equity', summary.account_equity, false);
            const f = summary.floating_pnl;
            const fEl = el('demo-floating');
            fEl.textContent = f === null || f === undefined ? '' : `(${signedMoney(f)})`;
            fEl.className = f === null || f === undefined ? '' : pnlClass(f);
            el('demo-pos-count').textContent = `${positions.length} lệnh`;
            el('demo-positions').innerHTML = positions.length
                ? positions.map(positionCardHtml).join('') : '<p class="ov-empty">Không giữ lệnh nào.</p>';
            const items = history.items || [];
            el('demo-history').innerHTML = items.length
                ? items.map(closedRowHtml).join('') : '<p class="ov-empty">Chưa có lệnh nào đóng.</p>';
        } catch (e) {
            if (el('ov-demo-figs').textContent === 'Đang tải…') el('ov-demo-figs').textContent = 'Chưa tải được số liệu demo, sẽ thử lại sau 30 giây';
        }
    }

    // A new Demo alert opens the block once; folding it again is the owner's call until the next new alert.
    document.addEventListener('ov:alerts', e => {
        const n = (e.detail || []).filter(a => a.mode === 'demo').length;
        if (n > lastDemoAlerts && !box.open) box.open = true;
        lastDemoAlerts = n;
    });

    el('demo-positions').addEventListener('click', e => {
        const btn = e.target.closest('.action-close-pos');
        if (btn && !btn.disabled) closePosition(btn).finally(() => setTimeout(refresh, 2000));
    });

    document.addEventListener('DOMContentLoaded', refresh);
    setInterval(() => { if (!document.hidden) refresh(); }, OV_DEMO_POLL_MS);
})();
