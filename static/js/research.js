/* Research view ("Nghiên cứu"): every researched algorithm from research/registry.yaml grouped by tier, the selected
 * one's detail with its forward tracker, and the collapsed "Đã thử, không đạt" table
 * (app/research_api.py, GET /api/research; docs/research-screen.md). Modelled on 106.dnse-stock's research page.
 *
 * Loaded with `defer`, after the dashboard script whose escapeHtml it uses. The functions above the DOM part are pure
 * (data in, HTML or values out) so tests/app/test_research_ui.py can run them in node with hostile strings.
 * Filter, search and the selected algorithm live in the hash: #research?tier=demo&q=ecb&id=F3 (#forward is an alias). */

const RS_TIERS = [
    {tier: 'live', label: 'Đang live'},
    {tier: 'demo', label: 'Demo'},
    {tier: 'cho-kiem', label: 'Chờ kiểm'},
    {tier: 'da-loai', label: 'Đã loại'},
];
const RS_COLLAPSED_TIER = 'da-loai';      // collapsed when the page opens
const RS_CLOSED_ROWS = 10;                // latest closed basis B demo signals shown

function rsNum(v, digits, signed) {
    if (v === null || v === undefined || v === '' || Number.isNaN(Number(v))) return '–';
    const n = Number(v);
    return (signed && n > 0 ? '+' : '') + n.toFixed(digits);
}

function rsTierOf(entry) {
    return RS_TIERS.some(t => t.tier === entry.tier) ? entry.tier : 'cho-kiem';
}

function rsTierLabel(tier) {
    const t = RS_TIERS.find(x => x.tier === tier);
    return t ? t.label : tier;
}

/** Lower case without Vietnamese accents, so "dung" finds "Dừng". */
function rsFold(text) {
    return String(text || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/đ/g, 'd');
}

function rsMatches(entry, q) {
    const needle = rsFold(q).trim();
    if (!needle) return true;
    return rsFold([entry.id, entry.name, entry.description, entry.market, entry.round].join(' ')).includes(needle);
}

function rsFilter(entries, state) {
    return (entries || []).filter(e => (!state.tier || rsTierOf(e) === state.tier) && rsMatches(e, state.q));
}

function rsCounts(entries) {
    const counts = {all: entries.length};
    RS_TIERS.forEach(t => { counts[t.tier] = 0; });
    entries.forEach(e => { counts[rsTierOf(e)] += 1; });
    return counts;
}

/** {tier, q, id} from "#research?tier=…&q=…&id=…"; anything unknown is dropped. */
function rsParseHash(hash) {
    const at = String(hash || '').indexOf('?');
    const params = new URLSearchParams(at >= 0 ? hash.slice(at + 1) : '');
    const tier = params.get('tier');
    return {
        tier: RS_TIERS.some(t => t.tier === tier) ? tier : null,
        q: (params.get('q') || '').slice(0, 80),
        id: (params.get('id') || '').slice(0, 80) || null,
    };
}

function rsHashFor(state) {
    const params = new URLSearchParams();
    if (state.tier) params.set('tier', state.tier);
    if (state.q && state.q.trim()) params.set('q', state.q);
    if (state.id) params.set('id', state.id);
    const query = params.toString();
    return '#research' + (query ? '?' + query : '');
}

/** The entries shown in the list, in tier order, and the selected one: the hash's id when it is shown, else the first
 *  shown entry outside the collapsed tier, else the first shown. */
function rsSelection(entries, state) {
    const shown = rsFilter(entries, state);
    const ordered = RS_TIERS.flatMap(t => shown.filter(e => rsTierOf(e) === t.tier));
    const selected = ordered.find(e => e.id === state.id)
        || ordered.find(e => rsTierOf(e) !== RS_COLLAPSED_TIER) || ordered[0] || null;
    return {ordered, selected};
}

function rsVerdictLabel(v) {
    return {NO_DATA: 'Chưa có dữ liệu', CONTINUE: 'Tiếp tục theo dõi', STOP: 'Dừng', PROMOTE_CHECK: 'Đủ điều kiện xét'}[v] || v;
}

function rsVerdictHtml(v) {
    return `<span class="fs-verdict fs-verdict--${escapeHtml(v)}" title="${escapeHtml(v)}">${escapeHtml(rsVerdictLabel(v))}</span>`;
}

function rsListItemsHtml(items) {
    if (!items || !items.length) return '';
    return `<ul class="fs-notes">${items.map(i => `<li>${escapeHtml(i)}</li>`).join('')}</ul>`;
}

function rsCode(path) {
    return `<code class="rs-code">${escapeHtml(path)}</code>`;
}

function rsChipsHtml(counts, state) {
    const chip = (tier, label, n) => `<button type="button" class="rs-chip${tier ? ' rs-chip--' + tier : ''}" `
        + `data-rs-tier="${escapeHtml(tier)}" aria-pressed="${(state.tier || '') === tier}">${escapeHtml(label)} `
        + `<b>${escapeHtml(n)}</b></button>`;
    return chip('', 'Tất cả', counts.all) + RS_TIERS.map(t => chip(t.tier, t.label, counts[t.tier])).join('');
}

/** The short state on the right of a list row: the tracker's verdict, or nothing. */
function rsItemStateHtml(entry) {
    const tr = entry.tracker;
    if (!tr) return '';
    if (!tr.available || !tr.data) return '<span class="td-dim">chưa có dữ liệu</span>';
    return rsVerdictHtml(tr.data.verdict);
}

function rsListHtml(ordered, selected, state, toggled) {
    const groups = RS_TIERS.filter(t => !state.tier || t.tier === state.tier);
    return groups.map(t => {
        const rows = ordered.filter(e => rsTierOf(e) === t.tier);
        const open = toggled[t.tier] !== undefined ? toggled[t.tier]
            : (t.tier !== RS_COLLAPSED_TIER || state.tier === t.tier || (selected && rsTierOf(selected) === t.tier));
        const head = `<button type="button" class="rs-group rs-group--${t.tier}" data-rs-group="${t.tier}" aria-expanded="${open}">`
            + `<span class="fold-chev" aria-hidden="true">›</span><span class="rs-dot"></span>${escapeHtml(t.label)} <span class="td-dim">${rows.length}</span>`
            + `${t.tier === RS_COLLAPSED_TIER ? '<span class="td-dim">· thu gọn sẵn</span>' : ''}</button>`;
        if (!open) return head;
        const body = rows.length ? rows.map(e => {
            const chosen = selected && e.id === selected.id;
            const meta = [e.market, e.round ? 'vòng ' + e.round : null].filter(Boolean).join(' · ');
            return `<button type="button" class="rs-item${chosen ? ' is-selected' : ''}" data-rs-id="${escapeHtml(e.id)}" aria-current="${chosen ? 'true' : 'false'}">`
                + `<span class="rs-item-name">${escapeHtml(e.name)}</span>`
                + `<span class="rs-item-state">${rsItemStateHtml(e)}</span>`
                + `<span class="rs-item-meta td-dim">${escapeHtml(meta)}</span></button>`;
        }).join('') : '<p class="rs-empty td-dim">Chưa có thuật toán nào ở bậc này.</p>';
        return head + body;
    }).join('');
}

function rsResearchHtml(r) {
    // The three stages of a study, in the order they were run; the registry's own words stay as written.
    const lines = [['is', 'Dữ liệu tìm luật', 'IS: những năm dùng để dò ra quy tắc'],
                   ['val', 'Dữ liệu kiểm lại', 'VAL: những năm chỉ dùng để kiểm, sau khi đã chốt quy tắc'],
                   ['hold', 'Dữ liệu để dành', 'HOLD: những năm cất riêng, chỉ mở một lần ở cuối']]
        .filter(([k]) => r && r[k]);
    if (!lines.length) return '<p class="td-dim">Sổ chưa ghi số nghiên cứu.</p>';
    return `<dl class="rs-dl">${lines.map(([k, label, title]) => `<dt title="${title}">${label} <span class="td-dim">${k.toUpperCase()}</span></dt>`
        + `<dd>${escapeHtml(r[k])}</dd>`).join('')}</dl>`
        + '<p class="rs-legend">R: lời/lỗ trung bình mỗi lệnh tính bằng số lần rủi ro (1 R = mất đúng khoảng stop). '
        + 't: độ tin cậy của con số đó, từ khoảng 2 trở lên mới khó là do may. Số viết theo sổ nghiên cứu (dấu phẩy là phần thập phân).</p>';
}

function rsStatsHtml(pairs) {
    return `<dl class="rs-stats">${pairs.map(([label, value, cls]) =>
        `<div><dt>${escapeHtml(label)}</dt><dd class="${cls || ''}">${value}</dd></div>`).join('')}</dl>`;
}

function rsTone(v) {
    return v === null || v === undefined ? '' : (Number(v) >= 0 ? 'pnl-positive' : 'pnl-negative');
}

/** The registered stop and promotion numbers of a rules candidate, in words. */
function rsRulesWords(rules) {
    if (!rules) return [];
    const out = [];
    if (rules.stop_t_after !== null && rules.stop_t_after !== undefined) {
        out.push(`Dừng nếu sau ${rules.stop_t_after} lệnh, t gộp (HOLD + kiểm chứng) ≤ ${rules.stop_t}.`);
    }
    if (rules.stop_cum_after) out.push(`Dừng nếu sau ${rules.stop_cum_after} lệnh, tổng ròng < 0.`);
    if (rules.floor_after) {
        out.push(`Dừng nếu sau ${rules.floor_after} lệnh, tổng ròng thấp hơn kỳ vọng theo VAL trừ 1,5 độ lệch chuẩn.`);
    }
    out.push(`Đủ điều kiện xét khi có ít nhất ${rules.promote_after} lệnh và t gộp ≥ ${rules.promote_t}.`);
    return out;
}

function rsCalendarHtml(g) {
    if (!g) return '';
    const cls = g.days_left <= 21 ? 'pnl-negative' : 'td-dim';
    return `<p class="rs-line ${cls}">Lịch mốc giá vàng: hiệu lực đến ${escapeHtml(g.valid_through)} `
        + `(còn ${escapeHtml(g.days_left)} ngày). Sau ngày đó bot ngừng đặt lệnh chờ; dựng lại khi biết kết quả funding tháng 12.</p>`;
}

function rsRulesTrackerHtml(tr, calendar) {
    const c = tr.data;
    const why = c.verdict === 'STOP' ? 'Lý do dừng' : 'Còn thiếu';
    return `<div class="rs-verdict-line">${rsVerdictHtml(c.verdict)}</div>`
        + rsStatsHtml([
            ['Lệnh kiểm chứng', escapeHtml(c.n)],
            ['TB ròng (bp)', rsNum(c.mean, 2, true), rsTone(c.mean)],
            ['Tổng ròng (bp)', rsNum(c.cum, 1, true), rsTone(c.n ? c.cum : null)],
            ['t gộp', `${rsNum(c.pooled_t, 2, true)} <span class="td-dim">(HOLD ${escapeHtml(c.hold_n)} lệnh)</span>`],
        ])
        + (c.reasons && c.reasons.length ? `<div class="td-dim">${why}</div>${rsListItemsHtml(c.reasons)}` : '')
        + `<div class="td-dim">Luật đã đăng ký</div>${rsListItemsHtml(rsRulesWords(tr.rules))}`
        + (c.manual && c.manual.length ? `<div class="td-dim">Chưa kiểm ở đây</div>${rsListItemsHtml(c.manual)}` : '')
        + (tr.key === 'gold_levels' ? rsCalendarHtml(calendar) : '')
        + '<p class="rs-line td-dim">Ròng là biến động giá khớp thật trừ phí 0,6 bp; t gộp ghép đợt HOLD đã đăng ký với các lệnh '
        + 'kiểm chứng. "Đủ điều kiện xét" chưa phải là nâng hạng.</p>';
}

function rsFillable(v) {
    return v === true ? 'Có' : (v === false ? '<span class="pnl-negative">Không</span>' : '<span class="td-dim">?</span>');
}

function rsBasisHtml(tr) {
    const b = tr.data || {};
    if (!tr.available) {
        return '<p class="td-dim">Chưa có dữ liệu.'
            + `${b.verdict_reason && b.verdict !== 'NO_DATA' ? ' ' + escapeHtml(b.verdict_reason) : ''}</p>`;
    }
    let html = b.has_secret === false
        ? '<p class="rs-warn">Chưa có API secret: chưa đo được lượng coin vay được và lãi vay.</p>' : '';
    html += `<div class="rs-verdict-line">${rsVerdictHtml(b.verdict)}`
        + `${b.verdict_reason ? ` <span>${escapeHtml(b.verdict_reason)}</span>` : ''}</div>`;
    html += rsStatsHtml([
        ['Tín hiệu', escapeHtml(b.signals)],
        ['Khớp được', escapeHtml(b.fillable)],
        ['Không khớp được', escapeHtml(b.not_fillable)],
        ['Chưa rõ vay', escapeHtml(b.unknown_borrow)],
        ['Tổng ròng (bp)', rsNum(b.cum_net_bp, 1, true), rsTone(b.cum_net_bp)],
        ['TB ròng (bp)', rsNum(b.mean_net_bp, 2, true), rsTone(b.mean_net_bp)],
        ['t gộp', rsNum(b.pooled_t, 2, true)],
    ]);
    const r = b.rules || {};
    const hold = r.hold || {};
    const words = [];
    if (r.stop_after !== undefined) {
        words.push(`Dừng nếu sau ${r.stop_after} tín hiệu, tổng ròng < 0, hoặc hơn `
            + `${rsNum(Number(r.stop_not_fillable_share) * 100, 0)} % tín hiệu không vay được coin.`);
    }
    if (r.promote_t !== undefined) {
        words.push(`Đủ điều kiện xét khi t gộp (HOLD + demo, chỉ lệnh vay được) ≥ ${r.promote_t}; đọc cùng lúc với luật dừng.`);
    }
    if (hold.n !== undefined) {
        words.push(`HOLD đã đăng ký: ${hold.n} lệnh, TB ${rsNum(hold.mean_bp, 2, true)} bp, t ${rsNum(hold.t, 2)}.`);
    }
    if (words.length) html += `<div class="td-dim">Luật đã đăng ký</div>${rsListItemsHtml(words)}`;
    const open = b.open || [];
    if (open.length) {
        html += `<div class="td-dim rs-sub">Đang mở (${open.length})</div><div class="table-wrap"><table class="data-table rs-table">`
            + '<thead><tr><th>Coin</th><th>Vào lúc</th><th>Chiết khấu (bp)</th><th>Đã giữ (giờ)</th></tr></thead><tbody>'
            + open.map(o => `<tr><td>${escapeHtml(o.coin)}</td><td>${escapeHtml(o.entry_time)}</td>`
                + `<td>${rsNum(o.d_bp, 1)}</td><td>${rsNum(o.hours_open, 1)}</td></tr>`).join('')
            + '</tbody></table></div>';
    }
    const closed = (b.closed || []).slice(0, RS_CLOSED_ROWS);
    if (closed.length) {
        html += `<div class="td-dim rs-sub">Tín hiệu đã đóng gần nhất (${closed.length})</div>`
            + '<div class="table-wrap"><table class="data-table rs-table"><thead><tr><th>Coin</th><th>Vào</th><th>Ra</th>'
            + '<th>Giữ (giờ)</th><th>Ròng đăng ký (bp)</th><th>Ròng sổ (bp)</th><th>Funding (bp)</th><th>Vay được</th>'
            + '<th>Lãi vay / năm</th><th>Lượng vay (USD)</th></tr></thead><tbody>'
            + closed.map(c => `<tr><td>${escapeHtml(c.coin)}</td><td>${escapeHtml(c.entry_time)}</td>`
                + `<td>${escapeHtml(c.exit_time)}</td><td>${rsNum(c.hold_h, 1)}</td>`
                + `<td class="${rsTone(c.net_bp_registered)}">${rsNum(c.net_bp_registered, 1, true)}</td>`
                + `<td class="${rsTone(c.net_bp_book)}">${rsNum(c.net_bp_book, 1, true)}</td>`
                + `<td>${rsNum(c.fund_bp, 1, true)}</td><td>${rsFillable(c.fillable)}</td>`
                + `<td>${c.borrow_rate_y === null || c.borrow_rate_y === undefined ? '–' : rsNum(Number(c.borrow_rate_y) * 100, 2) + ' %'}</td>`
                + `<td>${rsNum(c.inventory_usd, 0)}</td></tr>`).join('')
            + '</tbody></table></div>';
    } else if (!open.length) {
        html += '<p class="td-dim">Chưa có tín hiệu nào.</p>';
    }
    if (b.last_run) html += `<p class="rs-line td-dim">Lần chạy gần nhất: ${escapeHtml(b.last_run)}</p>`;
    if (b.last_error) html += `<p class="rs-line pnl-negative">Lỗi lần chạy đó: ${escapeHtml(b.last_error)}</p>`;
    return html;
}

function rsTrackerHtml(entry, data) {
    const tr = entry.tracker;
    if (!entry.forward || !tr) {
        // A live algorithm's forward check is its own real bots: send the reader to their results instead of
        // leaving the backtest numbers above as the only figures on screen.
        if (rsTierOf(entry) === 'live') return '<p class="rs-live-note">Không có bot kiểm chứng riêng: kết quả tiền thật '
            + 'của thuật toán này là kết quả các bot của nó. <a href="#docker" class="rs-link">Xem ở màn Bot (Theo rủi ro để so với R ở trên)</a></p>';
        return '<p class="td-dim">Không có bot kiểm chứng.</p>';
    }
    if (tr.kind === 'basis_b') return rsBasisHtml(tr);
    if (!tr.available || !tr.data) return `<p class="td-dim">${escapeHtml(tr.message || 'Chưa có dữ liệu.')}</p>`;
    return rsRulesTrackerHtml(tr, data && data.gold_calendar);
}

function rsDetailHtml(entry, data) {
    if (!entry) return '<section class="rs-detail"><p class="td-dim">Không có thuật toán nào khớp bộ lọc.</p></section>';
    const tier = rsTierOf(entry);
    const meta = [entry.market, entry.round ? 'vòng ' + entry.round : null].filter(Boolean).join(' · ');
    const files = [['Bot', entry.bot], ['Đăng ký trước', entry.prereg], ['Báo cáo', entry.report]].filter(([, v]) => v);
    return '<section class="rs-detail" aria-live="polite">'
        + `<div class="rs-detail-head"><h3>${escapeHtml(entry.name)}</h3>`
        + `<span class="rs-tier rs-tier--${tier}">${escapeHtml(rsTierLabel(tier))}</span>`
        + `<span class="td-dim rs-detail-meta">${escapeHtml(meta)}</span></div>`
        + `<div class="td-dim rs-id">${escapeHtml(entry.id)}</div>`
        + (entry.description ? `<p class="rs-desc">${escapeHtml(entry.description)}</p>` : '')
        + (entry.tier_reason ? `<p class="rs-line"><span class="td-dim">Vì sao ở bậc ${escapeHtml(rsTierLabel(tier))}:</span> ${escapeHtml(entry.tier_reason)}</p>` : '')
        + `<h4 class="rs-h">Kết quả nghiên cứu</h4>${rsResearchHtml(entry.research)}`
        + `<h4 class="rs-h">Kiểm chứng</h4>${rsTrackerHtml(entry, data)}`
        + (files.length ? `<h4 class="rs-h">Tệp</h4><dl class="rs-dl">${files.map(([k, v]) => `<dt>${k}</dt><dd>${rsCode(v)}</dd>`).join('')}</dl>` : '')
        + '</section>';
}

/** The rounds that did not pass, folded: one line until opened (the list and its detail above are the screen). */
function rsTriedHtml(tried, open) {
    if (!tried || !tried.length) return '';
    const body = open
        ? '<div class="table-wrap"><table class="data-table rs-table rs-table--wrap"><thead><tr><th>Vòng</th><th>Giả thuyết</th>'
            + '<th>Vì sao không đạt</th><th>Báo cáo</th></tr></thead><tbody>'
            + tried.map(t => `<tr><td>${escapeHtml(t.round || '')}</td><td>${escapeHtml(t.name || '')}</td>`
                + `<td>${escapeHtml(t.reason || '')}</td><td>${t.report ? rsCode(t.report) : ''}</td></tr>`).join('')
            + '</tbody></table></div>'
        : '';
    return `<section class="rs-fold"><button type="button" class="rs-fold-head" data-rs-tried="1" aria-expanded="${open}">`
        + `<span class="fold-chev" aria-hidden="true">›</span>`
        + `<span class="rs-fold-title">Đã thử, không đạt <span class="td-dim">${tried.length}</span></span>`
        + `<span class="td-dim">${tried.length} hướng đã kiểm và không qua cổng · chi tiết trong research/JOURNAL.md</span></button>${body}</section>`;
}

/** "Sổ research/registry.yaml · đọc lúc 14:05 01/11 giờ VN" (UTC+7 whatever the browser's zone). */
function rsMetaText(data) {
    const t = data && data.generated_at ? Date.parse(data.generated_at) : NaN;
    const at = Number.isNaN(t) ? null : new Date(t + 7 * 3600 * 1000);
    const p = n => String(n).padStart(2, '0');
    const when = at ? `${p(at.getUTCHours())}:${p(at.getUTCMinutes())} ${p(at.getUTCDate())}/${p(at.getUTCMonth() + 1)} giờ VN` : '–';
    return `Sổ ${(data && data.registry) || 'research/registry.yaml'} · đọc lúc ${when}`;
}

/** The title line: how many algorithms sit in each tier, and the trackers that hit a pre-registered rule.
 *  [css modifier, text]. */
function rsStatusOf(data) {
    const entries = (data && data.algorithms) || [];
    if (!entries.length) return ['', 'Sổ nghiên cứu chưa có thuật toán nào'];
    const c = rsCounts(entries);
    const verdicts = entries.map(e => e.tracker && e.tracker.available && e.tracker.data && e.tracker.data.verdict);
    const stop = verdicts.filter(v => v === 'STOP').length, promote = verdicts.filter(v => v === 'PROMOTE_CHECK').length;
    const flags = [stop ? `${stop} chạm luật dừng` : '', promote ? `${promote} đủ điều kiện xét nâng hạng` : ''].filter(Boolean);
    const text = `${c.live || 0} đang live · ${c.demo || 0} chạy demo · ${c['cho-kiem'] || 0} chờ kiểm`
        + (flags.length ? ` · ${flags.join(', ')}` : '');
    return [stop ? 'crit' : (promote ? 'warn' : 'ok'), text];
}

// ---------- DOM, fetch ----------

let rsData = null;
let rsState = {tier: null, q: '', id: null};
let rsToggled = {};          // list groups the user opened or closed
let rsTriedOpen = false;
let rsLoading = false;

function rsRender() {
    if (!rsData) return;
    const entries = rsData.algorithms || [];
    const {ordered, selected} = rsSelection(entries, rsState);
    document.getElementById('rs-meta').textContent = rsMetaText(rsData);
    const [cls, text] = rsStatusOf(rsData);
    const status = document.getElementById('rs-status');
    status.textContent = text;
    status.className = `ov-status${cls ? ` ov-status--${cls}` : ''}`;
    document.getElementById('rs-warning').innerHTML = rsData.warning
        ? `<p class="rs-warn">${escapeHtml(rsData.warning)}</p>` : '';
    document.getElementById('rs-chips').innerHTML = rsChipsHtml(rsCounts(rsFilter(entries, {q: rsState.q})), rsState);
    document.getElementById('rs-grid').innerHTML = entries.length
        ? `<nav class="rs-list" aria-label="Danh sách thuật toán">${rsListHtml(ordered, selected, rsState, rsToggled)}</nav>`
          + rsDetailHtml(selected, rsData)
        : '<p class="td-dim">Sổ nghiên cứu chưa có thuật toán nào.</p>';
    document.getElementById('rs-tried').innerHTML = rsTriedHtml(rsData.tried, rsTriedOpen);
}

function rsUpdate(patch) {
    rsState = {...rsState, ...patch};
    const hash = rsHashFor(rsState);
    if (location.hash !== hash) history.replaceState(null, '', hash);
    rsRender();
}

async function rsLoad() {
    if (rsLoading) return;
    rsLoading = true;
    try {
        const res = await fetch('/api/research');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        rsData = await res.json();
        rsRender();
    } catch (e) {
        document.getElementById('rs-grid').innerHTML =
            `<p class="pnl-negative">Không tải được trang nghiên cứu: ${escapeHtml(e.message)}</p>`;
        const status = document.getElementById('rs-status');
        status.textContent = 'Không đọc được sổ nghiên cứu';
        status.className = 'ov-status ov-status--warn';
    } finally {
        rsLoading = false;
    }
}

function rsOnShow() {
    rsState = rsParseHash(location.hash);
    const search = document.getElementById('rs-search');
    if (search && document.activeElement !== search) search.value = rsState.q;
    rsRender();
    rsLoad();
}

document.addEventListener('DOMContentLoaded', () => {
    const view = document.getElementById('view-research');
    if (!view) return;
    document.getElementById('rs-refresh-btn').addEventListener('click', rsLoad);
    document.getElementById('rs-search').addEventListener('input', e => rsUpdate({q: e.target.value}));
    view.addEventListener('click', e => {
        const el = e.target.closest('[data-rs-tier],[data-rs-id],[data-rs-group],[data-rs-tried]');
        if (!el || !view.contains(el)) return;
        if (el.hasAttribute('data-rs-tier')) {
            const tier = el.getAttribute('data-rs-tier') || null;
            rsUpdate({tier: rsState.tier === tier ? null : tier});
        } else if (el.hasAttribute('data-rs-group')) {
            const tier = el.getAttribute('data-rs-group');
            rsToggled = {...rsToggled, [tier]: el.getAttribute('aria-expanded') !== 'true'};
            rsRender();
        } else if (el.hasAttribute('data-rs-tried')) {
            rsTriedOpen = !rsTriedOpen;
            rsRender();
        } else {
            const id = el.getAttribute('data-rs-id');
            const entry = (rsData && rsData.algorithms || []).find(a => a.id === id);
            // A "Chờ kiểm" card may point at an entry the filter hides: clear the filter so the list shows it.
            const hidden = entry && !rsFilter([entry], rsState).length;
            if (hidden) {
                document.getElementById('rs-search').value = '';
                rsUpdate({id, tier: null, q: ''});
            } else {
                rsUpdate({id});
            }
            if (el.hasAttribute('data-rs-reveal')) document.getElementById('rs-grid').scrollIntoView({behavior: 'smooth', block: 'start'});
            // One column below 960 px: the detail sits under the whole list, so take the reader to it.
            else if (window.matchMedia('(max-width: 959px)').matches) {
                const detail = view.querySelector('.rs-detail');
                if (detail) detail.scrollIntoView({block: 'start'});
            }
        }
    });
});
