/* Overview "Cần làm": stuck, stopped or unpriced bots and recent watchdog restarts of BOTH modes
 * (GET /api/dashboard/alerts, each alert tagged live / demo / all), each with the button that deals with it.
 * The title line (#ov-status) answers for the real money first; the topbar pill counts what is waiting.
 * Redesign D (2026-11-01): before it, the strip showed the current page's mode only.
 *
 * Loaded with `defer`, after dashboard.js (escapeHtml, openView) and confirm_dialog.js. The ov*
 * functions above the DOM part are pure so tests/app/dashboard/test_overview_todo_ui.py can run them in node. */

const OV_ALERTS_POLL_MS = 30000;

/** Buttons for one alert: [action, label]. 'start' / 'restart' call the bot API, 'logs' opens its log lines. */
function ovAlertActions(alert) {
    switch (alert.kind) {
        case 'bot_stopped': return [['start', 'Chạy'], ['logs', 'Nhật ký']];
        case 'restart_failed':
        case 'stale_price': return [['restart', 'Khởi động lại'], ['logs', 'Nhật ký']];
        case 'feed_stalled':
        case 'restarted': return [['logs', 'Nhật ký']];
        default: return [];
    }
}

function ovModeChip(mode) {
    if (mode === 'live') return '<span class="mode-chip mode-chip--live">Thật</span>';
    if (mode === 'demo') return '<span class="mode-chip mode-chip--demo">Demo</span>';
    return '<span class="mode-chip">Server</span>';
}

/** Real first, then critical first: the order the owner deals with them. */
function ovSortAlerts(alerts) {
    const rank = a => (a.mode === 'demo' ? 2 : 0) + (a.level === 'crit' ? 0 : 1);
    return alerts.slice().sort((a, b) => rank(a) - rank(b));
}

/** pending: {container: {text, until}} for rows whose button was used: they keep the outcome and stay locked until
 *  the watchdog clears the alert or the wait runs out, instead of offering the same button again. */
function ovTodoHtml(alerts, pending) {
    const wait = pending || {};
    return ovSortAlerts(alerts).map(a => {
        const crit = a.level === 'crit';
        const held = wait[a.container || a.bot || ''];
        const buttons = held ? '' : ovAlertActions(a).map(([action, label]) => `<button type="button" class="log-btn ov-act${
            action === 'logs' ? '' : ' ov-act--primary'}" data-action="${action}" data-container="${
            escapeHtml(a.container || a.bot || '')}" data-mode="${escapeHtml(a.mode || '')}">${label}</button>`).join('');
        return `<div class="health-alert health-alert--${crit ? 'crit' : 'warn'}">
            ${ovModeChip(a.mode)}
            <span class="health-alert-tag">${crit ? 'Cần xử lý' : 'Để ý'}</span>
            <span class="health-alert-text"><span class="health-alert-bot">${escapeHtml(a.bot)}</span>
                <span class="health-alert-msg">${escapeHtml(a.message)}</span></span>
            <span class="health-alert-actions">${buttons}</span>
            <span class="health-alert-result">${held ? escapeHtml(held.text) : ''}</span>
        </div>`;
    }).join('');
}

/** The title line: the real money's state in words, Demo only as a trailing note. */
function ovStatus(alerts) {
    if (alerts === null) return {cls: 'warn', text: 'Không kiểm được bot: server không trả lời'};
    const real = alerts.filter(a => a.mode !== 'demo');
    const demo = alerts.length - real.length;
    const demoNote = demo ? ` · Demo có ${demo} cảnh báo` : '';
    const crit = real.filter(a => a.level === 'crit').length;
    if (crit) return {cls: 'crit', text: `${crit} việc tiền thật cần xử lý ngay${demoNote}`};
    if (real.length) return {cls: 'warn', text: `${real.length} điều cần để ý ở tiền thật${demoNote}`};
    return {cls: demo ? 'warn' : 'ok', text: `Tiền thật: mọi bot chạy bình thường${demoNote}`};
}

/** Where "Nhật ký" goes: the log view (all modes by default), filtered to the bot. */
function ovLogsUrl(mode, bot) {
    return `#logs?q=${encodeURIComponent(bot)}`;
}

(function () {
    const box = document.getElementById('health-alerts');
    const section = document.getElementById('ov-todo');
    const count = document.getElementById('ov-todo-count');
    const status = document.getElementById('ov-status');
    const pill = document.getElementById('todo-pill');
    if (!box) return;
    let busy = false;   // a click in flight: keep the row until it answers
    const pending = {};   // container -> {text, until}: see ovTodoHtml
    const PENDING_MS = 3 * 60 * 1000;
    let lastOk = null, failures = 0, lastHtml = '';
    const hhmm = d => d.toLocaleTimeString('vi-VN', {hour: '2-digit', minute: '2-digit', hour12: false});

    function render(alerts) {
        const now = Date.now();
        Object.keys(pending).forEach(k => {
            if (pending[k].until < now || !alerts.some(a => (a.container || a.bot) === k)) delete pending[k];
        });
        const s = ovStatus(alerts);
        if (status) {
            status.textContent = `${s.text} · kiểm lúc ${hhmm(lastOk)}`;
            status.className = `ov-status ov-status--${s.cls}`;
        }
        section.hidden = !alerts.length;
        if (count) count.textContent = alerts.length ? `${alerts.length} việc · cả Thật và Demo` : '';
        if (pill) {
            const realCrit = alerts.filter(a => a.mode !== 'demo' && a.level === 'crit').length;
            pill.hidden = !alerts.length;
            pill.className = `todo-pill${realCrit ? ' todo-pill--crit' : ''}`;
            pill.textContent = realCrit ? `${realCrit} việc tiền thật cần làm` : `${alerts.length} việc cần làm`;
        }
        // Only rewrite on a change, so the polite live region is not read out again every 30 s.
        const html = ovTodoHtml(alerts, pending);
        if (!busy && html !== lastHtml) { box.innerHTML = html; lastHtml = html; }
        document.dispatchEvent(new CustomEvent('ov:alerts', {detail: alerts}));
    }

    async function refresh() {
        try {
            const res = await fetch('/api/dashboard/alerts');
            if (!res.ok) throw new Error(String(res.status));
            const alerts = (await res.json()).alerts || [];
            lastOk = new Date(); failures = 0;
            render(alerts);
        } catch (e) {
            // One miss is a blip; two in a row means the "all fine" line can no longer be trusted, so say so.
            failures += 1;
            if (failures >= 2 && status) {
                status.textContent = lastOk ? `Không kiểm được bot từ ${hhmm(lastOk)}` : ovStatus(null).text;
                status.className = 'ov-status ov-status--warn';
            }
        }
    }

    async function runAction(btn) {
        const d = btn.dataset;
        const row = btn.closest('.health-alert');
        const result = row && row.querySelector('.health-alert-result');
        if (d.action === 'logs') {
            location.hash = ovLogsUrl(d.mode, d.container);
            return;
        }
        const live = d.mode === 'live';
        const restart = d.action === 'restart';
        // Hold the list from the dialog on: a poll that rebuilt it would leave this row (its result line and the
        // button focus returns to) detached.
        busy = true;
        const ok = await askConfirm({
            title: `${restart ? 'Khởi động lại' : 'Chạy'} ${d.container}?`,
            body: restart
                ? 'Docker dừng rồi chạy lại container; bot đăng nhập lại cTrader trong khoảng một phút. Lệnh đang mở vẫn nằm ở sàn cùng stop của nó.'
                : 'Docker chạy lại container với lệnh đã lưu; bot đăng nhập lại cTrader trong khoảng một phút.',
            ok: restart ? 'Khởi động lại' : 'Chạy',
            live, typeWord: confirmWordFor(d.container),
        });
        if (!ok) { busy = false; return; }
        row.querySelectorAll('button').forEach(b => { b.disabled = true; });
        if (result) result.textContent = restart ? 'Đang khởi động lại…' : 'Đang chạy…';
        try {
            const res = await fetch(`/api/bots/${encodeURIComponent(d.container)}/${restart ? 'restart' : 'start'}`, {method: 'POST'});
            const data = await res.json().catch(() => ({}));
            if (!res.ok || !data.success) throw new Error(data.message || `Server trả lỗi ${res.status}`);
            pending[d.container] = {until: Date.now() + PENDING_MS,
                text: `Đã gửi lệnh ${restart ? 'khởi động lại' : 'chạy'} lúc ${hhmm(new Date())}, chờ watchdog xác nhận (tối đa 3 phút).`};
            if (result) result.textContent = pending[d.container].text;
        } catch (err) {
            if (result) result.textContent = `Không được: ${(err && err.message) || err}. Thử ở màn Bot.`;
            row.querySelectorAll('button').forEach(b => { b.disabled = false; });
        } finally {
            busy = false;
            lastHtml = '';   // redraw with the row held as pending (or reopened after a failure)
            setTimeout(refresh, 5000);
        }
    }

    box.addEventListener('click', e => {
        const btn = e.target.closest('.ov-act');
        if (btn && !btn.disabled) runAction(btn);
    });
    if (pill) pill.addEventListener('click', e => {
        e.preventDefault();
        if (typeof openView === 'function') openView('view-dashboard');
        section.scrollIntoView({block: 'start'});
    });
    document.addEventListener('DOMContentLoaded', refresh);
    setInterval(() => { if (!document.hidden) refresh(); }, OV_ALERTS_POLL_MS);
})();
