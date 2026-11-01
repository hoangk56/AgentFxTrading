// Dashboard page script (moved out of templates/dashboard.html).
// Server-rendered data comes from window.DASHBOARD_BOOTSTRAP, set inline by the template.
const DASHBOARD_BOOTSTRAP = window.DASHBOARD_BOOTSTRAP || {};

        // --- Sidebar Toggle & Navigation ---
        const sidebar = document.getElementById('app-sidebar');
        const sidebarToggleBtn = document.getElementById('sidebar-toggle-btn');
        if (sidebar && sidebarToggleBtn) {
            // Only restore collapsed state on desktop screens (>= 1024px)
            if (window.innerWidth >= 1024 && localStorage.getItem('sidebar_collapsed') === 'true') {
                sidebar.classList.add('collapsed');
                document.body.classList.add('sidebar-collapsed');
            }
            sidebarToggleBtn.addEventListener('click', () => {
                sidebar.classList.toggle('collapsed');
                document.body.classList.toggle('sidebar-collapsed');
                localStorage.setItem('sidebar_collapsed', sidebar.classList.contains('collapsed'));
            });
        }

        function switchView(targetId) {
            // Remove active class from nav items, topbar action buttons, and views
            document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
            document.querySelectorAll('.topbar-action-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.view-section').forEach(view => view.classList.remove('active'));

            // Add active to matching nav item or topbar button. Views without their own menu item light their parent's:
            // Dự đoán AI and Backtest are tabs of Nghiên cứu, the full ranking hangs off Bot (redesign D).
            const NAV_PARENT = {'view-paper-desk': 'view-research', 'view-backtest': 'view-research', 'view-leaderboard': 'view-docker'};
            const activeNav = document.querySelector(`.nav-item[data-target="${NAV_PARENT[targetId] || targetId}"]`);
            if (activeNav) activeNav.classList.add('active');
            const activeTopbarBtn = document.querySelector(`.topbar-action-btn[data-target="${targetId}"]`);
            if (activeTopbarBtn) activeTopbarBtn.classList.add('active');

            // Show corresponding view
            const targetView = document.getElementById(targetId);
            if (targetView) {
                targetView.classList.add('active');
                if (targetId === 'view-logs') {
                    // "Nhật ký" on an Overview alert lands on #logs?q=<bot>: filter to that bot.
                    const q = new URLSearchParams(location.hash.split('?')[1] || '').get('q');
                    if (q) logFilterInput.value = q;
                    fetchAgentLogs(logDateSelect.value);
                } else if (targetId === 'view-docker') {
                    fetchBots();
                } else if (targetId === 'view-leaderboard') {
                    fetchLeaderboard();
                } else if (targetId === 'view-backtest') {
                    btOnShow();
                } else if (targetId === 'view-ledger') {
                    ledgerOnShow();
                } else if (targetId === 'view-calendar') {
                    gotobiOnShow();
                } else if (targetId === 'view-research') {
                    rsOnShow();
                } else if (targetId === 'view-paper-desk') {
                    pdOnShow();
                }
            }
        }

        // The open view lives in the URL hash (#backtest, #ledger, …; Overview has none),
        // so F5 and Back/Forward stay on it. A view may keep its own state after "?" (#research?id=…).
        function viewFromHash(hash) {
            // #gotobi was the Calendar's hash before it took the ECB window trades too, #forward the Research
            // view's before it became "Nghiên cứu"; old links still open them.
            const aliases = {gotobi: 'calendar', forward: 'research'};
            const name = hash.slice(1).split('?')[0];
            const view = hash.length > 1 ? document.getElementById('view-' + (aliases[name] || name)) : null;
            return view && view.classList.contains('view-section') ? view.id : 'view-dashboard';
        }

        function openView(targetId) {
            if (viewFromHash(location.hash) !== targetId) {
                history.pushState(null, '', targetId === 'view-dashboard'
                    ? location.pathname + location.search
                    : '#' + targetId.replace(/^view-/, ''));
            }
            switchView(targetId);
        }

        // Menu items and the Nghiên cứu tabs open views the same way.
        document.querySelectorAll('.nav-item[data-target], .rs-tab[data-target]').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                openView(item.getAttribute('data-target'));
            });
        });

        window.addEventListener('popstate', () => switchView(viewFromHash(location.hash)));
        // Wait for DOMContentLoaded: switchView's loaders live further down this file and in the deferred
        // backtest.js / ledger.js.
        document.addEventListener('DOMContentLoaded', () => {
            const initialView = viewFromHash(location.hash);
            if (initialView !== 'view-dashboard') switchView(initialView);
        });
        // --- Bot screen (redesign D step 2, 2026-11-01) ---
        // Real bots first, Demo folded; each row: what it trades, its state in words, its size per trade, what it
        // holds and its result for the chosen period (GET /api/leaderboard, the former Xếp hạng screen). One main
        // button by state, Sửa, the rest under ⋯. The pure functions below run in node in the XSS tests.
        let botsFetchInFlight = false;   // a slow poll must not stack up behind itself
        let botActionInFlight = false;  // a pending action owns the table until it finishes
        let botResults = {};            // bot_id -> leaderboard row for the chosen period
        let botsDemoIssues = 0;
        const BOT_SIZING = [['RiskPerTradeMoney', 'Rủi ro mỗi lệnh ($)'], ['MaxLotsPerTrade', 'Lot tối đa mỗi lệnh'], ['Lots', 'Lot mỗi lệnh']];

        /** --Key=value of a docker run command (quotes dropped), or null. */
        function botParam(cmd, key) {
            const m = String(cmd || '').match(new RegExp(`--${key}=("?)([^"\\s\\\\]*)\\1`));
            return m ? m[2] : null;
        }
        /** The command with --Key set to value: replaced where it is, appended when missing. */
        function setBotParam(cmd, key, value) {
            const s = String(cmd || '');
            const re = new RegExp(`(--${key}=)("?)[^"\\s\\\\]*\\2`);
            return re.test(s) ? s.replace(re, (all, flag, q) => `${flag}${q}${value}${q}`) : `${s.replace(/\s+$/, '')} --${key}=${value}`;
        }
        function botSizingHtml(cmd) {
            const risk = botParam(cmd, 'RiskPerTradeMoney'), maxLots = botParam(cmd, 'MaxLotsPerTrade'), lots = botParam(cmd, 'Lots');
            if (risk !== null && risk !== '') {
                const n = Number(risk);
                const money = Number.isFinite(n) ? `$${n.toLocaleString('en-US', {maximumFractionDigits: 2})}` : escapeHtml(risk);
                return money + (maxLots ? `<span class="bot-sub">tối đa ${escapeHtml(maxLots)} lot</span>` : '');
            }
            if (lots !== null && lots !== '') return `${escapeHtml(lots)} lot`;
            return '<span class="td-dim">—</span>';
        }
        /** State in words (never colour alone): [css modifier, text, tooltip]. */
        function botState(b) {
            const running = b.status === 'running';
            if (b.stuck) return ['crit', 'Bị treo', b.health_reason || ''];
            if (b.status === 'error') return ['crit', 'Lỗi Docker', b.health_reason || ''];
            if (!running) return b.stopped_on_purpose
                ? ['off', 'Đã dừng', `Container ở trạng thái ${b.status || 'không rõ'}, dừng từ dashboard`]
                : ['crit', 'Dừng bất thường', `Container ở trạng thái ${b.status || 'không rõ'} mà không ai bấm Dừng`];
            if (!b.polling) {
                const age = (b.last_poll_age_s === null || b.last_poll_age_s === undefined)
                    ? 'từ lúc server khởi động' : `trong ${b.last_poll_age_s} giây`;
                return ['warn', 'Không nhận lệnh', `Bot "${b.bot_id || b.name}" không hỏi lệnh ${age}. Nút Đóng và Đóng & dừng không tới được bot này, Tạm dừng có thể không chặn được lệnh mới. Nguyên nhân thường gặp: bot còn đang đăng nhập, file .algo build trước khi có tính năng hỏi lệnh, CommandPollMs=0, hoặc bot báo BotId khác với --BotId của container.`];
            }
            if (b.paused) return ['warn', 'Tạm dừng', 'Đã chặn vào lệnh mới từ dashboard; lệnh đang mở vẫn được bot quản lý'];
            return ['ok', 'Đang chạy', ''];
        }
        // Stuck, a Docker error, or running but deaf to commands. A stopped bot may be stopped on purpose (the
        // Overview's Cần làm flags the ones nobody stopped); a paused one is the owner's choice.
        /** The one line under a warning state, readable by touch and keyboard (the long text was a tooltip only). */
        function botReasonShort(b) {
            if (b.stuck) return b.health_reason || 'watchdog thấy bot không chạy tiếp';
            if (b.status === 'error') return 'không đọc được trạng thái container';
            if (b.status !== 'running') return b.stopped_on_purpose ? '' : `container ${b.status || 'không rõ'}, chưa ai bấm Dừng`;
            if (!b.polling) return b.last_poll_age_s == null ? 'chưa hỏi lệnh từ lúc server chạy' : `không hỏi lệnh ${b.last_poll_age_s} giây`;
            if (b.paused) return 'không vào lệnh mới';
            return '';
        }
        function botNeedsAction(b) { return botState(b)[0] === 'crit' || (b.status === 'running' && !b.polling); }
        function botResultCells(r) {
            if (!r || !Number(r.total_trades)) return '<td class="num td-dim" data-label="Lời/lỗ">—</td><td class="num td-dim" data-label="Số lệnh">0</td><td class="num td-dim" data-label="Hệ số lời">—</td>';
            const pnl = Number(r.total_pnl_usd) || 0;
            // A profit factor of one or two trades is noise (0.00 after one loss): shown from 5 closed trades.
            const pf = Number(r.total_trades) < 5 ? '<span class="td-dim" title="Cần ít nhất 5 lệnh đã đóng">ít lệnh</span>'
                : (r.profit_factor === null || r.profit_factor === undefined || !Number.isFinite(Number(r.profit_factor))
                    ? '—' : Number(r.profit_factor).toFixed(2));
            return `<td class="num ${pnl > 0 ? 'pnl-positive' : pnl < 0 ? 'pnl-negative' : ''}" data-label="Lời/lỗ">${signedMoney(pnl)}</td>`
                + `<td class="num" data-label="Số lệnh">${escapeHtml(r.total_trades || 0)}</td><td class="num" data-label="Hệ số lời">${pf}</td>`;
        }
        function botRowHtml(b, r) {
            const name = escapeHtml(b.name);
            const live = b.account_type === 'live' ? '1' : '0';
            const symbol = botParam(b.run_command, 'symbol') || '';
            const data = `data-name="${name}" data-live="${live}" data-symbol="${escapeHtml(symbol)}" data-open="${escapeHtml(b.open_positions || 0)}"`;
            const [stateCls, stateText, stateTitle] = botState(b);
            const running = b.status === 'running';
            const btn = (cls, label, extra = '') => `<button type="button" class="log-btn ${cls}" ${data}${extra}>${label}</button>`;
            let primary;
            if (b.stuck || (running && !b.polling)) primary = btn('action-restart bot-btn-primary', 'Khởi động lại');
            else if (!running) primary = btn('action-start bot-btn-primary', 'Chạy');
            else if (b.paused) primary = btn('action-resume', 'Tiếp tục');
            else primary = btn('action-pause', 'Tạm dừng');
            const edit = `<button type="button" class="log-btn action-edit" ${data} data-desc="${escapeHtml(b.description || '')}" data-cmd="${escapeHtml(b.run_command || '')}">Sửa</button>`;
            const more = [];
            if (running && !primary.includes('action-restart')) more.push(btn('action-restart', 'Khởi động lại'));
            if (running) more.push(btn('action-close-stop', 'Đóng &amp; dừng'));
            if (running) more.push(btn('action-stop', 'Dừng'));
            more.push(btn('action-delete bot-btn-danger', 'Xoá bot'));
            const containerLine = b.container_id ? `<span class="row-menu-note">Container ${escapeHtml(String(b.container_id).substring(0, 12))}</span>` : '';
            const menu = `<details class="row-menu"><summary class="log-btn" aria-label="Thao tác khác với ${name}">Khác</summary>`
                + `<div class="row-menu-list">${more.join('')}${containerLine}</div></details>`;
            return `<tr data-row-name="${name}">
                <td><div class="bot-main">${escapeHtml(strategyName(b.bot_id || b.name))} ${escapeHtml(symbol.toUpperCase())}</div>
                    <div class="bot-sub" title="${escapeHtml(b.description || '')}">${name}</div></td>
                <td><span class="bot-state bot-state--${stateCls}">${stateText}</span>${stateCls === 'crit' || stateCls === 'warn'
                    ? `<span class="bot-sub bot-reason">${escapeHtml(botReasonShort(b))}</span>` : ''}${stateTitle ? `<span class="sr-only">${escapeHtml(stateTitle)}</span>` : ''}</td>
                <td class="num" data-label="Rủi ro / lệnh">${botSizingHtml(b.run_command)}</td>
                <td class="num" data-label="Đang giữ">${escapeHtml(b.open_positions || 0)}</td>
                ${botResultCells(r)}
                <td class="bot-actions">${primary}${edit}${menu}</td>
            </tr>`;
        }
        /** Sizing flags that differ between two commands: [{text: 'Rủi ro mỗi lệnh $2,000 → $1,500', ratio}]. */
        function botSizingChanges(before, after) {
            const word = {RiskPerTradeMoney: 'Rủi ro mỗi lệnh', MaxLotsPerTrade: 'Lot tối đa', Lots: 'Lot mỗi lệnh'};
            const show = (key, v) => key === 'RiskPerTradeMoney' ? `$${Number(v).toLocaleString('en-US', {maximumFractionDigits: 2})}` : `${v}`;
            return Object.keys(word).map(key => [key, botParam(before, key), botParam(after, key)])
                .filter(([, a, b]) => b !== null && Number(a) !== Number(b))
                .map(([key, a, b]) => ({ratio: a === null || !Number(a) ? Infinity : Number(b) / Number(a),
                                        text: `${word[key]} ${a === null ? 'chưa đặt' : show(key, a)} → ${show(key, b)}`}));
        }
        function botSizingFieldsHtml(cmd) {
            return BOT_SIZING.filter(([key]) => botParam(cmd, key) !== null).map(([key, label]) =>
                `<label class="bot-field" for="bot-size-${key}">${label}
                    <input type="number" step="any" min="0" id="bot-size-${key}" class="log-input" data-param="${key}" value="${escapeHtml(botParam(cmd, key))}">
                </label>`).join('');
        }
        function botsSay(text, bad) {
            const el = document.getElementById('bots-msg');
            if (!el) return;
            el.textContent = text || '';
            el.className = `bots-msg${bad ? ' bots-msg--bad' : ''}`;
        }

        async function fetchBots() {
            if (botsFetchInFlight || botActionInFlight) return;
            botsFetchInFlight = true;
            try {
                const period = (document.getElementById('bots-period') || {}).value || '1m';
                const lb = type => fetch(`/api/leaderboard?account_id=${type}&account_type=${type}&period=${encodeURIComponent(period)}`)
                    .then(r => r.ok ? r.json() : null).catch(() => null);
                const [res, live, demo] = await Promise.all([fetch("/api/bots"), lb('live'), lb('demo')]);
                const data = await res.json();
                // Each call ranks every bot (zeros for the other mode's), so take a bot's row from its own mode only.
                const isLive = id => /(^|[-_])live([-_]|$)/i.test(String(id || ''));
                botResults = {};
                ((live && live.rankings) || []).forEach(r => { if (isLive(r.bot_id)) botResults[r.bot_id] = r; });
                ((demo && demo.rankings) || []).forEach(r => { if (!isLive(r.bot_id)) botResults[r.bot_id] = r; });
                renderBots(data.bots, data.docker_available);
            } catch(e) {
                const status = document.getElementById("bots-status");
                if (status) {
                    status.textContent = `Không tải được danh sách bot lúc ${new Date().toLocaleTimeString('vi-VN', {hour: '2-digit', minute: '2-digit'})}, sẽ thử lại sau 10 giây`;
                    status.className = 'ov-status ov-status--warn';
                }
            }
            finally { botsFetchInFlight = false; }
        }
        function renderBots(bots, dockerOk) {
            const realBody = document.getElementById("bots-tbody");
            const demoBody = document.getElementById("bots-tbody-demo");
            const status = document.getElementById("bots-status");
            const say = (cls, text) => { if (status) { status.textContent = text; status.className = `ov-status ov-status--${cls}`; } };
            if(!dockerOk) {
                const msg = `<tr><td colspan="8" class="pnl-negative">Server không có Docker. Hãy kiểm tra Docker daemon đang chạy.</td></tr>`;
                realBody.innerHTML = msg;
                if (demoBody) demoBody.innerHTML = msg;
                say('crit', 'Không có Docker: không kiểm tra, chạy hay khởi động lại bot được');
                return;
            }
            const list = bots || [];
            const real = list.filter(b => b.account_type === 'live'), demo = list.filter(b => b.account_type !== 'live');
            const rows = group => group.map(b => botRowHtml(b, botResults[b.bot_id])).join('');
            realBody.innerHTML = real.length ? rows(real)
                : '<tr><td colspan="8" class="td-dim">Chưa có bot tiền thật nào. Bấm "Cài bot từ mẫu" hoặc "Thêm bot".</td></tr>';
            if (demoBody) demoBody.innerHTML = demo.length ? rows(demo) : '<tr><td colspan="8" class="td-dim">Chưa có bot demo nào.</td></tr>';
            const realIssues = real.filter(botNeedsAction).length;
            const demoIssues = demo.filter(botNeedsAction).length;
            const realCount = document.getElementById('bots-real-count');
            if (realCount) realCount.textContent = `${real.length} bot · ${real.filter(b => b.status === 'running').length} đang chạy`;
            const figs = document.getElementById('bots-demo-figs');
            if (figs) figs.innerHTML = `<span><b>${demo.length}</b> bot</span><span><b>${demo.filter(b => b.status === 'running').length}</b> đang chạy</span>`
                + `<span><b>${demo.reduce((s, b) => s + (Number(b.open_positions) || 0), 0)}</b> lệnh đang giữ</span>`
                + (demoIssues ? `<span class="pnl-negative">${demoIssues} cần xử lý</span>` : '');
            say(realIssues ? 'crit' : (demoIssues ? 'warn' : 'ok'),
                (realIssues ? `${realIssues} bot tiền thật cần xử lý` : 'Bot tiền thật chạy bình thường')
                + (demoIssues ? ` · Demo có ${demoIssues} bot cần xử lý` : ''));
            const demoBox = document.getElementById('bots-demo');
            if (demoBox && demoIssues > botsDemoIssues) demoBox.open = true;   // a new Demo problem opens the fold once
            botsDemoIssues = demoIssues;
            if (window.lucide) window.lucide.createIcons();
            focusBotFromHash();
        }
        // #docker?bot=<name> (Overview alert, Telegram link): open its fold and mark the row once.
        let botsFocused = '';
        function focusBotFromHash() {
            const want = new URLSearchParams(location.hash.split('?')[1] || '').get('bot');
            if (!want || want === botsFocused || !location.hash.startsWith('#docker')) return;
            const row = Array.from(document.querySelectorAll('#view-docker tr[data-row-name]')).find(r => r.dataset.rowName === want);
            if (!row) return;
            botsFocused = want;
            const fold = row.closest('details');
            if (fold) fold.open = true;
            row.classList.add('bot-row--focus');
            row.scrollIntoView({block: 'center'});
        }

        const BOT_ACTION_PENDING = { start: "Đang chạy…", stop: "Đang dừng…", restart: "Đang khởi động lại…", delete: "Đang xoá…",
                                     pause: "Đang tạm dừng…", resume: "Đang tiếp tục…", "close-and-stop": "Đang đóng và dừng…" };
        // Docker stop/restart wait up to 10 s for the cBot to exit; lock the row and say so meanwhile.
        function lockBotRow(btn, action) {
            const buttons = btn ? Array.from(btn.closest("tr").querySelectorAll("button")) : [];
            buttons.forEach(b => { b.disabled = true; });
            if (btn) btn.textContent = BOT_ACTION_PENDING[action] || "Đang xử lý…";
            botActionInFlight = true;
            return () => { botActionInFlight = false; buttons.forEach(b => { b.disabled = false; }); fetchBots(); };
        }
        const BOT_CONFIRM = {
            start: ['Chạy', 'Docker chạy container với lệnh đã lưu; bot đăng nhập lại cTrader trong khoảng một phút.'],
            restart: ['Khởi động lại', 'Docker dừng rồi chạy lại container; bot đăng nhập lại cTrader trong khoảng một phút. Lệnh đang mở vẫn nằm ở sàn cùng stop của nó.'],
            stop: ['Dừng', 'Container dừng: bot không vào lệnh mới và không quản lý lệnh đang mở nữa (stop ở sàn vẫn còn).'],
        };
        async function actionBot(name, action, btn) {
            const d = (btn && btn.dataset) || {};
            if (BOT_CONFIRM[action]) {
                const [verb, base] = BOT_CONFIRM[action];
                const held = Number(d.open) || 0;
                const body = held && action === 'stop'
                    ? `Bot đang giữ ${held} lệnh. ${base} Muốn đóng lệnh trước thì dùng Đóng & dừng.` : base;
                const ok = await askConfirm({title: `${verb} ${name}?`, body, ok: verb,
                                             live: d.live === '1', typeWord: confirmWordFor(name, d.symbol)});
                if (!ok) return;
            }
            const unlock = lockBotRow(btn, action);
            try {
                const res = await fetch(`/api/bots/${encodeURIComponent(name)}/${action}`, { method: "POST" });
                const data = await res.json();
                const done = `${BOT_ACTION_PENDING[action].replace('Đang ', 'Đã ').replace('…', '')}: ${name}`
                    + (action === 'start' || action === 'restart' ? ', bot đang đăng nhập lại cTrader (khoảng một phút)' : '');
                botsSay(data.success ? done : `Không được: ${data.message || 'lỗi'}`, !data.success);
            } catch(e) { botsSay(`Không được: ${e}`, true); }
            finally { unlock(); }
        }
        // Kill switch: pause, close every position the bot holds, then stop the container. The server
        // stops it only when the bot confirms every close; otherwise it keeps running, paused.
        async function closeAndStopBot(btn) {
            const d = btn.dataset;
            const name = d.name;
            const ok = await askConfirm({
                title: `Đóng ${d.open || 0} lệnh của ${name} rồi dừng?`,
                body: 'Bot được tạm dừng trước, các lệnh đang mở đóng theo giá thị trường. Nếu có lệnh không đóng được, container vẫn chạy (đang tạm dừng) để còn quản lý stop.',
                ok: 'Đóng & dừng', live: d.live === '1', typeWord: confirmWordFor(name, d.symbol),
            });
            if (!ok) return;
            const unlock = lockBotRow(btn, "close-and-stop");
            try {
                const res = await fetch(`/api/bots/${encodeURIComponent(name)}/close-and-stop`, { method: "POST" });
                const data = await res.json();
                botsSay(data.message || (data.success ? "Xong" : "Lỗi"), !data.success);
            } catch(e) { botsSay(`Không được: ${e}`, true); }
            finally { unlock(); }
        }
        async function deleteBot(name, btn) {
            const d = (btn && btn.dataset) || {};
            const held = Number(d.open) || 0;
            const ok = await askConfirm({title: `Xoá bot ${name}?`, body: (held ? `Bot đang giữ ${held} lệnh. ` : '') + 'Container của bot bị dừng và xoá, cấu hình của nó bị bỏ. Lệnh đang mở vẫn nằm ở sàn nhưng không còn bot quản lý.',
                                         ok: 'Xoá bot', live: d.live === '1', typeWord: confirmWordFor(name, d.symbol)});
            if (!ok) return;
            const unlock = lockBotRow(btn, "delete");
            try {
                const res = await fetch(`/api/bots/${encodeURIComponent(name)}`, { method: "DELETE" });
                const data = await res.json();
                botsSay(data.success ? `Đã xoá ${name}` : (data.message || "Lỗi khi xoá bot"), !data.success);
            } catch(e) { botsSay(`Không được: ${e}`, true); }
            finally { unlock(); }
        }
        function openBotEditor(btn) {
            const d = btn.dataset;
            document.getElementById("setup-panel").style.display = "none";
            document.getElementById("bot-form-mode").value = "edit";
            document.getElementById("bot-form-title").textContent = `Sửa ${strategyName(d.name)} ${String(d.symbol || '').toUpperCase()}`.trim();
            const nameInput = document.getElementById("bot-name");
            nameInput.value = d.name;
            nameInput.disabled = true; // Bot name is key, don't change in-place
            document.getElementById("bot-desc").value = d.desc;
            document.getElementById("bot-cmd").value = d.cmd;
            document.getElementById("bot-form-container").dataset.live = d.live;
            document.getElementById("bot-form-container").dataset.symbol = d.symbol;
            document.getElementById("bot-form-container").dataset.origCmd = d.cmd;
            // A live bot reads its flags at start: a saved-only change would show a size it does not trade.
            document.getElementById("save-bot-btn").style.display = d.live === '1' ? 'none' : '';
            document.querySelectorAll('.bot-row--editing').forEach(r => r.classList.remove('bot-row--editing'));
            const editedRow = btn.closest('tr');
            if (editedRow) editedRow.classList.add('bot-row--editing');
            const sizing = document.getElementById("bot-sizing");
            sizing.innerHTML = botSizingFieldsHtml(d.cmd);
            document.getElementById("bot-cmd-advanced").open = !sizing.innerHTML;
            document.getElementById("bot-form-msg").textContent = "";
            document.getElementById("save-restart-bot-btn").style.display = "inline-flex";
            const form = document.getElementById("bot-form-container");
            form.style.display = "flex";
            form.scrollIntoView({block: 'start'});
            (sizing.querySelector('input') || document.getElementById("bot-cmd")).focus();
        }
        // The sizing fields write straight into the command, so what is saved is what the advanced box shows.
        document.getElementById("bot-sizing").addEventListener("input", e => {
            const input = e.target.closest('input[data-param]');
            if (!input || input.value === '') return;
            const cmd = document.getElementById("bot-cmd");
            cmd.value = setBotParam(cmd.value, input.dataset.param, input.value);
        });
        document.getElementById("view-docker").addEventListener("click", e => {
            const btn = e.target.closest("button[data-name]");
            if (!btn || btn.disabled) return;
            const name = btn.dataset.name;
            const menu = btn.closest('details.row-menu');
            if (menu) { menu.open = false; menu.querySelector('summary').focus(); }   // the dialog returns focus here
            if (btn.classList.contains("action-edit")) return openBotEditor(btn);
            if (btn.classList.contains("action-close-stop")) return closeAndStopBot(btn);
            if (btn.classList.contains("action-delete")) return deleteBot(name, btn);
            for (const action of ["start", "stop", "restart", "pause", "resume"]) {
                if (btn.classList.contains(`action-${action}`)) return actionBot(name, action, btn);
            }
        });
        document.addEventListener("keydown", e => {
            if (e.key !== 'Escape') return;
            document.querySelectorAll('#view-docker details.row-menu[open]').forEach(m => { m.open = false; m.querySelector('summary').focus(); });
        });
        // One ⋯ menu open at a time; a click elsewhere closes it.
        document.addEventListener("click", e => {
            document.querySelectorAll('#view-docker details.row-menu[open]').forEach(m => { if (!m.contains(e.target)) m.open = false; });
        });
        document.querySelectorAll('.bots-period-head').forEach(th => { th.textContent = `Lời/lỗ ${document.getElementById("bots-period").selectedOptions[0].textContent}`; });
        document.getElementById("bots-period").addEventListener("change", () => {
            const label = document.getElementById("bots-period").selectedOptions[0].textContent;
            document.querySelectorAll('.bots-period-head').forEach(th => { th.textContent = `Lời/lỗ ${label}`; });
            fetchBots();
        });

        async function submitBotForm(restart = false) {
            const mode = document.getElementById("bot-form-mode").value;
            const name = document.getElementById("bot-name").value.trim();
            const desc = document.getElementById("bot-desc").value.trim();
            const cmd = document.getElementById("bot-cmd").value.trim();
            const msg = document.getElementById("bot-form-msg");
            const form = document.getElementById("bot-form-container");
            msg.textContent = "";
            if (!name || !cmd) { msg.textContent = "Cần nhập tên bot và lệnh chạy."; return; }
            const bad = Array.from(document.querySelectorAll('#bot-sizing input')).find(i => !(Number(i.value) > 0));
            if (bad) { msg.textContent = `${bad.closest('label').firstChild.textContent.trim()} phải lớn hơn 0.`; bad.focus(); return; }
            if (mode === "edit" && restart) {
                const changes = botSizingChanges(form.dataset.origCmd || '', cmd);
                const big = changes.some(c => c.ratio >= 2 || c.ratio <= 0.5);
                const ok = await askConfirm({
                    title: changes.length ? changes.map(c => c.text).join(' · ') : `Lưu và khởi động lại ${name}?`,
                    body: (big ? 'Mức mới gấp đôi hoặc chỉ còn một nửa mức cũ: kiểm lại số trước khi xác nhận. ' : '')
                        + `${name}: container được tạo lại với lệnh mới (dừng, xoá, chạy lại); bot đăng nhập lại cTrader trong khoảng một phút. Lệnh đang mở vẫn nằm ở sàn cùng stop của nó.`,
                    ok: 'Lưu và khởi động lại', live: form.dataset.live === '1', typeWord: confirmWordFor(name, form.dataset.symbol)});
                if (!ok) return;
            }
            const formButtons = form.querySelectorAll('.bot-form-actions button');
            formButtons.forEach(b => { b.disabled = true; });
            try {
                let res, data;
                if (mode === "edit") {
                    res = await fetch(`/api/bots/${encodeURIComponent(name)}/update`, {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify({ description: desc, run_command: cmd, restart: restart })
                    });
                } else {
                    res = await fetch("/api/bots", {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify({ name: name, description: desc, run_command: cmd })
                    });
                }
                data = await res.json();
                if (!data.success) { msg.textContent = data.message || "Lỗi khi lưu bot"; return; }
                form.style.display = "none";
                document.querySelectorAll('.bot-row--editing').forEach(r => r.classList.remove('bot-row--editing'));
                botsSay(restart ? `Đã lưu và khởi động lại ${name}` : `Đã lưu ${name}${mode === 'edit' ? ' (có hiệu lực khi khởi động lại)' : ''}`);
                fetchBots();
            } catch(e) {
                msg.textContent = "Lỗi khi lưu bot: " + e;
            } finally {
                formButtons.forEach(b => { b.disabled = false; });
            }
        }

        // --- Setup Instances (presets from app/cbot_presets.py) ---
        const SETUP_NEW_ACCOUNT = "__new__";
        let setupPresets = null;      // {strategies, symbols, cells} from /api/setup/presets
        let setupAccounts = [];       // from /api/ctrader-accounts
        const setupEl = (id) => document.getElementById(id);
        const setupEscape = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

        async function fetchSetupPresets() {
            if (setupPresets) return setupPresets;
            const res = await fetch("/api/setup/presets");
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            setupPresets = await res.json();
            return setupPresets;
        }

        async function fetchCtraderAccounts(selectId = null) {
            try {
                const res = await fetch("/api/ctrader-accounts");
                setupAccounts = (await res.json()).accounts || [];
            } catch (e) { console.error("Error fetching cTrader accounts", e); setupAccounts = []; }
            const sel = setupEl("setup-account");
            let html = `<option value="">— chọn tài khoản —</option>`;
            setupAccounts.forEach(a => {
                html += `<option value="${a.id}">${a.account_type === 'live' ? 'THẬT' : 'DEMO'} · ${setupEscape(a.label)} (${setupEscape(a.account_number)})</option>`;
            });
            html += `<option value="${SETUP_NEW_ACCOUNT}">＋ Tài khoản mới…</option>`;
            sel.innerHTML = html;
            sel.value = selectId !== null ? String(selectId) : (setupAccounts.length ? "" : SETUP_NEW_ACCOUNT);
            onSetupAccountChange();
        }

        function onSetupAccountChange() {
            const v = setupEl("setup-account").value;
            setupEl("setup-new-account").style.display = v === SETUP_NEW_ACCOUNT ? "block" : "none";
            setupEl("setup-account-delete").style.display = (v && v !== SETUP_NEW_ACCOUNT) ? "inline-flex" : "none";
            updateSetupCreateState();
        }

        function renderSetupGrid(p) {
            const strategies = Object.keys(p.strategies);
            const cellMap = {};
            p.cells.forEach(c => { cellMap[`${c.symbol}|${c.strategy}`] = c; });
            setupEl("setup-grid-head").innerHTML = `<th>Cặp</th>` + strategies.map(s =>
                `<th style="text-align:center"><label style="cursor:pointer; white-space:nowrap;"><input type="checkbox" class="setup-col-all" data-strategy="${s}" title="Chọn tất cả ${setupEscape(p.strategies[s].label)}"> ${setupEscape(p.strategies[s].label)}</label></th>`
            ).join("");
            setupEl("setup-grid-body").innerHTML = p.symbols.map(sym => {
                const tds = strategies.map(s => {
                    const c = cellMap[`${sym}|${s}`];
                    if (!c) return `<td style="text-align:center" class="td-dim">–</td>`;
                    return `<td style="text-align:center"><input type="checkbox" class="setup-cell" data-symbol="${sym}" data-strategy="${s}" title="${c.period} · ${setupEscape(c.session)}"><div class="setup-cell-note" data-symbol="${sym}" data-strategy="${s}"></div></td>`;
                }).join("");
                return `<tr><td><strong>${sym}</strong></td>${tds}</tr>`;
            }).join("");
            document.querySelectorAll("#setup-grid .setup-cell").forEach(cb => cb.addEventListener("change", updateSetupCreateState));
            document.querySelectorAll("#setup-grid .setup-col-all").forEach(cb => cb.addEventListener("change", () => {
                document.querySelectorAll(`#setup-grid .setup-cell[data-strategy="${cb.dataset.strategy}"]`).forEach(c => { c.checked = cb.checked; });
                updateSetupCreateState();
            }));
        }

        // Which accounts already have a bot config for each cell: a small "👤 label" line under the
        // checkbox, full detail on hover. Updates the note slots only, so the user's ticks survive.
        async function refreshSetupInstalled() {
            let installed = [];
            try {
                const res = await fetch("/api/setup/installed");
                if (res.ok) installed = (await res.json()).installed || [];
            } catch (e) { console.error("Error fetching installed instances", e); }
            const byCell = {};
            installed.forEach(r => { const k = `${r.symbol}|${r.strategy}`; (byCell[k] = byCell[k] || []).push(r); });
            document.querySelectorAll("#setup-grid .setup-cell-note").forEach(note => {
                const rows = byCell[`${note.dataset.symbol}|${note.dataset.strategy}`] || [];
                if (!rows.length) { note.textContent = ""; note.title = ""; return; }
                note.textContent = "👤 " + rows.map(r => r.account_label).join(", ");
                note.title = "Đã tạo cho:\n" + rows.map(r =>
                    `${r.name} · ${r.account_type === 'live' ? 'THẬT' : 'DEMO'} · ${r.account_label}`).join("\n");
            });
        }

        function selectedSetupCells() {
            return Array.from(document.querySelectorAll("#setup-grid .setup-cell:checked"))
                .map(cb => ({ symbol: cb.dataset.symbol, strategy: cb.dataset.strategy }));
        }

        function updateSetupCreateState() {
            const v = setupEl("setup-account").value;
            setupEl("setup-create-btn").disabled = !(v && v !== SETUP_NEW_ACCOUNT && selectedSetupCells().length > 0);
        }

        async function openSetupPanel() {
            setupEl("bot-form-container").style.display = "none";
            setupEl("setup-panel").style.display = "flex";
            setupEl("setup-results").innerHTML = "";
            try {
                renderSetupGrid(await fetchSetupPresets());
            } catch (e) {
                setupEl("setup-grid-body").innerHTML = `<tr><td class="td-dim" style="color:var(--loss)">Không tải được mẫu bot: ${setupEscape(e)}</td></tr>`;
            }
            await fetchCtraderAccounts();
            await refreshSetupInstalled();
        }

        async function saveCtraderAccount() {
            const msg = setupEl("setup-account-msg");
            const body = {
                label: setupEl("setup-acc-label").value.trim(),
                ctid_email: setupEl("setup-acc-email").value.trim(),
                password: setupEl("setup-acc-password").value,
                account_number: setupEl("setup-acc-number").value.trim(),
                account_type: document.querySelector('input[name="setup-acc-type"]:checked').value,
            };
            msg.textContent = "Đang lưu…";
            try {
                const res = await fetch("/api/ctrader-accounts", {
                    method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)
                });
                const data = await res.json();
                if (!res.ok || !data.success) { msg.textContent = data.message || `Lỗi ${res.status}`; return; }
                msg.textContent = "";
                setupEl("setup-acc-password").value = "";
                await fetchCtraderAccounts(data.account.id);
            } catch (e) { msg.textContent = "Lỗi: " + e; }
        }

        async function deleteCtraderAccount() {
            const id = setupEl("setup-account").value;
            const acc = setupAccounts.find(a => String(a.id) === id);
            if (!acc) return;
            if (!confirm(`Xoá tài khoản "${acc.label}" (${acc.account_number})?\nCác bot đã cài vẫn chạy; file mật khẩu đã lưu sẽ bị xoá.`)) return;
            try {
                const res = await fetch(`/api/ctrader-accounts/${id}`, { method: "DELETE" });
                const data = await res.json();
                if (!data.success) alert(data.message || "Error");
                await fetchCtraderAccounts();
            } catch (e) { alert("Error: " + e); }
        }

        async function createSetupInstances() {
            const btn = setupEl("setup-create-btn");
            const list = setupEl("setup-results");
            const payload = {
                account_id: Number(setupEl("setup-account").value),
                selections: selectedSetupCells(),
                start: !setupEl("setup-save-only").checked,
            };
            btn.disabled = true;
            list.innerHTML = `<li class="td-dim">Đang tạo ${payload.selections.length} bot…</li>`;
            try {
                const res = await fetch("/api/setup/instances", {
                    method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (!res.ok) { list.innerHTML = `<li style="color:var(--loss)">❌ ${setupEscape(data.message || `HTTP ${res.status}`)}</li>`; return; }
                const icons = { started: "✅", saved: "💾", exists: "⏭", error: "❌" };
                list.innerHTML = (data.results || []).map(r =>
                    `<li>${icons[r.status] || "•"} <strong>${setupEscape(r.name || r.symbol)}</strong> <span class="td-dim">${setupEscape(r.symbol)} · ${setupEscape(r.strategy)}</span> — ${setupEscape(r.message || r.status)}</li>`
                ).join("");
                document.querySelectorAll("#setup-grid input[type=checkbox]:checked").forEach(cb => { cb.checked = false; });
                fetchBots();
                await refreshSetupInstalled();
            } catch (e) {
                list.innerHTML = `<li style="color:var(--loss)">Lỗi: ${setupEscape(e)}</li>`;
            } finally {
                updateSetupCreateState();
            }
        }

        document.addEventListener("DOMContentLoaded", () => {
            fetchBots();
            setInterval(fetchBots, 10000); // Auto-refresh bot status
            
            const formContainer = document.getElementById("bot-form-container");
            document.getElementById("add-bot-btn").addEventListener("click", () => {
                setupEl("setup-panel").style.display = "none";
                document.getElementById("bot-form-mode").value = "add";
                document.getElementById("bot-form-title").textContent = "Thêm cấu hình bot";
                const nameInput = document.getElementById("bot-name");
                nameInput.value = "";
                nameInput.disabled = false;
                document.getElementById("bot-desc").value = "";
                document.getElementById("bot-cmd").value = "";
                document.getElementById("bot-sizing").innerHTML = "";
                document.getElementById("bot-cmd-advanced").open = true;
                document.getElementById("bot-form-msg").textContent = "";
                formContainer.dataset.live = ""; formContainer.dataset.symbol = "";
                document.getElementById("save-restart-bot-btn").style.display = "none";
                document.getElementById("save-bot-btn").style.display = "";
                formContainer.style.display = "flex";
            });
            document.getElementById("cancel-bot-btn").addEventListener("click", () => formContainer.style.display = "none");

            document.getElementById("save-bot-btn").addEventListener("click", () => submitBotForm(false));
            document.getElementById("save-restart-bot-btn").addEventListener("click", () => submitBotForm(true));

            setupEl("setup-instances-btn").addEventListener("click", openSetupPanel);
            setupEl("setup-cancel-btn").addEventListener("click", () => { setupEl("setup-panel").style.display = "none"; });
            setupEl("setup-account").addEventListener("change", onSetupAccountChange);
            setupEl("setup-account-save").addEventListener("click", saveCtraderAccount);
            setupEl("setup-account-delete").addEventListener("click", deleteCtraderAccount);
            setupEl("setup-create-btn").addEventListener("click", createSetupInstances);
        });
        function formatMoney(v) {
            if (v === null || v === undefined) return "$0.00";
            const n = Number(v) || 0;
            const sign = n < 0 ? "-$" : "$";
            return `${sign}${Math.abs(n).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        }
        function pnlClass(v){return Number(v)>=0?'kpi-value--profit':'kpi-value--loss'}
        function accountBadge(t){return t==='live'?'<span class="badge badge--live"><span class="badge-dot"></span>THẬT</span>':'<span class="badge badge--demo"><span class="badge-dot"></span>DEMO</span>'}   // also used by ledger.js
        // Mirrors the side_chip macro: Mua / Bán, anything else shown as sent.
        function sideChip(s){const c=s==='BUY'?'side-chip--buy':'side-chip--sell';const t=s==='BUY'?'Mua':(s==='SELL'?'Bán':escapeHtml(s));return `<span class="side-chip ${c}">${t}</span>`}
        // "+$12.30" / "-$4.00" / "$0.00".
        function signedMoney(v){const n=Number(v)||0;return `${n>0?'+':''}${formatMoney(n)}`}
        // Single renderer for the P&L cell, shared by the row builder and the live tick handler.
        // Only the broker's own figure is shown; a missing one reads as "—" rather than a guess.
        function pnlCellHtml(pnl, pips){
            if(pnl===null||pnl===undefined){
                return '<span class="td-dim" title="Lời/lỗ từ sàn sẽ có khi bot gửi báo cáo tiếp theo">—</span>';
            }
            const v=Number(pnl)||0, p=Number(pips)||0;
            return `<span class="pos-money ${v>=0?'pnl-positive':'pnl-negative'}">${signedMoney(v)}</span> <span class="pos-pips">${p>0?'+':''}${p.toFixed(1)}p</span>`;
        }
        function escapeHtml(v){return String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
        // One SL or TP line: the price plus the bot's P&L estimate at it. Rows written before
        // prices were recorded fall back to the entry-time pip distance. noTp: the bot has taken
        // the TP off (a trailed runner), so the trade exits only at its stop. Mirrors the sltp_line macro.
        function sltpLineHtml(tag, price, pnl, pips, noTp){
            let body;
            if(price){
                body=`<span class="td-mono">${escapeHtml(price)}</span>`;
                if(pnl!==null&&pnl!==undefined){
                    const v=Number(pnl)||0;
                    body+=` <span class="${v>=0?'pnl-positive':'pnl-negative'}">${v>0?'+':(v<0?'-':'')}$${Math.abs(v).toFixed(2)}</span>`;
                    if(tag==='SL'&&v>0){
                        body+=noTp
                            ? '<span class="sltp-chip" title="Stop dời theo giá: bot kéo stop theo sau giá. Lệnh đóng khi giá quay lại chạm stop, vẫn giữ được khoản lời này.">dời theo giá</span>'
                            : '<span class="sltp-chip" title="Stop đã qua điểm hoà vốn: nếu giá quay lại chạm stop, lệnh vẫn đóng với khoản lời này.">đã khoá lời</span>';
                    }
                }
            } else if(noTp){
                body='<span class="sltp-none" title="Không đặt chốt lời ở sàn: bot tự thoát theo quy tắc của nó (giờ fix, thời gian giữ tối đa…) hoặc ở SL.">không có · thoát ở SL</span>';
            } else if(pips){
                body=`<span class="td-dim">${escapeHtml(pips)}p</span>`;
            } else {
                body='<span class="td-dim">—</span>';
            }
            return `<div class="sltp-line"><span class="sltp-tag">${tag}</span>${body}</div>`;
        }
        function sltpCellHtml(o, withPnl){
            const noTp=withPnl&&!!o.no_tp;
            return sltpLineHtml('SL', o.sl_price, withPnl?o.sl_pnl:null, o.sl_pips, noTp)
                 + sltpLineHtml('TP', o.tp_price, withPnl?o.tp_pnl:null, o.tp_pips, noTp);
        }
        // Mirrors the Recent Trades "Open / Close" cell: entry on one line, exit plus time in trade on the next.
        function tradeTimesHtml(t){
            const line=(tag, body)=>`<div class="sltp-line"><span class="sltp-tag">${tag}</span>${body}</div>`;
            return line('IN', `<span class="td-dim">${escapeHtml(t.entry_time||'—')}</span>`)
                 + line('OUT', `<span class="td-dim">${escapeHtml(t.exit_time||'—')}</span>`
                     + (t.duration ? `<span class="duration-chip" title="Thời gian giữ lệnh">${escapeHtml(t.duration)}</span>` : ''));
        }
        // Mirrors the close_reason_chip macro.
        function closeReasonHtml(reason){
            if(!reason) return '<span class="td-dim">—</span>';
            const r=String(reason).toLowerCase();
            let cls='';
            if(r.includes('stop out')||r.includes('stopout')) cls='reason-chip--loss';
            else if(r.includes('trailing')||r.includes('break-even')||r.includes('breakeven')) cls='reason-chip--lock';
            else if(r.includes('takeprofit')||r.includes('take profit')) cls='reason-chip--profit';
            else if(r.includes('stoploss')||r.includes('stop loss')) cls='reason-chip--loss';
            const safe=escapeHtml(reason);
            return `<span class="reason-chip ${cls}" title="${safe}">${safe}</span>`;
        }
        // Mirrors the bot_badge macro.
        function botBadge(b){
            if(!b)return '<span class="bot-badge bot-badge--default"><span class="bot-dot"></span>N/A</span>';
            const bl=String(b).toLowerCase();
            const isG=bl.includes('gotobi');
            const isE=bl.includes('-ecb-');
            const isL=bl.includes('-gold50');
            const badgeCls = isG ? 'bot-badge--gotobi' : (isE ? 'bot-badge--ecb' : (isL ? 'bot-badge--gold' : 'bot-badge--default'));
            const badgeText = isG ? 'Gotobi' : (isE ? 'ECB' : (isL ? 'Gold' : 'cBot'));
            const safe=escapeHtml(b);
            return `<div class="bot-cell">
                <span class="bot-badge ${badgeCls}"><span class="bot-dot"></span>${badgeText}</span>
                <span class="bot-id-text" title="${safe}">${safe}</span>
            </div>`;
        }
        // Mirrors the strategy_name macro.
        function strategyName(b){
            const bl=String(b||'').toLowerCase();
            return bl.includes('gotobi')?'Gotobi':(bl.includes('-ecb-')?'ECB':(bl.includes('-gold50')?'Gold':'cBot'));
        }
        // What the position loses if price reaches its stop. Mirrors the risk_line macro; takes a position or tick levels.
        function riskLineHtml(o){
            if(!o.sl_price) return '<span class="td-dim">Chưa có stop</span>';
            if(o.sl_pnl===null||o.sl_pnl===undefined) return `Stop ở <span class="td-mono">${escapeHtml(o.sl_price)}</span>`;
            const v=Number(o.sl_pnl)||0;
            return v<0 ? `Nếu chạm stop <b class="pnl-negative">${formatMoney(v)}</b>`
                       : `Stop đã khoá lời <b class="pnl-positive">+${formatMoney(v)}</b>`;
        }
        // One open position on the Overview: a two-line row that opens to the facts and the Close button.
        // Mirrors the pos-card block of templates/dashboard.html.
        function positionCardHtml(p){
            const curPrice = (p.current_price !== undefined && p.current_price !== null) ? p.current_price : p.entry_price;
            const priceAge = (typeof p.price_age_seconds === 'number') ? `<span class="td-dim" title="giá từ báo cáo gần nhất của bot"> ·${Math.floor(p.price_age_seconds/60)}m</span>` : '';
            const open = openPositionCards.has(String(p.id)) ? ' open' : '';
            return `<details class="pos-card" data-id="${escapeHtml(p.id)}" data-bot="${escapeHtml(p.bot_id||'')}" data-symbol="${escapeHtml(p.symbol||'')}" data-side="${escapeHtml(p.side||'')}"${open}>
                <summary class="pos-row">
                    <span class="pos-main">
                        <span class="pos-head">
                            <span class="pos-sym">${escapeHtml(p.symbol)}</span>
                            ${sideChip(p.side)}
                            <span class="pos-strategy">${strategyName(p.bot_id)}</span>
                        </span>
                        <span class="pos-risk">${riskLineHtml(p)}</span>
                    </span>
                    <span class="pos-pnl td-pnl-live">${pnlCellHtml(p.unrealized_pnl, p.unrealized_pnl_pips)}</span>
                    <span class="pos-chevron" aria-hidden="true"></span>
                </summary>
                <div class="pos-body">
                    <dl class="pos-facts">
                        <dt>Bot</dt><dd>${botBadge(p.bot_id)}</dd>
                        <dt>Tài khoản</dt><dd>${escapeHtml(p.account_label||'')}</dd>
                        <dt>Khối lượng</dt><dd>${escapeHtml(p.volume)} lot</dd>
                        <dt>Giá vào</dt><dd class="td-mono">${escapeHtml(p.entry_price)}</dd>
                        <dt>Giá hiện tại</dt><dd class="td-mono td-current-price">${escapeHtml(curPrice)}${priceAge}</dd>
                        <dt>SL / TP</dt><dd class="td-sltp">${sltpCellHtml(p, true)}</dd>
                        <dt>Mở lúc</dt><dd>${escapeHtml(p.entry_time||'—')}</dd>
                    </dl>
                    <div class="pos-actions">${closeButtonHtml(p)}</div>
                </div>
            </details>`;
        }
        // One closed trade on the Overview. Mirrors the closed-row block of templates/dashboard.html.
        function closedRowHtml(t){
            const day = String(t.exit_time||'').slice(9, 14) || '—';   // "HH:MM:SS DD/MM/YYYY" -> "DD/MM"
            const reason = t.close_reason_text || t.close_reason;   // close_reason_text: app/close_reasons.py
            const sub = [reason ? escapeHtml(reason) : '', t.duration ? `giữ ${escapeHtml(t.duration)}` : ''].filter(Boolean).join(' · ');
            const title = `${t.bot_id||''} · ${t.volume} lot · ${t.entry_price} → ${t.exit_price}`;
            return `<div class="closed-row" title="${escapeHtml(title)}">
                <span class="closed-day">${escapeHtml(day)}</span>
                <span class="closed-main">${strategyName(t.bot_id)} · ${sideChip(t.side)} <span class="td-mono">${escapeHtml(t.symbol)}</span>
                    <span class="closed-sub">${sub}</span></span>
                <span class="closed-pnl ${Number(t.pnl)>=0?'pnl-positive':'pnl-negative'}">${signedMoney(t.pnl)}</span>
            </div>`;
        }

        let currentMode = DASHBOARD_BOOTSTRAP.currentMode || 'demo';
        // Redesign D (2026-11-01): no page-wide Demo / Thật switch any more. The Overview's Real block reads the live
        // accounts (OV_ACCOUNT) and its Demo row is static/js/overview_demo.js; Bot shows both; Lịch, Xếp hạng chi tiết
        // and Nhật ký each carry their own small switch (bindModeSeg). The URL's /demo or /real no longer matters.
        const OV_ACCOUNT = 'live';
        let lbMode = 'live', logMode = 'all';
        /** A .mode-seg group: marks the pressed button and hands its data-mode to onChange. */
        function bindModeSeg(id, onChange) {
            const group = document.getElementById(id);
            if (!group) return;
            group.addEventListener('click', e => {
                const b = e.target.closest('button[data-mode]');
                if (!b || b.getAttribute('aria-pressed') === 'true') return;
                group.querySelectorAll('button[data-mode]').forEach(x => x.setAttribute('aria-pressed', x === b ? 'true' : 'false'));
                onChange(b.dataset.mode);
            });
        }

        const HISTORY_PAGE_SIZE = 5;   // the Overview shows the last few; matches dashboard_page()
        let historyPage = 1;
        function historyUrl() {
            return `/api/dashboard/history?account_id=${OV_ACCOUNT}&page=${historyPage}&page_size=${HISTORY_PAGE_SIZE}`;
        }

        async function fetchTradeHistory() {
            try {
                const [hR, cR] = await Promise.all([
                    fetch(historyUrl()),
                    fetch(`/api/dashboard/pnl-history?account_id=${OV_ACCOUNT}`)
                ]);
                updateTradeHistory(await hR.json());
                updatePnlChart(await cR.json());
            } catch(e) { console.error('Error fetching trade history:', e); }
        }

        async function refreshDashboardData() {
            try {
                const [sR, pR, hR, cR] = await Promise.all([
                    fetch(`/api/dashboard/summary?account_id=${OV_ACCOUNT}`),
                    fetch(`/api/dashboard/positions?account_id=${OV_ACCOUNT}`),
                    fetch(historyUrl()),
                    fetch(`/api/dashboard/pnl-history?account_id=${OV_ACCOUNT}`)
                ]);
                updateDashboard(await sR.json(), await pR.json());
                updateTradeHistory(await hR.json());
                updatePnlChart(await cR.json());
            } catch(err) { console.error('Fetch error:', err); }
        }

        bindModeSeg('lb-mode', mode => { lbMode = mode; fetchLeaderboard(); });
        bindModeSeg('log-mode', mode => { logMode = mode; fetchAgentLogs(logDateSelect.value); });

        let rawDailyHistory = DASHBOARD_BOOTSTRAP.pnlHistory;

        // Overview "Tiền 30 ngày qua": closed P&L added up day by day, drawn in the colour of where it ends.
        const cssVar = name => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
        function cumulativePnl(h){let c=0;return h.map(d=>{c+=(d.pnl||0);return parseFloat(c.toFixed(2));});}
        const equityChart = new Chart(document.getElementById('equity-chart').getContext('2d'), {
            type: 'line',
            data: { labels: [], datasets: [{ data: [], fill: true, tension: 0.3, borderWidth: 2, pointRadius: 0, pointHoverRadius: 4 }] },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: { display: false },
                    tooltip: { backgroundColor: cssVar('--bg-elevated'), titleColor: cssVar('--text-primary'), bodyColor: cssVar('--text-muted'),
                               displayColors: false, callbacks: { label: c => signedMoney(c.parsed.y) } }
                },
                scales: {
                    y: { grid: { color: cssVar('--border-subtle') }, border: { display: false },
                         ticks: { color: cssVar('--text-dim'), maxTicksLimit: 5, callback: v => '$' + v } },
                    x: { grid: { display: false }, ticks: { color: cssVar('--text-dim'), maxRotation: 0, autoSkip: true, maxTicksLimit: 4 } }
                }
            }
        });

        function updatePnlChart(h) {
            rawDailyHistory = h;
            const data = cumulativePnl(h);
            const last = data.length ? data[data.length - 1] : 0;
            const ds = equityChart.data.datasets[0];
            equityChart.data.labels = h.map(d => String(d.date || '').slice(8, 10) + '/' + String(d.date || '').slice(5, 7));
            ds.data = data;
            ds.borderColor = cssVar(last >= 0 ? '--profit' : '--loss');
            ds.backgroundColor = cssVar(last >= 0 ? '--profit-soft' : '--loss-soft');
            equityChart.update();
            const total = document.getElementById('curve-total');
            if (total) { total.textContent = signedMoney(last); total.className = `ov-card-count ${pnlClass(last)}`; }
        }
        updatePnlChart(rawDailyHistory);
        let ws=null,pingInterval=null;
        function setConn(on){const el=document.getElementById('connection-status');if(on){el.className='status-pill status-pill--online';el.innerHTML='<span class="status-dot"></span><span>Đã kết nối</span>'}else{el.className='status-pill status-pill--offline';el.innerHTML='<span class="status-dot"></span><span>Mất kết nối</span>'}}
        function connectWebSocket(){
            const p=window.location.protocol==='https:'?'wss:':'ws:';
            ws=new WebSocket(`${p}//${window.location.host}/ws/dashboard`);
            ws.onopen=()=>{
                setConn(true);
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({type:'subscribe',account_id:OV_ACCOUNT,mode:'real'}));
                }
                refreshDashboardData();
                if (typeof fetchLeaderboard === 'function') fetchLeaderboard();
                if (pingInterval) clearInterval(pingInterval);
                pingInterval=setInterval(()=>{
                    if(ws.readyState===WebSocket.OPEN)
                        ws.send(JSON.stringify({type:'ping',account_id:OV_ACCOUNT,mode:'real'}))
                },15000);
            };
            ws.onmessage=(e)=>{
                try {
                    const d=JSON.parse(e.data);
                    if(d.type==='update') {
                        // Updates for the live scope ('live', or 'real' from older senders) redraw the Real block.
                        const matchesAccount = (!d.account_id) || d.account_id === OV_ACCOUNT || d.account_id === 'real';
                        if (matchesAccount) {
                            if (d.summary && d.positions) {
                                updateDashboard(d.summary, d.positions);
                            }
                            fetchTradeHistory();
                            if (d.pnl_history) {
                                updatePnlChart(d.pnl_history);
                            }
                            if (typeof fetchLeaderboard === 'function') {
                                fetchLeaderboard();
                            }
                        }
                    } else if(d.type==='log') {
                        handleLiveLogLine(d.line);
                    } else if(d.type==='tick') {
                        handleLiveTick(d);
                    } else if(d.type==='event') {
                        handleLiveEvent(d);
                    }
                } catch(err) {
                    console.error('Error handling WS message:', err);
                }
            };
            ws.onclose=()=>{setConn(false);if(pingInterval)clearInterval(pingInterval);setTimeout(connectWebSocket,3000)};
            ws.onerror=(e)=>console.error('WS error:',e);
        }
        // Start WebSocket connection on page load
        connectWebSocket();

        function handleLiveTick(tick) {
            if (!tick || !tick.symbol) return;
            // Update the matching position cards
            const cards = document.querySelectorAll('#positions-table .pos-card');
            cards.forEach(tr => {
                if ((tr.dataset.symbol || '').toUpperCase() === tick.symbol.toUpperCase()) {
                    const curPriceCell = tr.querySelector('.td-current-price');
                    if (curPriceCell) {
                        const isBuy = tr.dataset.side === 'BUY';
                        const newPrice = isBuy ? (tick.bid || tick.ask) : (tick.ask || tick.bid);
                        if (newPrice) {
                            const oldPrice = parseFloat(curPriceCell.textContent) || newPrice;
                            // Replaces the whole cell, which also drops the "·Xm" snapshot-age
                            // suffix: a price that just arrived live has no age.
                            curPriceCell.textContent = newPrice;
                            curPriceCell.classList.remove('price-flash-up', 'price-flash-down');
                            void curPriceCell.offsetWidth; // trigger reflow
                            curPriceCell.classList.add(newPrice >= oldPrice ? 'price-flash-up' : 'price-flash-down');
                        }
                    }
                    // P&L and SL/TP belong to one bot's position; two bots can trade the same
                    // symbol (the same cell on two accounts), so match the bot as well.
                    const rowBot = tr.dataset.bot;
                    if (tick.bot_id && rowBot && rowBot !== tick.bot_id) return;
                    // The bot sends its own broker P&L sample with the tick when a position is
                    // open, so the chip stays live without the server rebuilding positions.
                    if (tick.pnl !== undefined && tick.pnl !== null) {
                        const pnlCell = tr.querySelector('.td-pnl-live');
                        if (pnlCell) pnlCell.innerHTML = pnlCellHtml(tick.pnl, tick.pips);
                    }
                    // Trailing / break-even stop moves show up here between bar snapshots.
                    if (tick.levels) {
                        const sltpCell = tr.querySelector('.td-sltp');
                        if (sltpCell) sltpCell.innerHTML = sltpCellHtml(tick.levels, true);
                        const riskEl = tr.querySelector('.pos-risk');
                        if (riskEl) riskEl.innerHTML = riskLineHtml(tick.levels);
                    }
                }
            });
        }

        function handleLiveEvent(evt) {
            // Auto refresh trade history and dashboard when positions open/close or guardrail triggers
            const msg = (evt.message || '').toUpperCase();
            const typ = (evt.event_type || '').toUpperCase();
            if (typ === 'GUARDRAIL' || typ === 'TRADE_CLOSE' || typ === 'TRADE_OPEN' || msg.includes('CLOSE') || msg.includes('OPEN')) {
                fetchTradeHistory();
                if (typeof fetchLeaderboard === 'function') fetchLeaderboard();
            }
        }

        function handleLiveLogLine(line) {
            if (!line) return;
            // Only append if viewing current date
            const todayStr = new Date().toISOString().split('T')[0];
            if (logDateSelect.value && logDateSelect.value !== todayStr && logDateSelect.value !== currentLogDate) {
                return;
            }
            rawLogLines.push(line);
            if (rawLogLines.length > 300) rawLogLines.shift();
            
            const filterText = (logFilterInput.value || '').toLowerCase();
            if (!filterText || line.toLowerCase().includes(filterText)) {
                // Remove empty state message if present
                const emptyState = logBox.querySelector('.td-dim');
                if (emptyState && logBox.children.length === 1) {
                    logBox.innerHTML = '';
                }
                const lineNode = document.createElement('div');
                lineNode.innerHTML = colorizeLogLine(line);
                logBox.appendChild(lineNode.firstElementChild || lineNode);
                if (logAutoscroll.checked) {
                    logBox.scrollTop = logBox.scrollHeight;
                }
            }
        }
        // "2 lệnh · nếu tất cả chạm stop -$3,975.50": the worst case of what is open, from each stop's P&L.
        function holdCountHtml(positions){
            const worst = positions.reduce((s, p) => s + (Number(p.sl_pnl) < 0 ? Number(p.sl_pnl) : 0), 0);
            return `${positions.length} lệnh` + (worst < 0
                ? ` · nếu tất cả chạm stop <b class="pnl-negative">${signedMoney(Math.round(worst * 100) / 100)}</b>` : '');
        }
        function updateDashboard(summary,positions){
            const money=(id, v, signed)=>{
                const el=document.getElementById(id); if(!el) return;
                el.textContent=signed?signedMoney(v):formatMoney(v);
                if(signed) el.className=`${el.className.split(' ').filter(c=>!c.startsWith('kpi-value--')).join(' ')} ${pnlClass(v)}`.trim();
            };
            money('daily-pnl', summary.daily_pnl, true);
            money('month-pnl', summary.month_pnl, true);
            money('account-balance', summary.account_balance||0, false);
            money('account-equity', summary.account_equity||0, false);
            const fEl=document.getElementById('floating-pnl');
            if(fEl){
                const hasFloating=summary.floating_pnl!==undefined && summary.floating_pnl!==null;
                fEl.textContent=hasFloating?`(${signedMoney(summary.floating_pnl)})`:'--';
                fEl.className=hasFloating?pnlClass(summary.floating_pnl):'';
            }
            document.getElementById('last-updated').textContent=new Date().toLocaleTimeString('vi-VN');

            const posCountEl = document.getElementById('active-pos-count');
            if (posCountEl) posCountEl.innerHTML = holdCountHtml(positions);
            const box=document.getElementById('positions-table');
            box.innerHTML = positions.length ? positions.map(positionCardHtml).join('') : '<p class="ov-empty">Không giữ lệnh nào.</p>';
        }
        // --- Manual close (Close button in Active Positions) ---
        // The dashboard queues the close; the position's bot picks it up within ~2 s, closes it at
        // market and reports back. The existing broadcast then removes the row.
        const closingPositions = new Set();   // row ids with a close in flight (survives re-renders)
        // Rows the user opened stay open when updateDashboard() redraws the list.
        const openPositionCards = new Set();
        // 'toggle' does not bubble, hence the capture listener on the list.
        document.getElementById('positions-table').addEventListener('toggle', e => {
            const card = e.target.closest && e.target.closest('.pos-card');
            if (!card || !card.dataset.id) return;
            if (card.open) openPositionCards.add(card.dataset.id); else openPositionCards.delete(card.dataset.id);
        }, true);
        const COMMAND_FAILURE_TEXT = {
            expired: 'Bot không nhận lệnh trong 15 giây - có thể bị treo hoặc đang chạy bản cũ. Hãy đóng lệnh trong cTrader.',
            unconfirmed: 'Bot đã nhận lệnh nhưng không báo lại kết quả. Hãy kiểm tra lệnh trong cTrader.',
        };
        function commandFailureText(cmd) {
            return COMMAND_FAILURE_TEXT[cmd.status] || `Đóng lệnh thất bại: ${cmd.message || cmd.status}`;
        }
        function closeButtonHtml(p) {
            const closing = closingPositions.has(String(p.id));
            const noId = !p.ctrader_id;
            const title = noId ? ' title="Lệnh này chưa có mã cTrader - hãy đóng trong cTrader"' : '';
            return `<button class="log-btn action-close-pos" data-id="${p.id}" data-bot="${escapeHtml(p.bot_id||'')}" data-symbol="${escapeHtml(p.symbol||'')}" data-side="${escapeHtml(p.side||'')}" data-volume="${escapeHtml(p.volume)}" data-live="${p.account_type==='live'?'1':'0'}"${(noId||closing)?' disabled':''}${title}>${closing?'Đang đóng…':'Đóng lệnh'}</button>`;
        }
        async function waitForBotCommand(id, maxSeconds = 35) {
            for (let i = 0; i < maxSeconds; i++) {
                await new Promise(r => setTimeout(r, 1000));
                const res = await fetch(`/api/bot-commands/${id}`);
                if (!res.ok) continue;
                const cmd = await res.json();
                if (['done', 'failed', 'expired', 'unconfirmed'].includes(cmd.status)) return cmd;
            }
            return { status: 'unconfirmed', message: '' };
        }
        async function closePosition(btn) {
            const d = btn.dataset;
            const card = btn.closest('.pos-card');
            const pnlCell = card ? card.querySelector('.td-pnl-live') : null;
            const pnlText = pnlCell ? pnlCell.textContent.trim() : '';
            const ok = await askConfirm({
                title: `Đóng lệnh ${d.side === 'BUY' ? 'mua' : 'bán'} ${d.symbol} ${d.volume} lot?`,
                body: `Bot ${d.bot} đóng lệnh theo giá thị trường. Lời/lỗ hiện tại: ${pnlText || 'chưa có'}.`,
                ok: 'Đóng lệnh', live: d.live === '1', typeWord: confirmWordFor(d.bot, d.symbol),
            });
            if (!ok) return;
            closingPositions.add(String(d.id));
            btn.disabled = true;
            btn.textContent = 'Đang đóng…';
            try {
                const res = await fetch(`/api/positions/${d.id}/close`, { method: 'POST' });
                const data = await res.json();
                if (!data.success) throw new Error(data.message || 'Server từ chối đóng lệnh');
                const cmd = await waitForBotCommand(data.command_id);
                if (cmd.status !== 'done') throw new Error(commandFailureText(cmd));
                refreshDashboardData();   // the broadcast normally removes the row first
            } catch (err) {
                closingPositions.delete(String(d.id));
                // updateDashboard() may have re-rendered the cards while this waited, so `btn` can be
                // a detached copy: re-enable whichever button shows this row now.
                document.querySelectorAll(`.action-close-pos[data-id="${d.id}"]`)
                    .forEach(b => {
                        b.disabled = false; b.textContent = 'Đóng lệnh';
                        // The reason sits next to the button it is about (the viewer never shows alert()).
                        const actions = b.closest('.pos-actions');
                        if (!actions) return;
                        let note = actions.querySelector('.pos-close-error');
                        if (!note) { note = document.createElement('p'); note.className = 'pos-close-error'; note.setAttribute('role', 'alert'); actions.appendChild(note); }
                        note.textContent = String((err && err.message) || err);
                    });
            } finally {
                closingPositions.delete(String(d.id));
            }
        }
        document.getElementById('positions-table').addEventListener('click', e => {
            const btn = e.target.closest('.action-close-pos');
            if (btn && !btn.disabled) closePosition(btn);
        });

        function updateTradeHistory(page){
            const history = page.items || [];
            const totalPages = page.total_pages || 1;
            if ((page.page || 1) > totalPages) { historyPage = totalPages; fetchTradeHistory(); return; }
            historyPage = page.page || 1;
            const label=document.getElementById('history-page-label');
            if(label) label.textContent=`Trang ${historyPage} / ${totalPages}`;
            const prev=document.getElementById('history-prev'), next=document.getElementById('history-next');
            if(prev) prev.disabled = historyPage <= 1;
            if(next) next.disabled = historyPage >= totalPages;
            const box=document.getElementById('history-table');if(!box)return;
            box.innerHTML = history.length ? history.map(closedRowHtml).join('') : '<p class="ov-empty">Chưa có lệnh nào đóng.</p>';
        }
        document.getElementById('history-prev')?.addEventListener('click', () => {
            if (historyPage > 1) { historyPage -= 1; fetchTradeHistory(); }
        });
        document.getElementById('history-next')?.addEventListener('click', () => {
            historyPage += 1; fetchTradeHistory();
        });

        // Auto-refresh when tab returns to focus
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                refreshDashboardData();
                if (typeof fetchLeaderboard === 'function') fetchLeaderboard();
            }
        });

        // Periodic background fallback for trade history & dashboard (every 30s)
        setInterval(() => {
            if (!document.hidden) {
                const wsOpen = ws && ws.readyState === WebSocket.OPEN;
                if (!wsOpen) {
                    refreshDashboardData();
                } else {
                    fetchTradeHistory();
                }
                if (typeof fetchLeaderboard === 'function') fetchLeaderboard();
            }
        }, 30000);
        const logBox = document.getElementById('agent-log-box');
        const logDateSelect = document.getElementById('log-date-select');
        const logFilterInput = document.getElementById('log-filter-input');
        const logAutoscroll = document.getElementById('log-autoscroll');
        const logRefreshBtn = document.getElementById('log-refresh-btn');
        const logClearBtn = document.getElementById('log-clear-btn');
        let rawLogLines = [];
        let currentLogDate = '';

        function colorizeLogLine(line) {
            let formatted = line
                .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
            
            // Highlight timestamps (YYYY-MM-DD HH:mm:ss or HH:mm:ss)
            formatted = formatted.replace(/^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}|\d{2}:\d{2}:\d{2})/, '<span class="log-time">$1</span>');
            // Highlight tags
            if (formatted.includes('[PORTFOLIO EVENT]') || formatted.includes('[PORTFOLIO]')) {
                formatted = formatted.replace(/\[PORTFOLIO EVENT\]|\[PORTFOLIO\]/, '<span class="log-tag-event">$&</span>');
            } else if (formatted.includes('[WARNING]') || formatted.includes('[WARN]')) {
                formatted = formatted.replace(/\[WARNING\]|\[WARN\s*\]/, '<span class="log-tag-warn">$&</span>');
            } else if (/\[(?:ERROR\s*|CRITICAL)\]/.test(formatted) || formatted.includes('Error:')) {
                // the log format pads the level to 7 characters: "[ERROR  ]"
                formatted = formatted.replace(/\[(?:ERROR\s*|CRITICAL)\]|Error:/, '<span class="log-tag-error">$&</span>');
            }

            // Highlight key actions
            formatted = formatted.replace(/\bAction: (BUY|SELL|CLOSE_ALL|HOLD)\b/g, (m, a) => {
                const cls = a === 'BUY' ? 'side-chip--buy' : (a === 'SELL' ? 'side-chip--sell' : 'td-dim');
                return `Action: <span class="side-chip ${cls}">${a}</span>`;
            });

            return `<div class="log-line">${formatted}</div>`;
        }

        function renderLogs() {
            const filterText = (logFilterInput.value || '').toLowerCase();
            const filtered = filterText 
                ? rawLogLines.filter(l => l.toLowerCase().includes(filterText))
                : rawLogLines;

            if (!filtered.length) {
                const msg = logMode === 'live'
                    ? 'Không có nhật ký tiền thật cho ngày này (bot có thể đang ngoài giờ giao dịch; thử Tất cả hoặc Demo).'
                    : logMode === 'demo' ? 'Không có nhật ký demo cho ngày này (thử Tất cả, Thật hoặc chọn ngày khác).'
                    : 'Không có nhật ký cho ngày này (chọn ngày khác).';
                logBox.innerHTML = `<div class="log-line td-dim">${msg}</div>`;
                return;
            }

            logBox.innerHTML = filtered.map(colorizeLogLine).join('');
            if (logAutoscroll.checked) {
                logBox.scrollTop = logBox.scrollHeight;
            }
        }

        async function fetchAgentLogs(dateParam = '') {
            try {
                const base = `/api/dashboard/logs?lines=150&mode=${logMode}&account_id=${logMode}`;
                const url = dateParam ? `${base}&date_str=${dateParam}` : base;
                const res = await fetch(url);
                const data = await res.json();
                rawLogLines = data.lines || [];
                currentLogDate = data.date || '';

                // Populate date selector if empty
                if (data.available_dates && logDateSelect.children.length !== data.available_dates.length) {
                    logDateSelect.innerHTML = data.available_dates.map(d => 
                        `<option value="${d}" ${d === currentLogDate ? 'selected' : ''}>${d}</option>`
                    ).join('');
                }

                renderLogs();
            } catch (err) {
                console.error('Failed to fetch logs:', err);
            }
        }

        logFilterInput.addEventListener('input', renderLogs);
        logRefreshBtn.addEventListener('click', () => fetchAgentLogs(logDateSelect.value));
        logClearBtn.addEventListener('click', () => { logBox.innerHTML = ''; rawLogLines = []; });
        logDateSelect.addEventListener('change', (e) => fetchAgentLogs(e.target.value));

        // Initial fetch for historical logs on load
        fetchAgentLogs();
        // Fallback polling only when WebSocket is disconnected (every 10s)
        setInterval(() => {
            if ((!ws || ws.readyState !== WebSocket.OPEN) && !document.hidden && logDateSelect.value === currentLogDate) {
                fetchAgentLogs(currentLogDate);
            }
        }, 10000);
        // --- Leaderboard Integration ---
        // Two rankings (USD P&L / lot-neutral) arrive in one response; the tab only picks which
        // table shows. The period, picked in a popover, is a rolling window, a calendar preset or a
        // custom range; presets and custom ranges both go out as Vietnam-time days (period=custom).
        const LB_TABS = ['usd', 'lot'];
        const LB_ROLLING = {'1d': '24 giờ qua', '1w': '7 ngày qua', '1m': '30 ngày qua',
                            '6m': '6 tháng qua', '1y': '12 tháng qua', 'all': 'Toàn bộ'};
        const LB_CALENDAR = {today: 'Hôm nay', yesterday: 'Hôm qua', thisweek: 'Tuần này',
                             lastweek: 'Tuần trước', thismonth: 'Tháng này', lastmonth: 'Tháng trước'};
        const LB_DAY_RE = /^\d{4}-\d{2}-\d{2}$/;
        const LB_WEIGHT_HINTS = {
            usd: 'Điểm: 30% tỷ lệ thắng + 30% hệ số lời + 20% lời/lỗ ròng + 20% độ đều',
            lot: 'Điểm: 30% tỷ lệ thắng + 30% hệ số lời + 20% lời/sụt giảm + 20% độ đều · mỗi lệnh tính trên rủi ro lúc vào',
        };
        let lbTab = 'usd';
        let lbPeriod = '1w';  // default: a deleted bot's old trades drop out after a week
        let lbDateFrom = '';  // custom range, 'YYYY-MM-DD' in Vietnam time; '' = open side
        let lbDateTo = '';
        try {
            const savedTab = localStorage.getItem('lb-tab');
            const savedPeriod = localStorage.getItem('lb-period');
            const savedFrom = localStorage.getItem('lb-date-from') || '';
            const savedTo = localStorage.getItem('lb-date-to') || '';
            if (LB_TABS.includes(savedTab)) lbTab = savedTab;
            if (LB_DAY_RE.test(savedFrom)) lbDateFrom = savedFrom;
            if (LB_DAY_RE.test(savedTo)) lbDateTo = savedTo;
            if (lbHas(LB_ROLLING, savedPeriod) || lbHas(LB_CALENDAR, savedPeriod)) lbPeriod = savedPeriod;
            // A stored custom range must still be one the server takes
            else if (savedPeriod === 'custom' && lbRangeOk(lbDateFrom, lbDateTo)) lbPeriod = 'custom';
        } catch (e) { /* storage unavailable: keep the defaults */ }

        function lbHas(obj, key) {
            return Object.prototype.hasOwnProperty.call(obj, key);
        }

        // Today in Vietnam time (GMT+7, no DST) as a UTC-midnight Date, whatever the browser's zone
        function lbVnToday() {
            const now = new Date(Date.now() + 7 * 3600e3);
            return new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()));
        }

        function lbAddDays(day, n) {
            return new Date(day.getTime() + n * 86400e3);
        }

        function lbIsoDay(day) {
            return day.toISOString().slice(0, 10);
        }

        // First and last day ('YYYY-MM-DD', both included) of a calendar preset or of the custom
        // range; null for a rolling window. Presets are worked out afresh, so "Today" moves on at
        // midnight Vietnam time.
        function lbRangeFor(period) {
            if (period === 'custom') return {from: lbDateFrom, to: lbDateTo};
            if (!lbHas(LB_CALENDAR, period)) return null;
            const today = lbVnToday();
            const monday = lbAddDays(today, -((today.getUTCDay() + 6) % 7));  // weeks start on Monday
            const y = today.getUTCFullYear(), m = today.getUTCMonth();
            const [from, to] = {
                today: [today, today],
                yesterday: [lbAddDays(today, -1), lbAddDays(today, -1)],
                thisweek: [monday, today],
                lastweek: [lbAddDays(monday, -7), lbAddDays(monday, -1)],
                thismonth: [new Date(Date.UTC(y, m, 1)), today],
                lastmonth: [new Date(Date.UTC(y, m - 1, 1)), new Date(Date.UTC(y, m, 0))],
            }[period];
            return {from: lbIsoDay(from), to: lbIsoDay(to)};
        }

        // A custom range the server takes: at least one day, and never reversed
        function lbRangeOk(from, to) {
            return !!(from || to) && !(from && to && from > to);
        }

        // 'YYYY-MM-DD' as 'DD/MM', or 'DD/MM/YYYY'
        function lbShortDay(day, withYear) {
            const [y, m, d] = day.split('-');
            return withYear ? `${d}/${m}/${y}` : `${d}/${m}`;
        }

        // A range for display; years only show when it leaves the current one
        function lbRangeText(range) {
            const year = String(lbVnToday().getUTCFullYear());
            const withYear = [range.from, range.to].some(day => day && day.slice(0, 4) !== year);
            const from = range.from && lbShortDay(range.from, withYear);
            const to = range.to && lbShortDay(range.to, withYear);
            if (!from) return `đến ${to}`;
            if (!to) return `từ ${from}`;
            return from === to ? from : `${from} – ${to}`;
        }

        // What the period button reads: the preset's name, and the days it covers when it has any
        function lbPeriodLabel() {
            if (lbHas(LB_ROLLING, lbPeriod)) return {label: LB_ROLLING[lbPeriod], dates: ''};
            return {label: LB_CALENDAR[lbPeriod] || 'Tự chọn', dates: lbRangeText(lbRangeFor(lbPeriod))};
        }
        let lbData = null;       // the response on screen
        let lbShownQuery = null; // the selection it was fetched for
        // One request at a time: a burst of WS updates (one per account scope) collapses into a
        // single follow-up request instead of one full recompute each.
        let lbInFlight = false;
        let lbQueued = false;

        function lbViewActive() {
            const view = document.getElementById('view-leaderboard');
            return !!(view && view.classList.contains('active'));
        }

        // The current selection (account, mode, period) as the query string that fetches it
        /** The API ranks every bot it knows (zeros for the other mode's); keep this mode's, numbered again. */
        function lbOwnMode(data, mode) {
            if (!data) return data;
            const live = id => /(^|[-_])live([-_]|$)/i.test(String(id || ''));
            const keep = list => (list || []).filter(b => live(b.bot_id) === (mode === 'live')).map((b, i) => ({...b, rank: i + 1}));
            const rankings = keep(data.rankings);
            const lot = data.lot_neutral ? {...data.lot_neutral, rankings: keep(data.lot_neutral.rankings)} : data.lot_neutral;
            if (lot) lot.top_performer = lot.rankings[0] || null;
            return {...data, rankings, lot_neutral: lot, top_performer: rankings[0] || null, total_bots: rankings.length};
        }
        function lbQuery() {
            // Rank strictly inside one mode, the one this screen's Thật / Demo switch shows.
            const query = `account_id=${lbMode}&account_type=${lbMode}`;
            const range = lbRangeFor(lbPeriod);
            if (!range) return `${query}&period=${lbPeriod}`;
            return `${query}&period=custom&date_from=${encodeURIComponent(range.from)}&date_to=${encodeURIComponent(range.to)}`;
        }

        async function fetchLeaderboard() {
            // Nothing to refresh while the view is hidden: opening it fetches
            if (!lbViewActive()) return;
            if (lbInFlight) { lbQueued = true; return; }
            lbInFlight = true;
            const query = lbQuery();
            try {
                const res = await fetch(`/api/leaderboard?${query}`);
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                const data = await res.json();
                // The selection changed meanwhile: the queued request fetches the new one
                if (query === lbQuery()) {
                    lbShownQuery = query;
                    renderLeaderboard(lbOwnMode(data, lbMode));
                }
            } catch (e) {
                console.error("Error fetching leaderboard", e);
                if (query === lbQuery()) lbShowFetchError(query);
            } finally {
                lbInFlight = false;
                if (lbQueued) {
                    lbQueued = false;
                    fetchLeaderboard();
                }
            }
        }

        // Rows already on screen for this same selection stay (a failed poll is not news), but rows
        // for the previous period or account must not sit under the new one.
        function lbShowFetchError(query) {
            if (lbShownQuery === query) return;
            lbData = null;
            lbShownQuery = null;
            const note = document.getElementById('lb-range-note');
            if (note) note.hidden = true;
            const row = colspan => `<tr><td colspan="${colspan}" class="empty-state">Chưa tải được bảng xếp hạng, đang thử lại…</td></tr>`;
            const tbody = document.getElementById('leaderboard-table-body');
            const lotBody = document.getElementById('leaderboard-lot-table-body');
            if (tbody) tbody.innerHTML = row(11);
            if (lotBody) lotBody.innerHTML = row(10);
            ['lb-top-performer', 'lb-fleet-winrate', 'lb-fleet-pnl', 'lb-total-bots'].forEach(id => {
                const el = document.getElementById(id);
                if (el) el.textContent = '--';
            });
        }

        function applyLbControls() {
            document.querySelectorAll('#lb-tab-group [data-lb-tab]').forEach(btn => {
                const on = btn.dataset.lbTab === lbTab;
                btn.classList.toggle('active', on);
                btn.setAttribute('aria-pressed', on ? 'true' : 'false');
            });
            document.querySelectorAll('.lb-period-opt[data-lb-period]').forEach(btn => {
                const on = btn.dataset.lbPeriod === lbPeriod;
                btn.classList.toggle('active', on);
                btn.setAttribute('aria-pressed', on ? 'true' : 'false');
            });
            const custom = document.getElementById('lb-period-custom');
            if (custom) custom.classList.toggle('active', lbPeriod === 'custom');
            const {label, dates} = lbPeriodLabel();
            const labelEl = document.getElementById('lb-period-label');
            if (labelEl) labelEl.textContent = label;
            const datesEl = document.getElementById('lb-period-dates');
            if (datesEl) {
                datesEl.textContent = dates;
                datesEl.hidden = !dates;
            }
            const usdPane = document.getElementById('lb-pane-usd');
            const lotPane = document.getElementById('lb-pane-lot');
            if (usdPane) usdPane.hidden = lbTab !== 'usd';
            if (lotPane) lotPane.hidden = lbTab !== 'lot';
            const hint = document.getElementById('lb-weight-hint');
            if (hint) hint.textContent = LB_WEIGHT_HINTS[lbTab];
        }

        function lbRankCell(bot) {
            if (bot.total_trades === 0) return `<span class="td-dim">${bot.rank}</span>`;
            // Top three by colour and weight, not medal emoji (redesign D).
            if (bot.rank === 1) return '<span class="rank-badge-1">1</span>';
            if (bot.rank === 2) return '<span class="rank-badge-2">2</span>';
            if (bot.rank === 3) return '<span class="rank-badge-3">3</span>';
            return `<span class="td-dim">${bot.rank}</span>`;
        }

        // bot_id comes from the bot's own reports: escape it and everything derived from it
        function lbBotCells(bot) {
            return `<td class="rank-cell">${lbRankCell(bot)}</td>
                    <td>
                        <div class="bot-cell">
                            <span class="font-bold" style="color: var(--text-primary);">${escapeHtml(bot.bot_name)}</span>
                            <span class="bot-id-text">${escapeHtml(bot.bot_id)}</span>
                        </div>
                    </td>
                    <td><span class="symbols-chip">${escapeHtml(bot.symbol_display)}</span></td>
                    <td><span class="tier-badge tier-badge--${bot.tier_badge}">${bot.tier_label}</span></td>`;
        }

        function lbWinRateCell(bot) {
            if (bot.total_trades === 0) return '<span class="td-dim">--</span>';
            if (bot.total_wins === 0) {
                return `<span class="font-mono font-bold pnl-negative">0.0%</span><div class="td-dim" style="font-size:0.69rem;">0 thắng / ${bot.total_losses} thua</div>`;
            }
            const color = bot.win_rate >= 60 ? 'var(--profit)' : (bot.win_rate >= 40 ? '#fbbf24' : 'var(--loss)');
            return `<span class="font-mono font-bold" style="color: ${color};">${bot.win_rate.toFixed(1)}%</span><div class="td-dim" style="font-size:0.69rem;">${bot.total_wins} thắng / ${bot.total_losses} thua</div>`;
        }

        function lbProfitFactorCell(bot) {
            if (bot.total_trades === 0) return '<span class="td-dim">--</span>';
            if (bot.profit_factor === null) return '<span class="font-mono pnl-positive" title="Chưa có lệnh thua">∞</span>';
            if (bot.profit_factor === 0) return '<span class="font-mono pnl-negative" title="Chưa có lệnh thắng">0.00</span>';
            return `<span class="font-mono">${bot.profit_factor.toFixed(2)}</span>`;
        }

        function lbTradesCell(bot) {
            const full = (lbData && lbData.full_sample_trades) || 10;
            const small = bot.total_trades > 0 && bot.total_trades < full;
            return `<td class="font-mono">${bot.total_trades}${small
                ? `<div class="td-dim" style="font-size:0.69rem;" title="Ít hơn ${full} lệnh đã đóng: điểm bị kéo về 50 cho tới khi đủ mẫu">ít mẫu</div>`
                : ''}</td>`;
        }

        function lbScoreCell(bot) {
            if (bot.total_trades === 0) return '<td><span class="td-dim">--</span></td>';
            return `<td>
                        <div class="score-pill">
                            <span style="color: ${bot.tier_color};">${bot.composite_score}</span>
                            <span class="score-bar-bg">
                                <span class="score-bar-fill" style="width: ${Math.min(100, Math.max(0, bot.composite_score))}%; background: ${bot.tier_color};"></span>
                            </span>
                        </div>
                    </td>`;
        }

        function lbReturnDdCell(bot) {
            if (bot.total_trades === 0) return '<span class="td-dim">--</span>';
            const unit = bot.basis === 'risk' ? 'lời/lỗ mỗi lot mỗi pip stop' : 'lời/lỗ mỗi lot';
            const title = `Ròng ${bot.net_units.toFixed(2)} · sụt giảm tối đa ${bot.max_dd_units.toFixed(2)} (${unit})`;
            let cell;
            if (bot.return_dd === null) {
                cell = bot.net_units > 0
                    ? `<span class="font-mono pnl-positive" title="Chưa có sụt giảm · ${title}">∞</span>`
                    : `<span class="font-mono td-dim" title="${title}">0.00</span>`;
            } else {
                const cls = bot.return_dd > 0 ? 'pnl-positive' : (bot.return_dd < 0 ? 'pnl-negative' : 'td-dim');
                cell = `<span class="font-mono ${cls}" title="${title}">${bot.return_dd.toFixed(2)}</span>`;
            }
            if (bot.basis === 'lot') {
                cell += '<div class="td-dim" style="font-size:0.69rem;" title="Một số lệnh không lưu khoảng stop, nên mọi lệnh được tính theo lot">theo lot</div>';
            }
            return cell;
        }

        function lbEmptyRow(colspan) {
            const msg = lbPeriod === 'all' ? 'Chưa có lịch sử giao dịch của bot' : 'Không có bot nào giao dịch trong khoảng này';
            return `<tr><td colspan="${colspan}" class="empty-state">${msg}</td></tr>`;
        }

        function renderLeaderboard(data) {
            if (!data) return;
            lbData = data;
            applyLbControls();
            const rangeNote = document.getElementById('lb-range-note');
            if (rangeNote) rangeNote.hidden = data.includes_open_positions !== false;
            const lot = data.lot_neutral || { top_performer: null, rankings: [] };
            const top = lbTab === 'lot' ? lot.top_performer : data.top_performer;
            const topPerfEl = document.getElementById('lb-top-performer');
            if (topPerfEl) {
                topPerfEl.textContent = top ? `${top.bot_name} (${top.composite_score}/100)` : '—';
            }
            const fleetWinrateEl = document.getElementById('lb-fleet-winrate');
            if (fleetWinrateEl) {
                fleetWinrateEl.textContent = `${(data.fleet_win_rate || 0).toFixed(1)}%`;
            }
            const fleetPnlEl = document.getElementById('lb-fleet-pnl');
            if (fleetPnlEl) {
                const pnl = data.fleet_total_pnl_usd || 0;
                fleetPnlEl.textContent = `$${pnl.toFixed(2)}`;
                fleetPnlEl.className = `kpi-value font-bold kpi-value--mono ${pnl >= 0 ? 'kpi-value--profit' : 'kpi-value--loss'}`;
            }
            const totalBotsEl = document.getElementById('lb-total-bots');
            if (totalBotsEl) {
                totalBotsEl.textContent = data.total_bots || 0;
            }

            const tbody = document.getElementById('leaderboard-table-body');
            if (tbody) {
                if (!data.rankings || data.rankings.length === 0) {
                    tbody.innerHTML = lbEmptyRow(11);
                } else {
                    tbody.innerHTML = data.rankings.map(bot => {
                        const closedPnlClass = bot.closed_pnl_usd >= 0 ? 'pnl-positive' : 'pnl-negative';
                        const floatingPnlClass = bot.floating_pnl_usd > 0 ? 'pnl-positive' : (bot.floating_pnl_usd < 0 ? 'pnl-negative' : 'td-dim');
                        return `<tr>
                            ${lbBotCells(bot)}
                            <td>${lbWinRateCell(bot)}</td>
                            <td>${lbProfitFactorCell(bot)}</td>
                            ${lbTradesCell(bot)}
                            <td>
                                <span class="pnl-chip ${bot.total_pnl_usd > 0 ? 'pnl-chip--profit' : (bot.total_pnl_usd < 0 ? 'pnl-chip--loss' : 'td-dim')}">
                                    ${bot.total_pnl_usd > 0 ? '+' : ''}$${bot.total_pnl_usd.toFixed(2)}
                                </span>
                            </td>
                            <td class="font-mono ${closedPnlClass}">$${bot.closed_pnl_usd.toFixed(2)}</td>
                            <td class="font-mono ${floatingPnlClass}">$${bot.floating_pnl_usd.toFixed(2)}</td>
                            ${lbScoreCell(bot)}
                        </tr>`;
                    }).join('');
                }
            }

            const lotBody = document.getElementById('leaderboard-lot-table-body');
            if (lotBody) {
                if (!lot.rankings || lot.rankings.length === 0) {
                    lotBody.innerHTML = lbEmptyRow(10);
                } else {
                    lotBody.innerHTML = lot.rankings.map(bot => {
                        const payoff = bot.total_trades === 0 ? '<span class="td-dim">--</span>'
                            : bot.payoff_ratio === null ? '<span class="font-mono pnl-positive" title="Chưa có lệnh thua">∞</span>'
                            : `<span class="font-mono">${bot.payoff_ratio.toFixed(2)}</span>`;
                        return `<tr>
                            ${lbBotCells(bot)}
                            <td>${lbWinRateCell(bot)}</td>
                            <td>${lbProfitFactorCell(bot)}</td>
                            <td>${payoff}</td>
                            <td>${lbReturnDdCell(bot)}</td>
                            ${lbTradesCell(bot)}
                            ${lbScoreCell(bot)}
                        </tr>`;
                    }).join('');
                }
            }
        }

        document.querySelectorAll('#lb-tab-group [data-lb-tab]').forEach(btn => {
            btn.addEventListener('click', () => {
                lbTab = btn.dataset.lbTab;
                try { localStorage.setItem('lb-tab', lbTab); } catch (e) { /* not persisted */ }
                // Both rankings are already loaded: switching tabs needs no request
                if (lbData) renderLeaderboard(lbData); else applyLbControls();
            });
        });
        function lbSetPeriod(period) {
            lbPeriod = period;
            try { localStorage.setItem('lb-period', lbPeriod); } catch (e) { /* not persisted */ }
            applyLbControls();
            fetchLeaderboard();
        }

        // --- Period picker popover ---
        const lbPeriodBtn = document.getElementById('lb-period-btn');
        const lbPeriodPop = document.getElementById('lb-period-pop');
        const lbCustomForm = document.getElementById('lb-period-custom');
        const lbFromInput = document.getElementById('lb-date-from');
        const lbToInput = document.getElementById('lb-date-to');
        const lbApplyBtn = document.getElementById('lb-date-apply');
        const lbDateError = document.getElementById('lb-date-error');

        function lbPopOpen() {
            return !!(lbPeriodPop && !lbPeriodPop.hidden);
        }

        // Under the button with the right edges lined up, above it when there is no room below,
        // and always inside the viewport, clear of the tab bar pinned to the bottom on phones
        function lbPlacePeriodPop() {
            if (!lbPopOpen()) return;
            const btn = lbPeriodBtn.getBoundingClientRect();
            const w = lbPeriodPop.offsetWidth, h = lbPeriodPop.offsetHeight;
            const bar = document.querySelector('.sidebar');
            const barTop = bar ? bar.getBoundingClientRect().top : window.innerHeight;
            const floor = (barTop > window.innerHeight / 2 ? barTop : window.innerHeight) - 8;
            const left = Math.max(8, Math.min(btn.right - w, window.innerWidth - w - 8));
            let top = btn.bottom + 6;
            if (top + h > floor) top = btn.top - h - 6 >= 8 ? btn.top - h - 6 : floor - h;
            lbPeriodPop.style.left = `${left}px`;
            lbPeriodPop.style.top = `${Math.max(8, top)}px`;
        }

        // The custom fields can only be applied as a range the server takes
        function lbCheckCustom() {
            const from = lbFromInput.value, to = lbToInput.value;
            const reversed = !!(from && to && from > to);
            lbFromInput.classList.toggle('lb-range-bad', reversed);
            lbToInput.classList.toggle('lb-range-bad', reversed);
            lbDateError.textContent = reversed ? 'Ngày đầu đang sau ngày cuối' : '';
            lbDateError.hidden = !reversed;
            lbApplyBtn.disabled = !lbRangeOk(from, to);
        }

        function lbOpenPeriodPop() {
            // Calendar presets show the days they cover today
            lbPeriodPop.querySelectorAll('.lb-period-opt[data-lb-period]').forEach(btn => {
                const range = lbRangeFor(btn.dataset.lbPeriod);
                const hint = btn.querySelector('.lb-period-hint');
                if (!range || !hint) return;
                hint.textContent = lbRangeText(range);
                btn.title = `${lbShortDay(range.from, true)} – ${lbShortDay(range.to, true)}, giờ Việt Nam`;
            });
            // The custom fields start from the days on screen, else the last custom range, else
            // the last 7 days
            const today = lbVnToday();
            const start = lbRangeFor(lbPeriod)
                || (lbDateFrom || lbDateTo ? {from: lbDateFrom, to: lbDateTo}
                                           : {from: lbIsoDay(lbAddDays(today, -6)), to: lbIsoDay(today)});
            lbFromInput.value = start.from;
            lbToInput.value = start.to;
            lbCheckCustom();
            lbPeriodPop.hidden = false;
            lbPeriodBtn.setAttribute('aria-expanded', 'true');
            lbPlacePeriodPop();
            const focus = lbPeriod === 'custom' ? lbFromInput
                : (lbPeriodPop.querySelector('.lb-period-opt.active') || lbPeriodPop.querySelector('.lb-period-opt'));
            if (focus) focus.focus();
        }

        function lbClosePeriodPop(refocus) {
            if (!lbPopOpen()) return;
            lbPeriodPop.hidden = true;
            lbPeriodBtn.setAttribute('aria-expanded', 'false');
            if (refocus) lbPeriodBtn.focus();
        }

        if (lbPeriodBtn && lbPeriodPop && lbCustomForm) {
            // Out from under the panel, whose overflow would clip it
            document.body.appendChild(lbPeriodPop);
            lbPeriodBtn.addEventListener('click', () => {
                if (lbPopOpen()) lbClosePeriodPop(false); else lbOpenPeriodPop();
            });
            lbPeriodPop.querySelectorAll('.lb-period-opt[data-lb-period]').forEach(btn => {
                btn.addEventListener('click', () => {
                    lbSetPeriod(btn.dataset.lbPeriod);
                    lbClosePeriodPop(true);
                });
            });
            [lbFromInput, lbToInput].forEach(input => {
                input.addEventListener('input', lbCheckCustom);
                input.addEventListener('change', lbCheckCustom);
            });
            // Apply, or Enter in a date field
            lbCustomForm.addEventListener('submit', e => {
                e.preventDefault();
                if (!lbRangeOk(lbFromInput.value, lbToInput.value)) return;
                lbDateFrom = lbFromInput.value;
                lbDateTo = lbToInput.value;
                try {
                    localStorage.setItem('lb-date-from', lbDateFrom);
                    localStorage.setItem('lb-date-to', lbDateTo);
                } catch (err) { /* not persisted */ }
                lbSetPeriod('custom');
                lbClosePeriodPop(true);
            });
            // A click or tap anywhere else, Escape, or tabbing out closes it
            document.addEventListener('pointerdown', e => {
                if (lbPopOpen() && !lbPeriodPop.contains(e.target) && !lbPeriodBtn.contains(e.target)) {
                    lbClosePeriodPop(false);
                }
            });
            document.addEventListener('keydown', e => {
                if (e.key === 'Escape' && lbPopOpen()) lbClosePeriodPop(true);
            });
            lbPeriodPop.addEventListener('focusout', e => {
                const next = e.relatedTarget;
                if (next && !lbPeriodPop.contains(next) && next !== lbPeriodBtn) lbClosePeriodPop(false);
            });
            window.addEventListener('resize', lbPlacePeriodPop);
            document.addEventListener('scroll', lbPlacePeriodPop, true);
        }
        applyLbControls();

        // First paint from the page's own payload (last 7 days, the page's account scope) when the
        // period is the default "1w"; otherwise the view's first fetch fills the tables.
        const lbInitial = DASHBOARD_BOOTSTRAP.leaderboard;
        if (lbInitial && lbInitial.period === lbPeriod) {
            lbShownQuery = lbQuery();
            renderLeaderboard(lbInitial);
        }

        const lbRefreshBtn = document.getElementById('lb-refresh-btn');
        if (lbRefreshBtn) {
            lbRefreshBtn.addEventListener('click', () => fetchLeaderboard());
        }

        // Periodic refresh for leaderboard if active
        setInterval(() => {
            if (lbViewActive() && !document.hidden) {
                fetchLeaderboard();
            }
        }, 8000);

        if (window.lucide) { lucide.createIcons(); }
