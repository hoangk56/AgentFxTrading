// Overview alert strip: stuck / unpriced bots and recent watchdog restarts (GET /api/dashboard/alerts).
// Hidden when there is nothing to report, so a quiet strip means a healthy desk.
(function () {
    const POLL_MS = 30000;
    const box = document.getElementById('health-alerts');
    const selector = document.getElementById('account-selector');
    if (!box) return;

    function escapeHtml(value) {
        return String(value == null ? '' : value).replace(/[&<>"']/g, ch => (
            {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[ch]));
    }

    function render(alerts) {
        if (!alerts.length) {
            box.hidden = true;
            box.innerHTML = '';
            return;
        }
        box.hidden = false;
        box.innerHTML = alerts.map(a => `
            <div class="health-alert health-alert--${a.level === 'crit' ? 'crit' : 'warn'}">
                <span class="health-alert-tag">${a.level === 'crit' ? 'Action' : 'Watch'}</span>
                <span class="health-alert-bot">${escapeHtml(a.bot)}</span>
                <span class="health-alert-msg">${escapeHtml(a.message)}</span>
            </div>`).join('');
    }

    async function refresh() {
        try {
            const account = selector ? selector.value : 'all';
            // The option's account type (demo / live) keeps a Demo page free of Real bots' alerts and the reverse.
            const type = selector && selector.selectedOptions[0] ? selector.selectedOptions[0].dataset.type || '' : '';
            const res = await fetch(`/api/dashboard/alerts?account_id=${encodeURIComponent(account)}&mode=${encodeURIComponent(type)}`);
            if (res.ok) render((await res.json()).alerts || []);
        } catch (e) {
            // A failed poll must not raise a false alarm; the connection pill already shows a dead link.
        }
    }

    if (selector) selector.addEventListener('change', refresh);
    document.addEventListener('DOMContentLoaded', refresh);
    setInterval(refresh, POLL_MS);
})();
