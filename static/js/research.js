/* Research view ("Nghiên cứu"): every researched algorithm from research/registry.yaml grouped by tier, the selected
 * one's detail, and the collapsed "Đã thử, không đạt" table (app/research_api.py, GET /api/research;
 * docs/research-screen.md). Written for a reader who is not a professional investor (2026-11-02): each row shows a
 * trend word and four period bars, the detail says what the rule does, whether it is holding up and its dated journey,
 * from research/plain.yaml; the registry's technical text is folded under "Số kỹ thuật". Since 2026-11-13 every
 * algorithm shares one detail frame ("Hồi research" next to "Dữ liệu mới", then "Theo kỳ"), as in 106.dnse-stock.
 *
 * Loaded with `defer`, after the dashboard script whose escapeHtml it uses. The functions above the DOM part are pure
 * (data in, HTML or values out) so tests/app/test_research_ui.py can run them in node with hostile strings.
 * Filter, search and the selected algorithm live in the hash: #research?tier=demo&q=ecb&id=F3. */

const RS_TIERS = [
    {tier: 'live', label: 'Tiền thật'},
    {tier: 'demo', label: 'Demo'},
    {tier: 'cho-kiem', label: 'Chờ anh quyết'},
    {tier: 'da-loai', label: 'Đã loại'},
];
// Bar value = mean x scale, in words a layman reads (spec 2026-11-02-research-plain-design.md, Units).
const RS_UNITS = {
    R: {scale: 100, caption: '$ lãi trên mỗi $100 chịu rủi ro', count: 'lệnh'},
    bp: {scale: 1, caption: '$ lãi trên mỗi $10.000 vào lệnh', count: 'lệnh'},
    pct_week: {scale: 1, caption: '% lãi mỗi tuần', count: 'tuần'},
    pct_year: {scale: 1, caption: '% lãi mỗi năm', count: ''},
};
const RS_PERIODS = [['is', 'Lúc tìm ra'], ['val', 'Kiểm lần 1'], ['hold', 'Kiểm cuối']];
const RS_REAL_MIN = 30;                  // real-run trades before its own numbers decide the trend
const RS_TRENDS = {up: '↗', flat: '→', down: '↘', unk: '?', out: '×'};
const RS_COLLAPSED_TIER = 'da-loai';      // collapsed when the page opens
const RS_CLOSED_ROWS = 10;                // latest closed basis B demo signals shown
// "Theo kỳ" rows (app/research_periods.py) and the trade count under which a period is for reference only.
const RS_PERIOD_ROWS = [['week', 'Tuần qua', false], ['month', 'Tháng qua', false], ['year', 'Năm qua', true]];
const RS_FEW = 5;

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
    const p = entry.plain || {};
    return rsFold([entry.id, entry.name, entry.description, entry.market, entry.round, p.name, p.what, p.why].join(' '))
        .includes(needle);
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

/** A tracker verdict that needs the owner (STOP, PROMOTE_CHECK), or null. */
function rsFlagOf(entry) {
    const tr = entry.tracker;
    const v = tr && tr.available && tr.data && tr.data.verdict;
    return v === 'STOP' || v === 'PROMOTE_CHECK' ? v : null;
}

/** The badge on a list row: only a tracker verdict that needs the owner; the trend word says the rest. */
function rsItemStateHtml(entry) {
    const flag = rsFlagOf(entry);
    return flag ? rsVerdictHtml(flag) : '';
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
            const trend = rsTrend(e);
            return `<button type="button" class="rs-item${chosen ? ' is-selected' : ''}" data-rs-id="${escapeHtml(e.id)}" aria-current="${chosen ? 'true' : 'false'}">`
                + `<span class="rs-item-name">${escapeHtml(rsPlainName(e))}</span>`
                + `<span class="rs-item-bars">${rsMiniBarsHtml(e)}</span>`
                + `<span class="rs-item-meta">${rsTrendHtml(trend)}${rsItemStateHtml(e)}</span></button>`;
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

/** The A2-D5L executor (app/a2_live_status.py): real-money trades on Binance, read from its own files. */
function rsA2Html(tr) {
    const a = tr.data || {};
    if (!tr.available) return '<p class="td-dim">Bộ đặt lệnh chưa chạy lần nào (chưa có sổ).</p>';
    const mode = a.mode === 'live'
        ? `<b>Tiền thật</b>${a.notional ? `, ${rsNum(a.notional, 0)} USDT/chân` : ''}${a.leverage ? `, đòn bẩy ${rsNum(a.leverage, 0)}` : ''}`
        : '<b>Chạy thử</b> (không gửi lệnh)';
    let html = `<p class="rs-line">${mode}${a.stopped ? ' · <span class="pnl-negative">đang tạm dừng (STOP_A2)</span>' : ''}</p>`;
    html += `<div class="rs-verdict-line">${rsVerdictHtml(a.verdict)}`
        + `${a.verdict_reason ? ` <span>${escapeHtml(a.verdict_reason)}</span>` : ''}</div>`;
    html += rsStatsHtml([
        ['Lệnh thật đã đóng', escapeHtml(a.n)],
        ['Tổng ròng (bp)', rsNum(a.cum_net_bp, 1, true), rsTone(a.cum_net_bp)],
        ['TB ròng (bp)', rsNum(a.mean_net_bp, 1, true), rsTone(a.mean_net_bp)],
        ['t gộp', rsNum(a.pooled_t, 2, true)],
        ['Thấy tin ≤ 3 giây', a.seen_le3_share === null || a.seen_le3_share === undefined ? '–'
            : rsNum(Number(a.seen_le3_share) * 100, 0) + ' %'],
        ['Bỏ qua', escapeHtml(a.skipped)],
    ]);
    const r = a.rules || {}, hold = r.hold || {};
    html += '<div class="td-dim">Luật đã đăng ký</div>' + rsListItemsHtml([
        `Đủ điều kiện xét khi t gộp (HOLD + lệnh thật) ≥ ${r.promote_t} sau ít nhất ${r.min_live} lệnh thật, `
            + `và thấy tin trong ${r.detect_s} giây ở ≥ ${rsNum(Number(r.detect_share) * 100, 0)} % lần.`,
        `HOLD đã đăng ký: ${hold.n} lệnh, TB ${rsNum(hold.mean_bp, 1, true)} bp, t ${rsNum(hold.t, 2)}.`,
    ]);
    const open = a.open || [];
    if (open.length) {
        html += `<div class="td-dim rs-sub">Đang mở (${open.length})</div><div class="table-wrap"><table class="data-table rs-table">`
            + '<thead><tr><th>Coin</th><th>Hợp đồng</th><th>Vào lúc (UTC)</th><th>USDT/chân</th><th>Chế độ</th></tr></thead><tbody>'
            + open.map(o => `<tr><td>${escapeHtml(o.coin)}</td><td>${escapeHtml(o.perp)}</td><td>${escapeHtml(o.entry_time)}</td>`
                + `<td>${rsNum(o.notional, 0)}</td><td>${o.mode === 'live' ? 'thật' : 'thử'}</td></tr>`).join('')
            + '</tbody></table></div>';
    }
    const closed = (a.closed || []).slice(0, RS_CLOSED_ROWS);
    if (closed.length) {
        html += `<div class="td-dim rs-sub">Thông báo gần nhất (${closed.length})</div>`
            + '<div class="table-wrap"><table class="data-table rs-table"><thead><tr><th>Tin (UTC)</th><th>Coin</th>'
            + '<th>Chế độ</th><th>Thấy tin (giây)</th><th>Vào (giây)</th><th>Trượt giá (bp)</th><th>Giữ (giờ)</th>'
            + '<th>Ròng (bp)</th><th>Ghi chú</th></tr></thead><tbody>'
            + closed.map(c => `<tr><td>${escapeHtml(c.post_time)}</td><td>${escapeHtml(c.coin)}</td>`
                + `<td>${c.mode === 'live' ? 'thật' : 'thử'}</td><td>${rsNum(c.seen_s, 1)}</td><td>${rsNum(c.entry_s, 1)}</td>`
                + `<td>${rsNum(c.slip_bp, 1, true)}</td><td>${rsNum(c.hold_h, 2)}</td>`
                + `<td class="${rsTone(c.net_bp)}">${rsNum(c.net_bp, 1, true)}</td>`
                + `<td class="td-dim">${escapeHtml(c.exit_reason === 'skipped' ? (c.note || 'bỏ qua') : (c.exit_reason || ''))}</td></tr>`).join('')
            + '</tbody></table></div>';
    } else if (!open.length) {
        html += '<p class="td-dim">Chưa có thông báo niêm yết nào từ lúc bộ đặt lệnh chạy.</p>';
    }
    html += '<p class="rs-line td-dim">Ròng = lãi chân long coin trừ chân short BTC theo giá khớp, trừ 20 bp phí như trong '
        + `nghiên cứu. Trượt giá = giá khớp so với giá chào bán ngay trước lệnh.${a.updated ? ` Sổ cập nhật ${escapeHtml(a.updated)} UTC.` : ''}</p>`;
    return html;
}

/** Real-money R of a live rule without a tracker of its own (app/live_r.py). */
function rsLiveRHtml(tr) {
    if (!tr.available || !tr.data) return `<p class="td-dim">${escapeHtml(tr.message || 'Chưa có dữ liệu.')}</p>`;
    const d = tr.data;
    return rsStatsHtml([
        ['Lệnh thật', escapeHtml(d.n)],
        ['TB mỗi lệnh (R)', rsNum(d.mean, 3, true), rsTone(d.mean)],
        ['t riêng lệnh thật', rsNum(d.forward_t, 2, true)],
        ['Bỏ qua (thiếu stop)', escapeHtml(d.skipped)],
    ]) + `<p class="rs-line td-dim">R tính từ giá khớp thật và khoảng stop của từng chân thật (bỏ chân nghi binh)${
        d.since ? `, từ ${escapeHtml(d.since)}` : ''}; đã có spread, chưa trừ phí hoa hồng.</p>`;
}

function rsTrackerHtml(entry, data) {
    const tr = entry.tracker;
    if (tr && tr.kind === 'live_r') return rsLiveRHtml(tr);
    if (!entry.forward || !tr) {
        // A live algorithm's forward check is its own real bots: send the reader to their results instead of
        // leaving the backtest numbers above as the only figures on screen.
        if (rsTierOf(entry) === 'live') return '<p class="rs-live-note">Không có bot kiểm chứng riêng: kết quả tiền thật '
            + 'của thuật toán này là kết quả các bot của nó. <a href="#bot" class="rs-link">Xem ở màn Bot (Theo rủi ro để so với R ở trên)</a></p>';
        return '<p class="td-dim">Không có bot kiểm chứng.</p>';
    }
    if (tr.kind === 'basis_b') return rsBasisHtml(tr);
    if (tr.kind === 'a2_live') return rsA2Html(tr);
    if (tr.kind === 'live_r') return rsLiveRHtml(tr);
    if (!tr.available || !tr.data) return `<p class="td-dim">${escapeHtml(tr.message || 'Chưa có dữ liệu.')}</p>`;
    return rsRulesTrackerHtml(tr, data && data.gold_calendar);
}

/** The detail, one frame for every algorithm whatever its tier (layout of 106.dnse-stock's research detail,
 *  2026-11-13): title, what / why, "Hồi research" next to "Dữ liệu mới", the trend verdict, the bar chart, "Theo kỳ",
 *  the journey, why it sits in its tier, then the folded technical numbers. A panel with no number keeps its place and
 *  says why in words, so the layout does not jump between algorithms. */
function rsDetailHtml(entry, data) {
    if (!entry) return '<section class="rs-detail"><p class="td-dim">Không có thuật toán nào khớp bộ lọc.</p></section>';
    const tier = rsTierOf(entry);
    const p = entry.plain || {};
    const trend = rsTrend(entry);
    const name = rsPlainName(entry);
    const sub = [name !== entry.name ? entry.name : null, entry.id].filter(Boolean).join(' · ');
    const meta = [entry.round ? 'Vòng ' + entry.round : null, entry.market].filter(Boolean).join(' · ');
    const what = p.what || entry.description;
    const plain = (what ? `<dt>Làm gì</dt><dd>${escapeHtml(what)}</dd>` : '')
        + (p.why ? `<dt>Vì sao có lãi</dt><dd>${escapeHtml(p.why)}</dd>` : '');
    const unit = rsUnitInfo(p.unit);
    const hasBars = rsBarValues(entry).some(v => v !== null);
    return '<section class="rs-detail" aria-live="polite">'
        + `<div class="rs-detail-head"><h3>${escapeHtml(name)}</h3>`
        + `<span class="rs-tier rs-tier--${tier}">${escapeHtml(rsTierLabel(tier))}</span>`
        + (meta ? `<span class="rs-detail-meta td-dim">${escapeHtml(meta)}</span>` : '') + '</div>'
        + `<div class="td-dim rs-id">${escapeHtml(sub)}</div>`
        + (plain ? `<dl class="rs-plain">${plain}</dl>` : '')
        + `<div class="rs-pair">${rsResearchPanelHtml(entry)}${rsForwardPanelHtml(entry)}</div>`
        + `<div class="rs-verdict rs-verdict--${trend.key}"><span class="rs-arrow" aria-hidden="true">${trend.arrow}</span>`
        + `<p><b>${escapeHtml(trend.word)}</b>${trend.sentence ? ' ' + escapeHtml(trend.sentence) : ''}</p></div>`
        + (hasBars && unit
            ? `<p class="rs-caption td-dim">Cột: ${escapeHtml(unit.caption)}, đã trừ phí như trong nghiên cứu${
                entry.tracker && entry.tracker.kind === 'live_r' && rsRealRun(entry)
                    ? '; cột chạy thật tính từ giá khớp, chưa trừ phí hoa hồng' : ''}.</p>`
              + rsPeriodChartHtml(entry)
            : '')
        + rsPeriodsHtml(entry)
        + `<h4 class="rs-h">Hành trình</h4>${rsJourneyHtml(p.history)}`
        + (entry.tier_reason ? `<p class="rs-line rs-why"><span class="td-dim">Vì sao ở bậc ${escapeHtml(rsTierLabel(tier))}:</span> ${escapeHtml(entry.tier_reason)}</p>` : '')
        + rsTechHtml(entry, data)
        + '</section>';
}

function rsPanelHtml(title, body) {
    return `<div class="rs-panel"><h4 class="rs-panel-title">${title}</h4>${body}</div>`;
}

function rsRowHtml(label, value) {
    return `<div class="rs-row"><span class="td-dim">${label}</span><span>${value}</span></div>`;
}

/** The panel's big number, coloured by sign, with its unit in words; "—" without a number. */
function rsBigHtml(value, unit) {
    if (value === null || value === undefined || !Number.isFinite(Number(value))) return '<div class="rs-big td-dim">—</div>';
    return `<div class="rs-big"><span class="${rsTone(value)}">${rsVi(value, true)}</span>`
        + (unit ? ` <small class="td-dim">${escapeHtml(unit.caption)}</small>` : '') + '</div>';
}

/** "dd/mm/yyyy" (or "dd/mm") from an ISO date; anything else as is. */
function rsDate(iso, withYear) {
    const d = String(iso || '');
    if (!/^\d{4}-\d{2}-\d{2}/.test(d)) return d;
    return `${d.slice(8, 10)}/${d.slice(5, 7)}` + (withYear === false ? '' : `/${d.slice(0, 4)}`);
}

/** The research figure the new data is compared with: the last study period that has a mean (kiểm cuối first). */
function rsResearchRef(entry) {
    const periods = (entry.plain && entry.plain.periods) || {};
    for (const [k, label] of RS_PERIODS.slice().reverse()) {
        const per = periods[k];
        if (per && per.mean !== null && per.mean !== undefined && Number.isFinite(Number(per.mean))) {
            return {key: k, label, mean: Number(per.mean), t: per.t, n: per.n, years: per.years};
        }
    }
    return null;
}

/** First day of the forward run, as the API and the chart read it from the journey. */
function rsSinceOf(entry) {
    if (entry.periods && entry.periods.since) return entry.periods.since;
    const kind = rsTierOf(entry) === 'live' ? 'live' : 'demo';
    return ((entry.plain && entry.plain.history) || []).find(h => h.kind === kind)?.date || null;
}

function rsResearchPanelHtml(entry) {
    const p = entry.plain || {};
    const unit = rsUnitInfo(p.unit);
    const ref = rsResearchRef(entry);
    if (!ref || !unit) {
        const r = entry.research || {};
        const text = r.hold || r.val || r.is;
        return rsPanelHtml('Hồi research', rsBigHtml(null)
            + '<p class="rs-panel-note">Sổ chưa có số của từng giai đoạn.</p>'
            + (text ? `<p class="rs-panel-note td-dim">Sổ ghi: ${escapeHtml(text)}</p>` : ''));
    }
    const periods = p.periods || {};
    const rows = RS_PERIODS.filter(([k]) => periods[k]).map(([k, label]) => {
        const per = periods[k];
        const n = per.n !== null && per.n !== undefined && unit.count ? ` · ${escapeHtml(per.n)} ${unit.count}` : '';
        return rsRowHtml(`${label}${per.years ? ' ' + escapeHtml(per.years) : ''}`,
            `<span class="${rsTone(per.mean)}">${rsVi(Number(per.mean) * unit.scale, true)}</span>${n}`
            + (per.t !== null && per.t !== undefined ? ` · t ${rsVi(per.t)}` : ''));
    }).join('');
    return rsPanelHtml(`Hồi research <span class="td-dim">${escapeHtml(ref.label.toLowerCase())}${ref.years ? ' ' + escapeHtml(ref.years) : ''}</span>`,
        rsBigHtml(ref.mean * unit.scale, unit) + rows
        + rsRowHtml('Độ chắc chắn', rsSureHtml(rsSure(ref.t))));
}

function rsForwardPanelHtml(entry) {
    const tier = rsTierOf(entry);
    const since = rsSinceOf(entry);
    const unit = rsUnitInfo(entry.plain && entry.plain.unit);
    const run = rsRealRun(entry);
    const title = ['live', 'demo'].includes(tier)
        ? `${escapeHtml(rsRunLabel(entry))}${since ? ` <span class="td-dim">từ ${escapeHtml(rsDate(since))}</span>` : ''}`
        : 'Dữ liệu mới';
    if (run) {
        const pct = run.target ? Math.min(100, run.n / run.target * 100) : null;
        return rsPanelHtml(title, rsBigHtml(run.mean * (unit ? unit.scale : 1), unit)
            + rsRowHtml('Số lệnh', `${escapeHtml(run.n)}${run.target ? ' / ' + escapeHtml(run.target) : ''}`)
            + rsRowHtml('Độ chắc chắn', rsSureHtml(rsSure(run.t, run.n)) + (run.t !== null ? ` · t ${rsVi(run.t)}` : ''))
            + (pct !== null
                ? `<div class="rs-progress" role="progressbar" aria-label="${escapeHtml(run.n)} trên ${escapeHtml(run.target)} lệnh" `
                  + `aria-valuemin="0" aria-valuemax="${escapeHtml(run.target)}" aria-valuenow="${escapeHtml(run.n)}">`
                  + `<b style="width:${pct.toFixed(1)}%"></b></div>`
                  + `<p class="rs-panel-note td-dim">Mốc xét theo luật đăng ký trước: ${escapeHtml(run.target)} lệnh.</p>`
                : ''));
    }
    let words;
    if (tier === 'cho-kiem') words = 'Chưa chạy: chờ anh quyết có cho chạy demo không.';
    else if (tier === 'da-loai') words = 'Đã loại, không chạy tiếp.';
    else if (entry.tracker && !entry.tracker.available) words = `${rsRunLabel(entry)}: chưa đọc được số.`;
    else if (entry.tracker && rsTrackerCount(entry.tracker) === 0) words = 'Chưa có lệnh nào đóng.';
    else if (entry.tracker) words = 'Bộ theo dõi tính ở đơn vị khác với số nghiên cứu: xem phần Số kỹ thuật.';
    else if (tier === 'live') return rsPanelHtml(title, rsBigHtml(null) + '<p class="rs-panel-note">Không có bot kiểm chứng riêng: '
        + 'kết quả tiền thật là kết quả các bot của nó. <a href="#bot" class="rs-link">Xem ở màn Bot</a></p>');
    else words = 'Chưa có bộ theo dõi lệnh demo.';
    return rsPanelHtml(title, rsBigHtml(null) + `<p class="rs-panel-note">${escapeHtml(words)}</p>`);
}

/** One period cell: words when the run had not started or had no trade, else mean · trades · t. */
function rsPeriodCellHtml(cell, scale) {
    if (!cell || !cell.covered) return '<span class="td-dim">Chưa chạy</span>';
    if (!cell.n) return '<span class="td-dim">0 lệnh</span>';
    const few = cell.n < RS_FEW;
    return `<b class="${few ? 'td-dim' : rsTone(cell.mean)}">${rsVi(Number(cell.mean) * scale, true)}</b>`
        + ` <span class="td-dim">· ${escapeHtml(cell.n)} lệnh${cell.n >= 2 && cell.t !== null && cell.t !== undefined ? ` · t ${rsVi(cell.t)}` : ''}</span>`
        + (few ? '<small class="rs-pt-note td-dim">ít lệnh, chỉ để tham khảo</small>' : '')
        + (cell.covered < cell.days ? `<small class="rs-pt-note rs-pt-cover">chạy ${escapeHtml(cell.covered)}/${escapeHtml(cell.days)} ngày</small>` : '');
}

function rsPeriodDiff(cell, research, scale) {
    if (research === null || !cell || !cell.covered || cell.n < RS_FEW || cell.mean === null) return null;
    return Number(cell.mean) * scale - research;
}

/** "Theo kỳ": the last week / month / year of the forward run against the period before it and the research figure.
 *  A flat table from 640 px, one card per period below that. */
function rsPeriodsHtml(entry) {
    const per = entry.periods;
    const tier = rsTierOf(entry);
    if (!per) {
        const words = entry.periods_note
            || (tier === 'cho-kiem' ? 'Chưa chạy nên chưa có số theo kỳ.'
                : tier === 'da-loai' ? 'Đã loại: không có lệnh mới để tính theo kỳ.'
                : 'Chưa có bộ theo dõi lệnh, nên chưa có số theo kỳ. Chưa có job chạy lại luật trên dữ liệu cũ.');
        return rsPanelHtml('Theo kỳ', `<p class="rs-panel-note">${escapeHtml(words)}</p>`);
    }
    const unit = rsUnitInfo(per.unit) || RS_UNITS.bp;
    const plainUnit = entry.plain && entry.plain.unit;
    const ref = plainUnit === per.unit ? rsResearchRef(entry) : null;
    const research = ref ? ref.mean * unit.scale : null;
    const researchText = research === null ? '–' : rsVi(research, true);
    const diffHtml = cell => {
        const d = rsPeriodDiff(cell, research, unit.scale);
        return d === null ? '–' : `<span class="${rsTone(d)}">${rsVi(d, true)}</span>`;
    };
    const range = (cell, year) => `${rsDate(cell.from, year)} – ${rsDate(cell.to, year)}`;
    const rows = RS_PERIOD_ROWS.map(([k, label, year]) => [k, label, year, per[k] || {}]);
    const table = '<div class="rs-pt-wrap"><table class="rs-pt"><thead><tr><th scope="col">Kỳ</th><th scope="col">Kỳ này</th>'
        + '<th scope="col">Kỳ liền trước</th><th scope="col">Research</th><th scope="col">Chênh với research</th></tr></thead><tbody>'
        + rows.map(([k, label, year, p]) => `<tr><th scope="row"><b>${label}</b>`
            + `<small class="td-dim">${p.current ? escapeHtml(range(p.current, year)) : ''}</small></th>`
            + `<td>${rsPeriodCellHtml(p.current, unit.scale)}</td><td>${rsPeriodCellHtml(p.previous, unit.scale)}</td>`
            + `<td>${researchText}</td><td>${diffHtml(p.current)}</td></tr>`).join('')
        + '</tbody></table></div>';
    const cards = '<div class="rs-pcards">' + rows.map(([k, label, year, p]) => '<div class="rs-pcard">'
        + `<div><b>${label}</b> <small class="td-dim">${p.current ? escapeHtml(range(p.current, year)) : ''}</small></div>`
        + rsRowHtml('Kỳ này', rsPeriodCellHtml(p.current, unit.scale))
        + rsRowHtml('Kỳ liền trước', rsPeriodCellHtml(p.previous, unit.scale))
        + rsRowHtml('Research', researchText) + rsRowHtml('Chênh với research', diffHtml(p.current))
        + '</div>').join('') + '</div>';
    const run = tier === 'live' ? 'tiền thật' : 'demo';
    return rsPanelHtml('Theo kỳ',
        `<p class="rs-panel-note td-dim">Lãi trung bình mỗi lệnh: ${escapeHtml(unit.caption)}. Kỳ tính theo ngày lịch, tới ${escapeHtml(rsDate(per.end))} (UTC).</p>`
        + table + cards
        + `<p class="rs-panel-note td-dim">Chỉ có lệnh chạy ${run}${per.since ? ` từ ${escapeHtml(rsDate(per.since))}` : ''}: `
        + 'chưa có job chạy lại luật trên dữ liệu trước đó. '
        + (ref ? `Research là ${escapeHtml(ref.label.toLowerCase())}${ref.years ? ' ' + escapeHtml(ref.years) : ''}.`
               : 'Sổ nghiên cứu không có số cùng đơn vị để so.') + '</p>');
}

/** Everything the detail showed before 2026-11-02, folded: IS / VAL / HOLD text, the tracker and the files. */
function rsTechHtml(entry, data) {
    const files = [['Bot', entry.bot], ['Đăng ký trước', entry.prereg], ['Báo cáo', entry.report]].filter(([, v]) => v);
    return '<details class="rs-tech"><summary class="rs-h"><span class="fold-chev" aria-hidden="true">›</span>'
        + 'Số kỹ thuật <span class="td-dim">t, bp, luật dừng, tệp nghiên cứu</span></summary>'
        + (entry.description && entry.plain && entry.plain.what ? `<p class="rs-desc">${escapeHtml(entry.description)}</p>` : '')
        + `<h4 class="rs-h">Kết quả nghiên cứu</h4>${rsResearchHtml(entry.research)}`
        + `<h4 class="rs-h">Kiểm chứng</h4>${rsTrackerHtml(entry, data)}`
        + (files.length ? `<h4 class="rs-h">Tệp</h4><dl class="rs-dl">${files.map(([k, v]) => `<dt>${k}</dt><dd>${rsCode(v)}</dd>`).join('')}</dl>` : '')
        + '</details>';
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
    const weak = entries.filter(e => rsTierOf(e) !== 'da-loai' && rsTrend(e).key === 'down').length;
    const text = `${c.live || 0} tiền thật · ${c.demo || 0} demo · ${c['cho-kiem'] || 0} chờ anh quyết`
        + (weak ? ` · ${weak} đang yếu đi` : '') + (flags.length ? ` · ${flags.join(', ')}` : '');
    return [stop ? 'crit' : (promote ? 'warn' : 'ok'), text];
}

// ---------- plain words: trend, certainty, bars, journey (pure) ----------

function rsPlainName(entry) {
    return (entry.plain && entry.plain.name) || entry.name || entry.id;
}

function rsUnitInfo(unit) {
    return RS_UNITS[unit] || null;
}

/** Vietnamese number: comma decimal, real minus sign, trailing zeros dropped; 0 decimals from 100, 1 from 10. */
function rsVi(v, signed) {
    if (v === null || v === undefined || !Number.isFinite(Number(v))) return '–';
    const n = Number(v), a = Math.abs(n);
    const text = a.toFixed(a >= 100 ? 0 : (a >= 10 ? 1 : 2)).replace(/\.?0+$/, '').replace('.', ',');
    return (n < 0 ? '−' : (signed && n > 0 ? '+' : '')) + text;
}

/** {level 0-4, word} for a t; a run under RS_REAL_MIN trades (n given) gets no certainty yet. */
function rsSure(t, n) {
    if (n !== null && n !== undefined && n < RS_REAL_MIN) return {level: 0, word: `mới ${n} lệnh, chưa đủ`};
    if (t === null || t === undefined || !Number.isFinite(Number(t))) return {level: 0, word: 'chưa có số'};
    if (t >= 3) return {level: 4, word: 'Rất chắc'};
    if (t >= 2) return {level: 3, word: 'Khá chắc'};
    if (t >= 1) return {level: 2, word: 'Chưa chắc'};
    if (t > -1) return {level: 1, word: 'Như may rủi'};
    return {level: 1, word: 'Lỗ khá rõ'};
}

function rsSureHtml(sure) {
    const boxes = [1, 2, 3, 4].map(i => `<i class="${i <= sure.level ? 'on' : ''}"></i>`).join('');
    return `<span class="rs-sure" aria-hidden="true">${boxes}</span> ${escapeHtml(sure.word)}`;
}

/** "Chạy thật" for a live rule, "Chạy demo" otherwise. */
function rsRunLabel(entry) {
    return rsTierOf(entry) === 'live' ? 'Chạy thật' : 'Chạy demo';
}

/** The forward run in the plain unit: {n, mean, t, target, label}, or null without trades or in another unit. */
function rsRealRun(entry) {
    const tr = entry.tracker;
    const unit = entry.plain && entry.plain.unit;
    if (!tr || !tr.available || !tr.data) return null;
    const d = tr.data;
    let run = null;
    if (tr.kind === 'rules' && unit === 'bp') {
        run = {n: d.n, mean: d.mean, t: d.forward_t, target: tr.rules ? tr.rules.promote_after : null};
    } else if (tr.kind === 'basis_b' && unit === 'bp') {
        run = {n: d.closed_n, mean: d.mean_net_bp, t: d.forward_t, target: d.rules ? d.rules.stop_after : null};
    } else if (tr.kind === 'a2_live' && unit === 'bp') {
        run = {n: d.n, mean: d.mean_net_bp, t: d.forward_t, target: d.rules ? d.rules.min_live : null};
    } else if (tr.kind === 'live_r' && unit === 'R') {
        run = {n: d.n, mean: d.mean, t: d.forward_t, target: null};
    }
    if (!run || !run.n || run.mean === null || run.mean === undefined) return null;
    return {...run, t: run.t === undefined ? null : run.t, label: rsRunLabel(entry)};
}

/** [lúc tìm ra, kiểm lần 1, kiểm cuối, chạy] in bar units (mean x scale), null where missing. */
function rsBarValues(entry) {
    const p = entry.plain || {};
    const unit = rsUnitInfo(p.unit);
    if (!unit) return [null, null, null, null];
    const periods = p.periods || {};
    const scaled = v => (v === null || v === undefined || !Number.isFinite(Number(v))) ? null : Number(v) * unit.scale;
    const run = rsRealRun(entry);
    return RS_PERIODS.map(([k]) => scaled(periods[k] && periods[k].mean)).concat([run ? scaled(run.mean) : null]);
}

/** Trend word from the research periods, or from the real run once it has RS_REAL_MIN trades (spec, Trend rule). */
function rsTrend(entry) {
    const p = entry.plain || {};
    const periods = p.periods || {};
    const num = v => (v === null || v === undefined || !Number.isFinite(Number(v))) ? null : Number(v);
    const is = num(periods.is && periods.is.mean), hold = num(periods.hold && periods.hold.mean);
    const holdT = num(periods.hold && periods.hold.t);
    const run = rsRealRun(entry);
    const real = run && run.n >= RS_REAL_MIN ? rsRealVerdict(run, is) : null;
    const noisy = Boolean(run && run.n >= RS_REAL_MIN && !real);
    let key, word;
    if (rsTierOf(entry) === 'da-loai') [key, word] = ['out', 'Đã loại'];
    else if (real) [key, word] = real;
    else if (is === null || hold === null) [key, word] = ['unk', 'Chưa rõ'];
    else if (is <= 0) [key, word] = hold <= 0 ? ['down', 'Yếu đi'] : ['unk', 'Chưa rõ'];
    else if (hold <= 0) [key, word] = ['down', 'Yếu đi'];
    else if (hold >= 1.25 * is && holdT !== null && holdT >= 2) [key, word] = ['up', 'Mạnh lên'];
    else if (hold >= 0.75 * is) [key, word] = ['flat', 'Giữ vững'];
    else if (hold >= 0.4 * is) [key, word] = ['down', 'Yếu dần'];
    else [key, word] = ['down', 'Yếu đi'];
    return {key, arrow: RS_TRENDS[key], word, sentence: rsTrendSentence(entry, is, hold, run, noisy)};
}

/** [key, word] from a forward run of RS_REAL_MIN+ trades, or null when it cannot overrule the research: no positive
 *  "lúc tìm ra" mean to compare with, no t, or a shortfall under one standard error (a few dozen legs are mostly
 *  noise next to a small edge; Gotobi's 42 live legs on 2026-11-02 sit 0,8 se under its research mean). */
function rsRealVerdict(run, is) {
    if (is === null || is <= 0 || !run.t) return null;
    if (run.mean >= is && run.t >= 2) return ['up', 'Mạnh lên'];
    if (run.mean >= 0.5 * is) return ['flat', 'Giữ vững'];
    const se = Math.abs(run.mean / run.t);
    if ((run.mean - is) / se > -1) return null;
    return run.mean <= 0 ? ['down', 'Yếu đi'] : ['down', 'Yếu dần'];
}

/** Trades the forward tracker has, whatever their unit: null when it cannot be read. */
function rsTrackerCount(tr) {
    if (!tr || !tr.available || !tr.data) return null;
    const n = tr.kind === 'basis_b' ? tr.data.closed_n : tr.data.n;
    return Number.isFinite(Number(n)) ? Number(n) : null;
}

function rsTrendSentence(entry, is, hold, run, noisy) {
    const parts = [];
    const flag = rsFlagOf(entry);
    if (flag === 'STOP') parts.push('Đã chạm luật dừng đăng ký trước.');
    if (flag === 'PROMOTE_CHECK') parts.push('Đủ điều kiện xét nâng hạng, chờ anh quyết.');
    if (is !== null && hold !== null && is > 0) {
        parts.push(hold <= 0 ? 'Lần kiểm cuối bị lỗ.' : `Kiểm cuối lãi bằng ${Math.round(hold / is * 100)}% lúc tìm ra.`);
    }
    const unit = rsUnitInfo(entry.plain && entry.plain.unit);
    if (run) {
        parts.push(run.n < RS_REAL_MIN
            ? `${run.label}: ${run.n}${run.target ? '/' + run.target : ''} lệnh, chưa đủ để kết luận.`
            : `${run.label}: ${run.n} lệnh, trung bình ${rsVi(run.mean * (unit ? unit.scale : 1), true)} `
              + `(${rsSure(run.t).word.toLowerCase()})${noisy ? ', chưa đủ chắc để đổi kết luận' : ''}.`);
    } else if (entry.tracker && ['live', 'demo'].includes(rsTierOf(entry))) {
        // Only say "no trades" when the tracker says so; a tracker in another unit says nothing here.
        const count = rsTrackerCount(entry.tracker);
        if (!entry.tracker.available) parts.push(`${rsRunLabel(entry)}: chưa đọc được số.`);
        else if (count === 0) parts.push(`${rsRunLabel(entry)}: chưa có lệnh nào.`);
    }
    if (entry.plain && entry.plain.note) parts.push(entry.plain.note);
    return parts.join(' ');
}

function rsTrendHtml(trend) {
    return `<span class="rs-trend rs-trend--${trend.key}"><span aria-hidden="true">${trend.arrow}</span> ${escapeHtml(trend.word)}</span>`;
}

/** Four tiny bars for a list row (one scale per row); a missing period is a flat dash. */
function rsMiniBarsHtml(entry) {
    const vals = rsBarValues(entry);
    const known = vals.filter(v => v !== null);
    if (!known.length) return '';
    const w = 64, h = 22, mid = h / 2, bw = w / 4 - 4;
    const max = Math.max(...known.map(Math.abs)) || 1;
    const bars = vals.map((v, i) => {
        const x = i * (w / 4) + 2;
        if (v === null) return `<rect x="${x}" y="${mid - 1}" width="${bw}" height="2" fill="var(--border)"></rect>`;
        const bh = Math.max(2, Math.abs(v) / max * (mid - 1));
        return `<rect x="${x}" y="${(v >= 0 ? mid - bh : mid).toFixed(1)}" width="${bw}" height="${bh.toFixed(1)}" rx="1.5" `
            + `fill="var(${v >= 0 ? '--profit' : '--loss'})"${i === 3 ? '' : ' opacity="0.7"'}></rect>`;
    }).join('');
    return `<svg class="rs-mini" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" aria-hidden="true">`
        + `<line x1="0" x2="${w}" y1="${mid}" y2="${mid}" stroke="var(--border)"></line>${bars}</svg>`;
}

/** The detail's bar chart: one bar per period on one scale, value on the bar, years and count under it. */
function rsPeriodChartHtml(entry) {
    const p = entry.plain || {};
    const unit = rsUnitInfo(p.unit) || RS_UNITS.bp;
    const periods = p.periods || {};
    const run = rsRealRun(entry);
    const vals = rsBarValues(entry);
    const known = vals.filter(v => v !== null);
    const pos = Math.max(0, ...known.filter(v => v > 0)), neg = Math.max(0, ...known.filter(v => v < 0).map(Math.abs));
    // A negative bar prints its value under itself: keep that row clear of the period labels.
    const W = 520, top = 26, bottom = neg > 0 ? 76 : 58, H = 134 + bottom, L = 6, R = 6, plotH = H - top - bottom;
    const span = (pos + neg) || 1, zeroY = top + plotH * pos / span, colW = (W - L - R) / 4, bw = Math.min(64, colW * 0.5);
    const since = ((p.history || []).find(h => h.kind === (rsTierOf(entry) === 'live' ? 'live' : 'demo')) || {}).date;
    const cols = RS_PERIODS.map(([k, label]) => [label, periods[k] ? periods[k].years : null, periods[k] ? periods[k].n : null])
        .concat([[rsRunLabel(entry), since ? 'từ ' + since.slice(8, 10) + '/' + since.slice(5, 7) : null, run ? run.n : null]]);
    let svg = `<svg class="rs-chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="Lãi qua các giai đoạn: ${
        escapeHtml(cols.map(([label], i) => `${label} ${rsVi(vals[i], true)}`).join(', '))}">`;
    cols.forEach(([label, years, n], i) => {
        const cx = L + colW * i + colW / 2, v = vals[i];
        if (v === null) {
            svg += `<text class="rs-chart-none" x="${cx}" y="${(zeroY - 8).toFixed(1)}" text-anchor="middle">chưa có</text>`;
        } else {
            const bh = Math.max(2, Math.abs(v) / span * plotH), y = v >= 0 ? zeroY - bh : zeroY;
            svg += `<rect x="${(cx - bw / 2).toFixed(1)}" y="${y.toFixed(1)}" width="${bw.toFixed(1)}" height="${bh.toFixed(1)}" rx="4" `
                + `fill="var(${v >= 0 ? '--profit' : '--loss'})"${i === 3 ? '' : ' opacity="0.8"'}></rect>`
                + `<text class="rs-chart-val" x="${cx}" y="${(v >= 0 ? y - 6 : y + bh + 14).toFixed(1)}" text-anchor="middle">${rsVi(v, true)}</text>`;
        }
        // Three short lines under each bar (label, years, count) so a phone can draw them large without overlap.
        const count = n !== null && n !== undefined && unit.count ? `${n} ${unit.count}` : '';
        svg += `<text class="rs-chart-label" x="${cx}" y="${H - 38}" text-anchor="middle">${escapeHtml(label)}</text>`
            + `<text class="rs-chart-sub" x="${cx}" y="${H - 22}" text-anchor="middle">${escapeHtml(years || '')}</text>`
            + `<text class="rs-chart-sub" x="${cx}" y="${H - 6}" text-anchor="middle">${escapeHtml(count)}</text>`;
    });
    return svg + `<line x1="${L}" x2="${W - R}" y1="${zeroY.toFixed(1)}" y2="${zeroY.toFixed(1)}" stroke="var(--border)"></line></svg>`;
}

/** The dated journey, oldest first; dd/mm/yyyy dates. */
function rsJourneyHtml(history) {
    if (!history || !history.length) return '<p class="td-dim">Sổ chưa ghi mốc thời gian.</p>';
    return `<ol class="rs-journey">${history.map(h => {
        const d = String(h.date || '');
        const when = /^\d{4}-\d{2}-\d{2}$/.test(d) ? `${d.slice(8, 10)}/${d.slice(5, 7)}/${d.slice(0, 4)}` : d;
        return `<li class="rs-ev rs-ev--${escapeHtml(h.kind)}"><span class="rs-ev-date">${escapeHtml(when)}</span>`
            + `<span class="rs-ev-dot" aria-hidden="true"></span><span>${escapeHtml(h.text || '')}</span></li>`;
    }).join('')}</ol>`;
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
