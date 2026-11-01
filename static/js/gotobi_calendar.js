/* Calendar view: one month of the GotobiBot's gotobi days, Monday to Friday, with the P&L of its real legs and, apart,
 * of its decoys and of the EcbWindowBot's trades (F3, E1) (app/gotobi_calendar.py, /api/gotobi/calendar). Clicking a
 * day lists its positions.
 *
 * Loaded with `defer`, after the dashboard script whose escapeHtml, formatMoney (and bindModeSeg) it uses.
 * The gc*Html functions are pure (data in, HTML out) so tests/app/test_gotobi_calendar_ui.py can render them in node
 * with hostile strings; everything that touches the DOM or fetch lives below them. */

function gcMoney(v) {
    const n = Number(v) || 0;
    return (n > 0 ? '+' : '') + formatMoney(n);
}

function gcMonthLabel(month) {
    const [y, m] = String(month).split('-').map(Number);
    return m >= 1 && m <= 12 ? `Tháng ${m} ${y}` : `? ${y}`;
}

// An installed ECB rule's day without its trade: E1 'scheduled' / 'no-trade', F3 'possible' (USD-TOP is known at
// 07:00 London on the day).
const GC_ECB_PLAN = {scheduled: 'theo lịch', 'no-trade': 'không có lệnh', possible: 'nếu USD-TOP'};

function gcEcbPlanText(p) {
    return `${escapeHtml(p.rule)} ${GC_ECB_PLAN[p.status] || escapeHtml(p.status)}`;
}

const GC_WEEKDAY = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'];
const GC_WEEKDAY_LONG = ['Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy', 'Chủ nhật'];

function gcPnlClass(v) {
    const n = Number(v) || 0;
    return n > 0 ? 'pnl-positive' : n < 0 ? 'pnl-negative' : '';
}

/** Nothing happened and nothing is planned: drawn as a bare number (and left out of the phone list). */
function gcNear(date, today) {
    const days = (Date.parse(date) - Date.parse(today)) / 86400000;
    return !Number.isNaN(days) && days >= 0 && days <= 7;
}

function gcDayIsEmpty(day, today) {
    return !day.real.n && !(day.ecb || {}).n && !(gcNear(day.date, today) && (day.ecb_plan || []).length) && !day.decoy.n && !day.other.n
        && !['scheduled', 'no-trade', 'skipped'].includes(day.status);
}

function gcCellHtml(day, today, selected) {
    const num = Number(day.date.slice(8));
    const cls = ['gc-cell', `gc-cell--${day.status}`];
    if (day.gotobi) cls.push('gc-cell--gotobi');
    if (day.date === today) cls.push('gc-cell--today');
    if (day.date === selected) cls.push('gc-cell--selected');
    if (gcDayIsEmpty(day, today)) cls.push('gc-cell--empty');
    const tag = day.status === 'skipped' ? '<span class="gc-tag gc-tag--skip">nghỉ lễ</span>'
        : (day.gotobi ? '<span class="gc-tag">gotobi</span>' : '');
    const todayTag = day.date === today ? '<span class="gc-today">hôm nay</span>' : '';
    let main = '';
    if (day.real.n) {
        const open = day.real.open ? ` · ${day.real.open} đang mở` : '';
        main = `<span class="gc-pnl ${gcPnlClass(day.real.pnl)}">${gcMoney(day.real.pnl)}</span>`
            + `<span class="gc-sub">${day.real.n} lệnh${open}</span>`;
    } else if (day.status === 'scheduled') {
        main = '<span class="gc-sub">theo lịch</span>';
    } else if (day.status === 'no-trade') {
        main = '<span class="gc-sub">không có lệnh</span>';
    } else if (day.status === 'skipped') {
        main = '<span class="gc-sub">Nghỉ lễ Nhật</span>';
    }
    const extra = [];
    const ecb = day.ecb || {n: 0};
    if (ecb.n) extra.push(`<span class="gc-ecb">ECB <span class="${gcPnlClass(ecb.pnl)}">${gcMoney(ecb.pnl)}</span> · ${ecb.n} lệnh${ecb.open ? ` (${ecb.open} đang mở)` : ''}</span>`);
    // A plan is news for the coming week only; further out it repeats on every cell (the day's detail still has it).
    const plan = gcNear(day.date, today) ? (day.ecb_plan || []) : [];
    if (plan.length) extra.push(`<span class="gc-ecb gc-ecb--plan">ECB ${plan.map(gcEcbPlanText).join(' · ')}</span>`);
    if (day.decoy.n) extra.push(`nguỵ trang ${gcMoney(day.decoy.pnl)} · ${day.decoy.n}${day.decoy.open ? ` (${day.decoy.open} đang mở)` : ''}`);
    if (day.other.n) extra.push(`khác ${gcMoney(day.other.pnl)} · ${day.other.n}`);
    const foot = extra.map(x => `<span class="gc-decoy">${x}</span>`).join('');
    const wd = GC_WEEKDAY[Number(day.weekday)] || '';
    return `<button type="button" class="${cls.join(' ')}" data-date="${escapeHtml(day.date)}" aria-pressed="${day.date === selected}">`
        + `<span class="gc-cell-head"><span class="gc-num"><span class="gc-wd">${wd} </span>${num}</span>${todayTag}${tag}</span>${main}${foot}</button>`;
}

/** The month in one sentence: the real money's result, else the next gotobi day still to come. */
function gcStatusText(data) {
    if (!data) return '';
    const t = data.totals || {};
    const label = gcMonthLabel(data.month);
    const n = Number(t.real_trades) || 0;
    if (n) {
        const pnl = Number(t.real_pnl) || 0;
        return `${label}: ${pnl >= 0 ? 'lời' : 'lỗ'} ${formatMoney(Math.abs(pnl))} trên ${n} lệnh thật, ${Number(t.traded_days) || 0} ngày có lệnh`;
    }
    const next = (data.days || []).find(d => d.gotobi && d.date >= data.today && d.status !== 'skipped');
    const wd = new Date(`${data.today}T00:00:00Z`).getUTCDay();
    const weekend = wd === 0 || wd === 6 ? ` · hôm nay ${wd === 0 ? 'Chủ nhật' : 'thứ Bảy'}, không giao dịch` : '';
    return (next ? `${label}: chưa có lệnh thật · ngày gotobi tới ${Number(next.date.slice(8))}/${Number(next.date.slice(5, 7))}`
        : `${label}: không có lệnh thật`) + (String(data.month) === String(data.today).slice(0, 7) ? weekend : '');
}

function gcMonthHtml(data, selected) {
    const days = (data && data.days) || [];
    const t = (data && data.totals) || {};
    const stat = (label, value, cls, sub) => `<div class="ov-stat"><div class="ov-label">${label}</div>`
        + `<div class="ov-stat-num ${cls}">${value}</div><div class="ov-stat-sub">${sub}</div></div>`;
    const traded = (Number(t.real_trades) || 0) + (Number(t.ecb_trades) || 0) + (Number(t.decoy_trades) || 0);
    // A month with no trade yet: the status line says so, three $0.00 tiles would only repeat it.
    const stats = !traded ? '' : '<div class="ov-hero ov-hero--auto gc-stats">'
        + stat('Lời/lỗ thật', gcMoney(t.real_pnl), gcPnlClass(t.real_pnl),
               `${Number(t.real_trades) || 0} lệnh · ${Number(t.gotobi_days) || 0} ngày gotobi`)
        + stat('ECB', gcMoney(t.ecb_pnl), gcPnlClass(t.ecb_pnl), `${Number(t.ecb_trades) || 0} lệnh`)
        + stat('Nguỵ trang', gcMoney(t.decoy_pnl), 'gc-stat-dim', `${Number(t.decoy_trades) || 0} lệnh, không tính vào lời/lỗ thật`)
        + '</div>';
    const head = ['T2', 'T3', 'T4', 'T5', 'T6'].map(d => `<div class="gc-dow" aria-hidden="true">${d}</div>`).join('');
    const blanks = days.length ? '<div class="gc-cell gc-cell--blank"></div>'.repeat(Number(days[0].weekday) || 0) : '';
    const cells = days.map(d => gcCellHtml(d, data.today, selected)).join('');
    return `${stats}<div class="gc-grid">${head}${blanks}${cells}</div>`;
}

function gcTradeRow(tr) {
    const legs = {long: 'Lệnh mua', short: 'Lệnh bán'};
    const sides = {BUY: 'Mua', SELL: 'Bán'};
    const ecb = tr.strategy === 'ecb';
    const kind = ecb ? `ECB ${escapeHtml(tr.rule)}` : (tr.decoy ? 'Nguỵ trang' : (tr.leg ? 'Thật' : 'Khác'));
    const leg = ecb ? '11-13 London' : (tr.leg ? legs[tr.leg] || escapeHtml(tr.leg[0].toUpperCase() + tr.leg.slice(1)) : '—');
    const pnl = tr.status === 'closed'
        ? `<span class="${gcPnlClass(tr.pnl)}">${gcMoney(tr.pnl)}</span>`
        : '<span class="td-dim">đang mở</span>';
    return `<tr class="${tr.decoy ? 'gc-row--decoy' : (ecb ? 'gc-row--ecb' : '')}"><td>${kind}</td><td>${leg}</td>`
        + `<td class="td-mono">${escapeHtml(tr.symbol)}</td><td>${sides[String(tr.side).toUpperCase()] || escapeHtml(tr.side)}</td>`
        + `<td class="num">${escapeHtml(tr.volume)}</td>`
        + `<td class="td-mono">${escapeHtml(tr.entry_time_vn || tr.entry_time || '')}</td>`
        + `<td class="td-mono">${escapeHtml(tr.exit_time_vn || tr.exit_time || '—')}</td>`
        + `<td class="num">${pnl}</td>`
        + `<td class="td-dim" title="${escapeHtml(tr.account_id)}">${escapeHtml(tr.bot_id)}</td></tr>`;
}

function gcTradeTable(trades) {
    return '<div class="table-wrap"><table class="data-table gc-trades"><thead><tr><th>Loại</th><th>Chân lệnh</th><th>Cặp</th>'
        + '<th>Chiều</th><th class="num">Lot</th><th>Giờ vào (giờ VN)</th><th>Giờ ra (giờ VN)</th><th class="num">Lời/lỗ</th><th>Bot</th>'
        + `</tr></thead><tbody>${trades.map(gcTradeRow).join('')}</tbody></table></div>`;
}

function gcDayHtml(day) {
    if (!day) return '';
    const [y, m, d] = day.date.split('-');
    const wd = GC_WEEKDAY_LONG[Number(day.weekday)] || '';
    const tags = `${day.gotobi ? ' · ngày gotobi' : ''}${day.skipped ? ' · bỏ qua' : ''}`;
    const plan = (day.ecb_plan || []).map(p => `<p class="gc-day-note">ECB ${gcEcbPlanText(p)}`
        + `${p.rule === 'F3' && p.status === 'possible' ? ' (quyết định lúc 07:00 London)' : ''}: bán EURUSD 11:00, đóng 13:00 London.</p>`).join('');
    const title = `<h2 class="gc-day-title">${wd} ${escapeHtml(`${d}/${m}/${y}`)}${tags}</h2>${plan}`;
    if (!day.trades.length) return `${title}<p class="gc-day-note">Ngày này không có lệnh Gotobi hay ECB nào.</p>`;
    // Real legs and ECB first; the decoys (small lots that hide the strategy) fold under their own line.
    const main = day.trades.filter(tr => !tr.decoy);
    const decoys = day.trades.filter(tr => tr.decoy);
    const decoyPnl = decoys.reduce((sum, tr) => sum + (tr.status === 'closed' ? Number(tr.pnl) || 0 : 0), 0);
    return title + (main.length ? gcTradeTable(main) : '<p class="gc-day-note">Không có lệnh thật hay ECB.</p>')
        + (decoys.length ? `<details class="gc-decoys"${main.length ? '' : ' open'}><summary>${decoys.length} lệnh nguỵ trang · `
            + `<span class="${gcPnlClass(decoyPnl)}">${gcMoney(decoyPnl)}</span></summary>${gcTradeTable(decoys)}</details>` : '');
}

// ---------- DOM, fetch ----------

let gcMonth = null;        // 'YYYY-MM'; null = the server's current month
let gcSelected = null;     // 'YYYY-MM-DD'
let gcData = null;
let gcLoading = false;

// The calendar's own Thật / Demo switch (#gc-mode): the two modes trade different ECB rules (F3 live, E1 demo),
// so their days are not added together.
let gcMode = 'live';
function gcScope() {
    return gcMode;
}

function gcShown() {
    const view = document.getElementById('view-calendar');
    return view && view.classList.contains('active');
}

function gcRender() {
    document.getElementById('gc-month-label').textContent = gcData ? gcMonthLabel(gcData.month) : '';
    const status = document.getElementById('gc-status');
    if (status) { status.textContent = gcStatusText(gcData); status.className = 'ov-status'; }
    document.getElementById('gc-body').innerHTML = gcMonthHtml(gcData, gcSelected);
    const day = gcData && gcData.days.find(d => d.date === gcSelected);
    document.getElementById('gc-day').innerHTML = gcDayHtml(day);
}

async function gcLoad() {
    if (gcLoading) return;
    gcLoading = true;
    const body = document.getElementById('gc-body');
    try {
        const month = gcMonth ? `month=${encodeURIComponent(gcMonth)}&` : '';
        const res = await fetch(`/api/gotobi/calendar?${month}account_id=${encodeURIComponent(gcScope())}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        gcData = await res.json();
        if (!gcMonth) gcMonth = gcData.month;
        if (gcSelected === null && gcData.days.some(d => d.date === gcData.today)) gcSelected = gcData.today;
        gcRender();
    } catch (e) {
        body.innerHTML = `<p class="pnl-negative">Không tải được lịch: ${escapeHtml(e.message)}</p>`;
        const status = document.getElementById('gc-status');
        if (status) { status.textContent = 'Không tải được lịch, sẽ thử lại sau một phút'; status.className = 'ov-status ov-status--warn'; }
    } finally {
        gcLoading = false;
    }
}

function gcShiftMonth(delta) {
    const [y, m] = (gcMonth || new Date().toISOString().slice(0, 7)).split('-').map(Number);
    const d = new Date(Date.UTC(y, m - 1 + delta, 1));
    gcMonth = d.toISOString().slice(0, 7);
    gcSelected = null;
    gcLoad();
}

function gotobiOnShow() { gcLoad(); }

function gotobiRefreshIfShown() { if (gcShown()) gcLoad(); }

document.addEventListener('DOMContentLoaded', () => {
    const body = document.getElementById('gc-body');
    if (!body) return;
    body.addEventListener('click', e => {
        const cell = e.target.closest('.gc-cell[data-date]');
        if (!cell || !gcData) return;
        gcSelected = gcSelected === cell.dataset.date ? null : cell.dataset.date;
        gcRender();
        // On a phone the day's trades are below a long list: bring them into view.
        const day = document.getElementById('gc-day');
        if (gcSelected && day && window.matchMedia('(max-width: 640px)').matches) day.scrollIntoView({block: 'start'});
    });
    document.getElementById('gc-prev-btn').addEventListener('click', () => gcShiftMonth(-1));
    document.getElementById('gc-next-btn').addEventListener('click', () => gcShiftMonth(1));
    document.getElementById('gc-today-btn').addEventListener('click', () => {
        gcMonth = null;
        gcSelected = null;
        gcLoad();
    });
    setInterval(() => { if (gcShown() && !document.hidden) gcLoad(); }, 60000);
});

document.addEventListener('DOMContentLoaded', () => {
    if (typeof bindModeSeg === 'function') bindModeSeg('gc-mode', mode => { gcMode = mode; gcLoad(); });
});
