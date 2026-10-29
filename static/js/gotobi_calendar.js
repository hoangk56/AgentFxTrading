/* Calendar view: one month of the GotobiBot's gotobi days, Monday to Friday, with the P&L of its real legs and, apart,
 * of its decoys and of the EcbWindowBot's trades (F3, E1) (app/gotobi_calendar.py, /api/gotobi/calendar). Clicking a
 * day lists its positions.
 *
 * Loaded with `defer`, after the dashboard script whose escapeHtml, formatMoney and selectedAccountId it uses.
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

function gcCellHtml(day, today, selected) {
    const num = Number(day.date.slice(8));
    const cls = ['gc-cell', `gc-cell--${day.status}`];
    if (day.date === today) cls.push('gc-cell--today');
    if (day.date === selected) cls.push('gc-cell--selected');
    const tag = day.status === 'skipped' ? '<span class="gc-tag gc-tag--skip">BỎ QUA</span>'
        : (day.gotobi ? '<span class="gc-tag">GOTOBI</span>' : '');
    let main = '';
    if (day.real.n) {
        const open = day.real.open ? ` · ${day.real.open} đang mở` : '';
        main = `<div class="gc-pnl ${Number(day.real.pnl) >= 0 ? 'pnl-positive' : 'pnl-negative'}">${gcMoney(day.real.pnl)}</div>`
            + `<div class="gc-sub">${day.real.n} lệnh${open}</div>`;
    } else if (day.status === 'scheduled') {
        main = '<div class="gc-sub">theo lịch</div>';
    } else if (day.status === 'no-trade') {
        main = '<div class="gc-sub">không có lệnh</div>';
    } else if (day.status === 'skipped') {
        main = '<div class="gc-sub">Nghỉ lễ Nhật</div>';
    }
    const extra = [];
    const ecb = day.ecb || {n: 0};
    if (ecb.n) extra.push(`<span class="gc-ecb">ECB ${gcMoney(ecb.pnl)} ·${ecb.n}${ecb.open ? ` (${ecb.open} đang mở)` : ''}</span>`);
    const plan = day.ecb_plan || [];
    if (plan.length) extra.push(`<span class="gc-ecb gc-ecb--plan">ECB ${plan.map(gcEcbPlanText).join(' · ')}</span>`);
    if (day.decoy.n) extra.push(`nguỵ trang ${gcMoney(day.decoy.pnl)} ·${day.decoy.n}${day.decoy.open ? ` (${day.decoy.open} đang mở)` : ''}`);
    if (day.other.n) extra.push(`khác ${gcMoney(day.other.pnl)} ·${day.other.n}`);
    const foot = extra.map(x => `<div class="gc-decoy">${x}</div>`).join('');
    return `<button type="button" class="${cls.join(' ')}" data-date="${escapeHtml(day.date)}">`
        + `<div class="gc-cell-head"><span class="gc-num">${num}</span>${tag}</div>${main}${foot}</button>`;
}

function gcMonthHtml(data, selected) {
    const days = (data && data.days) || [];
    const t = (data && data.totals) || {};
    const stat = (label, value, cls = '') => `<div class="kpi-card"><div class="kpi-label">${label}</div>`
        + `<div class="kpi-value kpi-value--mono ${cls}">${value}</div></div>`;
    const stats = '<div class="kpi-grid gc-stats">'
        + stat('Ngày gotobi', `${Number(t.gotobi_days) || 0}`)
        + stat('Ngày có lệnh', `${Number(t.traded_days) || 0}`)
        + stat(`Lời/lỗ thật (${Number(t.real_trades) || 0} lệnh)`, gcMoney(t.real_pnl),
               Number(t.real_pnl) >= 0 ? 'kpi-value--profit' : 'kpi-value--loss')
        + stat(`Lời/lỗ nguỵ trang (${Number(t.decoy_trades) || 0})`, gcMoney(t.decoy_pnl))
        + stat(`Lời/lỗ ECB (${Number(t.ecb_trades) || 0} lệnh)`, gcMoney(t.ecb_pnl),
               Number(t.ecb_pnl) >= 0 ? 'kpi-value--profit' : 'kpi-value--loss')
        + '</div>';
    const head = ['T2', 'T3', 'T4', 'T5', 'T6'].map(d => `<div class="gc-dow">${d}</div>`).join('');
    const blanks = days.length ? '<div class="gc-cell gc-cell--blank"></div>'.repeat(Number(days[0].weekday) || 0) : '';
    const cells = days.map(d => gcCellHtml(d, data.today, selected)).join('');
    return `${stats}<div class="gc-grid">${head}${blanks}${cells}</div>`;
}

function gcDayHtml(day) {
    if (!day) return '';
    const date = escapeHtml(day.date);
    const plan = (day.ecb_plan || []).map(p => `<p class="td-dim lg-hint">ECB ${gcEcbPlanText(p)}`
        + `${p.rule === 'F3' && p.status === 'possible' ? ' (quyết định lúc 07:00 London)' : ''}: bán EURUSD 11:00, đóng 13:00 London.</p>`).join('');
    const title = `<h4 class="lg-subtitle">${date}${day.gotobi ? ' · ngày gotobi' : ''}${day.skipped ? ' · bỏ qua' : ''}</h4>${plan}`;
    if (!day.trades.length) return `${title}<p class="td-dim lg-hint">Ngày này không có lệnh Gotobi hay ECB nào.</p>`;
    const legs = {long: 'Lệnh mua', short: 'Lệnh bán'};
    const sides = {BUY: 'Mua', SELL: 'Bán'};
    const rows = day.trades.map(tr => {
        const ecb = tr.strategy === 'ecb';
        const kind = ecb ? `ECB ${escapeHtml(tr.rule)}` : (tr.decoy ? 'Nguỵ trang' : (tr.leg ? 'Thật' : 'Khác'));
        const leg = ecb ? '11-13 London' : (tr.leg ? legs[tr.leg] || tr.leg[0].toUpperCase() + tr.leg.slice(1) : '—');
        const pnl = tr.status === 'closed'
            ? `<span class="${Number(tr.pnl) >= 0 ? 'pnl-positive' : 'pnl-negative'}">${gcMoney(tr.pnl)}</span>`
            : '<span class="td-dim">đang mở</span>';
        return `<tr class="${tr.decoy ? 'gc-row--decoy' : (ecb ? 'gc-row--ecb' : '')}"><td>${kind}</td><td>${leg}</td>`
            + `<td class="td-mono">${escapeHtml(tr.symbol)}</td><td>${sides[String(tr.side).toUpperCase()] || escapeHtml(tr.side)}</td>`
            + `<td class="td-mono">${escapeHtml(tr.volume)}</td>`
            + `<td class="td-mono">${escapeHtml(tr.entry_time_vn || tr.entry_time || '')}</td>`
            + `<td class="td-mono">${escapeHtml(tr.exit_time_vn || tr.exit_time || '—')}</td>`
            + `<td class="td-mono">${pnl}</td>`
            + `<td class="td-dim">${escapeHtml(tr.account_id)} · ${escapeHtml(tr.bot_id)}</td></tr>`;
    }).join('');
    return `${title}<div class="table-wrap"><table class="data-table"><thead><tr><th>Loại</th><th>Chân lệnh</th><th>Cặp/Mã</th>`
        + '<th>Chiều</th><th>Lot</th><th>Giờ vào (GMT+7)</th><th>Giờ ra (GMT+7)</th><th>Lời/lỗ</th><th>Tài khoản · bot</th>'
        + `</tr></thead><tbody>${rows}</tbody></table></div>`;
}

// ---------- DOM, fetch ----------

let gcMonth = null;        // 'YYYY-MM'; null = the server's current month
let gcSelected = null;     // 'YYYY-MM-DD'
let gcData = null;
let gcLoading = false;

function gcScope() {
    return typeof selectedAccountId !== 'undefined' && selectedAccountId ? selectedAccountId : 'all';
}

function gcShown() {
    const view = document.getElementById('view-calendar');
    return view && view.classList.contains('active');
}

function gcRender() {
    document.getElementById('gc-month-label').textContent = gcData ? gcMonthLabel(gcData.month) : '';
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
