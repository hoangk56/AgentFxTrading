// Overview "Sắp tới": the next scheduled Gotobi / ECB entries of the installed bots (GET /api/overview/upcoming),
// shown in Vietnam time. The server works out the days; this file only words them.
// Each list names its scope in data-upcoming-account (the Real block "live", the folded Demo block "demo").
(function () {
    const POLL_MS = 5 * 60 * 1000;
    const lists = Array.from(document.querySelectorAll('ul[data-upcoming-account]'));
    if (!lists.length) return;
    const TZ = 'Asia/Ho_Chi_Minh';
    const hm = new Intl.DateTimeFormat('vi-VN', {timeZone: TZ, hour: '2-digit', minute: '2-digit', hour12: false});
    const ymd = new Intl.DateTimeFormat('en-CA', {timeZone: TZ, year: 'numeric', month: '2-digit', day: '2-digit'});
    const WEEKDAYS = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'];

    function escapeHtml(value) {
        return String(value == null ? '' : value).replace(/[&<>"']/g, ch => (
            {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[ch]));
    }

    // "hôm nay" / "ngày mai" / "T6 31/10", by the Vietnam calendar day.
    function dayLabel(at, now) {
        const day = ymd.format(at), today = ymd.format(now);
        const tomorrow = ymd.format(new Date(now.getTime() + 86400000));
        if (day === today) return 'hôm nay';
        if (day === tomorrow) return 'ngày mai';
        const [, m, d] = day.split('-');
        const weekday = new Date(`${day}T12:00:00+07:00`).getUTCDay();
        return `${WEEKDAYS[weekday]} ${d}/${m}`;
    }

    function itemHtml(e, now) {
        const at = new Date(e.at);
        const name = e.strategy === 'ecb' ? `ECB ${escapeHtml(e.rule || '')}` : 'Gotobi';
        const action = `${e.side === 'BUY' ? 'mua' : 'bán'} ${(e.symbols || []).map(escapeHtml).join(', ')}`;
        const notes = [];
        if (e.jitter_min) notes.push(`giờ xê dịch ±${Math.round(e.jitter_min / 60) || 1} giờ`);
        if (e.conditional) notes.push('chỉ khi đủ điều kiện USD');
        return `<li class="up-row">
            <time class="up-time" datetime="${escapeHtml(e.at)}">${e.jitter_min ? '~' : ''}${hm.format(at)}</time>
            <span class="up-main">${name} · ${action}${notes.length ? `<span class="up-sub">${notes.join(' · ')}</span>` : ''}</span>
            <span class="up-day">${dayLabel(at, now)}</span>
        </li>`;
    }

    function render(list, data) {
        const events = data.events || [];
        const now = data.now ? new Date(data.now) : new Date();
        list.innerHTML = events.length
            ? events.map(e => itemHtml(e, now)).join('')
            : '<li class="ov-empty">Không có lệnh nào theo lịch trong 2 tuần tới.</li>';
    }

    async function refreshOne(list) {
        try {
            const res = await fetch(`/api/overview/upcoming?account_id=${encodeURIComponent(list.dataset.upcomingAccount)}`);
            if (!res.ok) throw new Error(String(res.status));
            render(list, await res.json());
            list.dataset.loaded = '1';
        } catch (e) {
            // Keep the last list; say so only when there is none to keep.
            if (!list.dataset.loaded) list.innerHTML = '<li class="ov-empty">Chưa tải được lịch, sẽ thử lại sau 5 phút.</li>';
        }
    }

    const refresh = () => lists.forEach(refreshOne);
    document.addEventListener('DOMContentLoaded', refresh);
    setInterval(refresh, POLL_MS);
})();
