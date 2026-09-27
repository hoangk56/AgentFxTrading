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

            // Add active to matching nav item or topbar button
            const activeNav = document.querySelector(`.nav-item[data-target="${targetId}"]`);
            if (activeNav) activeNav.classList.add('active');
            const activeTopbarBtn = document.querySelector(`.topbar-action-btn[data-target="${targetId}"]`);
            if (activeTopbarBtn) activeTopbarBtn.classList.add('active');

            // Show corresponding view
            const targetView = document.getElementById(targetId);
            if (targetView) {
                targetView.classList.add('active');
                if (targetId === 'view-logs') {
                    fetchAgentLogs(logDateSelect.value);
                } else if (targetId === 'view-docker') {
                    fetchBots();
                } else if (targetId === 'view-leaderboard') {
                    fetchLeaderboard();
                } else if (targetId === 'view-backtest') {
                    btOnShow();
                } else if (targetId === 'view-ledger') {
                    ledgerOnShow();
                }
            }
        }

        // The open view lives in the URL hash (#backtest, #ledger, …; Overview has none),
        // so F5 and Back/Forward stay on it.
        function viewFromHash(hash) {
            const view = hash.length > 1 ? document.getElementById('view-' + hash.slice(1)) : null;
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

        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                openView(item.getAttribute('data-target'));
            });
        });

        const topbarDockerBtn = document.getElementById('topbar-docker-btn');
        if (topbarDockerBtn) {
            topbarDockerBtn.addEventListener('click', (e) => {
                e.preventDefault();
                openView('view-docker');
            });
        }

        window.addEventListener('popstate', () => switchView(viewFromHash(location.hash)));
        // Wait for DOMContentLoaded: switchView's loaders live further down this file and in the deferred
        // backtest.js / ledger.js.
        document.addEventListener('DOMContentLoaded', () => {
            const initialView = viewFromHash(location.hash);
            if (initialView !== 'view-dashboard') switchView(initialView);
        });
        // --- Docker Bot Management ---
        let botsFetchInFlight = false;   // a slow poll must not stack up behind itself
        let botActionInFlight = false;   // a poll must not re-render over a row that says "Stopping…"
        async function fetchBots() {
            if (botsFetchInFlight || botActionInFlight) return;
            botsFetchInFlight = true;
            try {
                const res = await fetch("/api/bots");
                const data = await res.json();
                renderBots(data.bots, data.docker_available);
            } catch(e) { console.error("Error fetching bots", e); }
            finally { botsFetchInFlight = false; }
        }
        function renderBots(bots, dockerOk) {
            const tbody = document.getElementById("bots-tbody");
            if(!dockerOk) {
                tbody.innerHTML = `<tr><td colspan="7" class="td-dim" style="color:var(--color-loss)">Docker is not available on the server. Please ensure Docker daemon is running.</td></tr>`;
                return;
            }
            if(!bots || bots.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" class="td-dim">No bots configured.</td></tr>`;
                return;
            }
            
            const targetType = (currentMode === 'real' || currentMode === 'live') ? 'live' : 'demo';
            const filteredBots = bots.filter(b => (b.account_type || 'demo') === targetType);
                
            if(!filteredBots.length) {
                tbody.innerHTML = `<tr><td colspan="7" class="td-dim">No ${targetType.toUpperCase()} bots configured. Use "+ Add Bot" to create one.</td></tr>`;
                return;
            }
            let html = "";
            filteredBots.forEach(b => {
                const isRunning = b.status === "running";
                let statusHtml = `<span style="color:var(--color-dim)">${escapeHtml(b.status)}</span>`;
                if (b.stuck) {
                    statusHtml = `<span style="color:var(--color-loss); font-weight:bold;" title="${escapeHtml(b.health_reason || 'Bot is stuck')}">⚠️ STUCK</span>`;
                } else if (isRunning) {
                    statusHtml = `<span style="color:var(--color-profit)">● running</span>`;
                } else if (b.status === "error") {
                    statusHtml = `<span style="color:var(--color-loss)">● error</span>`;
                }
                // Escaped once for text and attributes alike; dataset hands the Edit form the decoded values.
                const escapedName = escapeHtml(b.name);
                const escapedCmd = escapeHtml(b.run_command || '');
                const escapedDesc = escapeHtml(b.description || '');
                const modeBadge = (b.account_type === 'live')
                    ? '<span class="badge badge--live"><span class="badge-dot"></span>LIVE</span>'
                    : '<span class="badge badge--demo"><span class="badge-dot"></span>DEMO</span>';
                // Pause blocks new entries only; the container keeps managing its open positions.
                const pausedHtml = b.paused
                    ? ' <span class="badge" style="background:rgba(245,158,11,0.15); color:#f59e0b;" title="New entries blocked from the dashboard; open positions are still managed">PAUSED</span>'
                    : '';
                // A running bot asks /api/cbot/commands every 2 s. One that doesn't can't be reached
                // by Close / Close & Stop (they expire), and its own pause guard never hears of a Pause.
                const lastPoll = (b.last_poll_age_s === null || b.last_poll_age_s === undefined)
                    ? 'since the service started' : `for ${b.last_poll_age_s} s`;
                const notPollingTitle = `No command poll from bot_id "${b.bot_id}" ${lastPoll}. Close and Close & Stop can't reach this bot and Pause may not stop its entries. Usual causes: still logging in, an .algo built before the command poll, CommandPollMs=0, or the bot reports a BotId other than this container's --BotId.`;
                const notPollingHtml = (isRunning && !b.polling)
                    ? ` <span class="badge" style="background:rgba(229,57,53,0.12); color:var(--loss);" title="${escapeHtml(notPollingTitle)}">NOT POLLING</span>`
                    : '';
                const pauseBtn = b.paused
                    ? `<button class="log-btn action-resume" data-name="${escapedName}" style="background:rgba(125,189,30,0.15); color:var(--profit); margin-right:4px;">Resume</button>`
                    : `<button class="log-btn action-pause" data-name="${escapedName}" style="background:rgba(255,193,7,0.15); color:#f59e0b; margin-right:4px;">Pause</button>`;
                const closeStopBtn = isRunning
                    ? `<button class="log-btn action-close-stop" data-name="${escapedName}" data-open="${b.open_positions || 0}" data-live="${b.account_type === 'live' ? '1' : '0'}" style="background:var(--loss); color:#fff; margin-right:4px;">Close &amp; Stop</button>`
                    : '';
                
                html += `<tr>
                    <td><strong>${escapedName}</strong></td>
                    <td>${modeBadge}</td>
                    <td>${statusHtml}${pausedHtml}${notPollingHtml}</td>
                    <td class="td-dim">${b.container_id ? b.container_id.substring(0,12) : "-"}</td>
                    <td class="td-dim">${escapedDesc || "-"}</td>
                    <td class="td-dim" style="font-family:monospace; max-width:240px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis" title="${escapedCmd}">${escapedCmd}</td>
                    <td style="text-align:right; white-space:nowrap;">
                        ${pauseBtn}${closeStopBtn}${isRunning
                            ? `<button class="log-btn action-restart" data-name="${escapedName}" style="background:rgba(255,193,7,0.15); color:#f59e0b; margin-right:4px;">Restart</button><button class="log-btn action-stop" data-name="${escapedName}" style="background:rgba(229,57,53,0.15); color:var(--loss);">Stop</button>`
                            : `<button class="log-btn action-start" data-name="${escapedName}" style="background:rgba(125,189,30,0.15); color:var(--profit);">Start</button>`
                        }
                        <button class="log-btn action-edit" data-name="${escapedName}" data-desc="${escapedDesc}" data-cmd="${escapedCmd}" style="background:var(--bg-elevated); margin:0 4px;">Edit</button>
                        <button class="log-btn action-delete" data-name="${escapedName}">Delete</button>
                    </td>
                </tr>`;
            });
            tbody.innerHTML = html;
            
            document.querySelectorAll(".action-start").forEach(btn => btn.addEventListener("click", e => actionBot(e.currentTarget.dataset.name, "start", e.currentTarget)));
            document.querySelectorAll(".action-stop").forEach(btn => btn.addEventListener("click", e => actionBot(e.currentTarget.dataset.name, "stop", e.currentTarget)));
            document.querySelectorAll(".action-delete").forEach(btn => btn.addEventListener("click", e => deleteBot(e.currentTarget.dataset.name, e.currentTarget)));
            document.querySelectorAll(".action-restart").forEach(btn => btn.addEventListener("click", e => actionBot(e.currentTarget.dataset.name, "restart", e.currentTarget)));
            document.querySelectorAll(".action-pause").forEach(btn => btn.addEventListener("click", e => actionBot(e.currentTarget.dataset.name, "pause", e.currentTarget)));
            document.querySelectorAll(".action-resume").forEach(btn => btn.addEventListener("click", e => actionBot(e.currentTarget.dataset.name, "resume", e.currentTarget)));
            document.querySelectorAll(".action-close-stop").forEach(btn => btn.addEventListener("click", e => closeAndStopBot(e.currentTarget)));
            document.querySelectorAll(".action-edit").forEach(btn => btn.addEventListener("click", e => {
                const bName = btn.dataset.name;
                const bDesc = btn.dataset.desc;
                const bCmd = btn.dataset.cmd;
                
                document.getElementById("bot-form-mode").value = "edit";
                document.getElementById("bot-form-title").textContent = `Edit Bot Configuration: ${bName}`;
                const nameInput = document.getElementById("bot-name");
                nameInput.value = bName;
                nameInput.disabled = true; // Bot name is key, don't change in-place
                document.getElementById("bot-desc").value = bDesc;
                document.getElementById("bot-cmd").value = bCmd;
                
                document.getElementById("bot-form-container").style.display = "block";
                document.getElementById("save-restart-bot-btn").style.display = "inline-flex";
                document.getElementById("bot-cmd").focus();
            }));
        }
        const BOT_ACTION_PENDING = { start: "Starting…", stop: "Stopping…", restart: "Restarting…", delete: "Deleting…",
                                     pause: "Pausing…", resume: "Resuming…", "close-and-stop": "Closing & stopping…" };
        // Docker stop/restart wait up to 10 s for the cBot to exit; lock the row and say so meanwhile.
        function lockBotRow(btn, action) {
            const buttons = btn ? Array.from(btn.closest("tr").querySelectorAll("button")) : [];
            buttons.forEach(b => { b.disabled = true; });
            if (btn) btn.textContent = BOT_ACTION_PENDING[action] || "Working…";
            botActionInFlight = true;
            return () => { botActionInFlight = false; buttons.forEach(b => { b.disabled = false; }); fetchBots(); };
        }
        async function actionBot(name, action, btn) {
            const unlock = lockBotRow(btn, action);
            try {
                const res = await fetch(`/api/bots/${name}/${action}`, { method: "POST" });
                const data = await res.json();
                if(!data.success) alert(data.message || "Error");
            } catch(e) { alert("Error: " + e); }
            finally { unlock(); }
        }
        // Kill switch: pause, close every position the bot holds, then stop the container. The server
        // stops it only when the bot confirms every close; otherwise it keeps running, paused.
        async function closeAndStopBot(btn) {
            const name = btn.dataset.name;
            const n = btn.dataset.open || '0';
            const prefix = btn.dataset.live === '1' ? '[LIVE] ' : '';
            if (!confirm(`${prefix}Close ${n} open position(s) of ${name} at market, then stop the container?\n\nThe bot is paused first. If a position cannot be closed, the container keeps running (paused) so it still manages its stops.`)) return;
            const unlock = lockBotRow(btn, "close-and-stop");
            try {
                const res = await fetch(`/api/bots/${name}/close-and-stop`, { method: "POST" });
                const data = await res.json();
                alert(data.message || (data.success ? "Done" : "Error"));
            } catch(e) { alert("Error: " + e); }
            finally { unlock(); }
        }
        async function deleteBot(name, btn) {
            if(!confirm(`Delete bot ${name}? This stops and removes its container.`)) return;
            const unlock = lockBotRow(btn, "delete");
            try {
                const res = await fetch(`/api/bots/${name}`, { method: "DELETE" });
                const data = await res.json();
                if(!data.success) alert(data.message || "Error deleting bot");
            } catch(e) { alert("Error: " + e); }
            finally { unlock(); }
        }
        
        async function submitBotForm(restart = false) {
            const mode = document.getElementById("bot-form-mode").value;
            const name = document.getElementById("bot-name").value.trim();
            const desc = document.getElementById("bot-desc").value.trim();
            const cmd = document.getElementById("bot-cmd").value.trim();
            
            if (!name || !cmd) return alert("Bot Name and Command are required.");
            
            try {
                let res, data;
                if (mode === "edit") {
                    res = await fetch(`/api/bots/${name}/update`, {
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
                if (!data.success) {
                    return alert(data.message || "Error saving bot");
                }
                document.getElementById("bot-form-container").style.display = "none";
                fetchBots();
            } catch(e) {
                alert("Error saving bot: " + e);
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
            let html = `<option value="">— select account —</option>`;
            setupAccounts.forEach(a => {
                html += `<option value="${a.id}">${a.account_type.toUpperCase()} · ${setupEscape(a.label)} (${setupEscape(a.account_number)})</option>`;
            });
            html += `<option value="${SETUP_NEW_ACCOUNT}">＋ New account…</option>`;
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
            setupEl("setup-grid-head").innerHTML = `<th>Symbol</th>` + strategies.map(s =>
                `<th style="text-align:center"><label style="cursor:pointer; white-space:nowrap;"><input type="checkbox" class="setup-col-all" data-strategy="${s}" title="Select all ${setupEscape(p.strategies[s].label)}"> ${setupEscape(p.strategies[s].label)}</label></th>`
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
                note.title = "Already created for:\n" + rows.map(r =>
                    `${r.name} · ${r.account_type.toUpperCase()} · ${r.account_label}`).join("\n");
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
            setupEl("setup-panel").style.display = "block";
            setupEl("setup-results").innerHTML = "";
            try {
                renderSetupGrid(await fetchSetupPresets());
            } catch (e) {
                setupEl("setup-grid-body").innerHTML = `<tr><td class="td-dim" style="color:var(--loss)">Failed to load presets: ${setupEscape(e)}</td></tr>`;
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
            msg.textContent = "Saving…";
            try {
                const res = await fetch("/api/ctrader-accounts", {
                    method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)
                });
                const data = await res.json();
                if (!res.ok || !data.success) { msg.textContent = data.message || `Error ${res.status}`; return; }
                msg.textContent = "";
                setupEl("setup-acc-password").value = "";
                await fetchCtraderAccounts(data.account.id);
            } catch (e) { msg.textContent = "Error: " + e; }
        }

        async function deleteCtraderAccount() {
            const id = setupEl("setup-account").value;
            const acc = setupAccounts.find(a => String(a.id) === id);
            if (!acc) return;
            if (!confirm(`Delete account "${acc.label}" (${acc.account_number})?\nExisting bot configs keep working; the stored password file is removed.`)) return;
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
            list.innerHTML = `<li class="td-dim">Creating ${payload.selections.length} instance(s)…</li>`;
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
                list.innerHTML = `<li style="color:var(--loss)">Error: ${setupEscape(e)}</li>`;
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
                document.getElementById("bot-form-title").textContent = "Add New Bot Configuration";
                const nameInput = document.getElementById("bot-name");
                nameInput.value = "";
                nameInput.disabled = false;
                document.getElementById("bot-desc").value = "";
                document.getElementById("bot-cmd").value = "";
                document.getElementById("save-restart-bot-btn").style.display = "none";
                formContainer.style.display = "block";
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
            return `${sign}${Math.abs(n).toFixed(2)}`;
        }
        function pnlClass(v){return Number(v)>=0?'kpi-value--profit':'kpi-value--loss'}
        function accountBadge(t){return t==='live'?'<span class="badge badge--live"><span class="badge-dot"></span>LIVE</span>':'<span class="badge badge--demo"><span class="badge-dot"></span>DEMO</span>'}
        function sideChip(s){const c=s==='BUY'?'side-chip--buy':'side-chip--sell';return `<span class="side-chip ${c}">${escapeHtml(s)}</span>`}
        // Single renderer for the P&L cell, shared by the row builder and the live tick handler.
        // Only the broker's own figure is shown; a missing one reads as "—" rather than a guess.
        function pnlCellHtml(pnl, pips){
            if(pnl===null||pnl===undefined){
                return '<span class="td-dim" title="broker-reported P&L arrives with the bot\'s next snapshot">—</span>';
            }
            const v=Number(pnl)||0, p=Number(pips)||0;
            const cls=v>=0?'pnl-chip--profit':'pnl-chip--loss';
            return `<span class="pnl-chip ${cls}">${v>0?'+':''}$${v.toFixed(2)} (${p>0?'+':''}${p.toFixed(1)}p)</span>`;
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
                            ? '<span class="sltp-chip" title="Trailing stop: the bot moves it up behind price. The position closes when price comes back to it, keeping this profit.">trailing</span>'
                            : '<span class="sltp-chip" title="Stop is past break-even: if price comes back to it the position still closes at this profit.">locked</span>';
                    }
                }
            } else if(noTp){
                body='<span class="sltp-none" title="No take-profit at the broker: the bot exits on its own rule (fix time, channel, max hold) or at the SL.">none · exits at SL</span>';
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
                     + (t.duration ? `<span class="duration-chip" title="Time in trade">${escapeHtml(t.duration)}</span>` : ''));
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
            const isD=bl.includes('donchian');
            const badgeCls = isG ? 'bot-badge--gotobi' : (isD ? 'bot-badge--donchian' : 'bot-badge--default');
            const badgeText = isG ? 'Gotobi' : (isD ? 'Donchian' : 'cBot');
            const safe=escapeHtml(b);
            return `<div class="bot-cell">
                <span class="bot-badge ${badgeCls}"><span class="bot-dot"></span>${badgeText}</span>
                <span class="bot-id-text" title="${safe}">${safe}</span>
            </div>`;
        }

        let currentMode = DASHBOARD_BOOTSTRAP.currentMode || 'demo';
        let selectedAccountId = (currentMode === 'real' || currentMode === 'live') ? 'live' : 'demo';
        const accountSelector = document.getElementById('account-selector');

        const HISTORY_PAGE_SIZE = 10;
        let historyPage = 1;
        function historyUrl() {
            return `/api/dashboard/history?account_id=${selectedAccountId}&page=${historyPage}&page_size=${HISTORY_PAGE_SIZE}`;
        }

        async function fetchTradeHistory() {
            try {
                const [hR, cR] = await Promise.all([
                    fetch(historyUrl()),
                    fetch(`/api/dashboard/pnl-history?account_id=${selectedAccountId}`)
                ]);
                updateTradeHistory(await hR.json());
                updatePnlChart(await cR.json());
            } catch(e) { console.error('Error fetching trade history:', e); }
        }

        async function refreshDashboardData() {
            try {
                const [sR, pR, hR, cR] = await Promise.all([
                    fetch(`/api/dashboard/summary?account_id=${selectedAccountId}`),
                    fetch(`/api/dashboard/positions?account_id=${selectedAccountId}`),
                    fetch(historyUrl()),
                    fetch(`/api/dashboard/pnl-history?account_id=${selectedAccountId}`)
                ]);
                updateDashboard(await sR.json(), await pR.json());
                updateTradeHistory(await hR.json());
                updatePnlChart(await cR.json());
            } catch(err) { console.error('Fetch error:', err); }
        }

        // Mode switcher buttons navigate cleanly to respective URL routes, keeping the open view (hash)
        document.querySelectorAll('.trade-mode-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const targetMode = btn.dataset.mode;
                if (targetMode === 'real' || targetMode === 'live') {
                    window.location.href = '/real/dashboard' + location.hash;
                } else {
                    window.location.href = '/demo/dashboard' + location.hash;
                }
            });
        });

        // Attach account selector change listener
        accountSelector.addEventListener('change', async (e) => {
            selectedAccountId = e.target.value;
            historyPage = 1;
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({type: 'subscribe', account_id: selectedAccountId, mode: currentMode}));
            }
            refreshDashboardData();
            fetchLeaderboard();
            if (typeof ledgerRefreshIfShown === 'function') ledgerRefreshIfShown();
        });

        let rawDailyHistory = DASHBOARD_BOOTSTRAP.pnlHistory;
        let initialExposure = DASHBOARD_BOOTSTRAP.exposure;

        // 1. Daily P&L Bar Chart
        const pnlCtx = document.getElementById('pnl-chart').getContext('2d');
        const pnlChart = new Chart(pnlCtx, {
            type: 'bar',
            data: {
                labels: rawDailyHistory.map(d=>d.date),
                datasets: [{
                    label: 'Daily P&L',
                    data: rawDailyHistory.map(d=>d.pnl),
                    backgroundColor: rawDailyHistory.map(d=>d.pnl>=0?'rgba(125,189,30,0.6)':'rgba(229,57,53,0.6)'),
                    borderColor: rawDailyHistory.map(d=>d.pnl>=0?'rgba(125,189,30,1)':'rgba(229,57,53,1)'),
                    borderWidth: 1,
                    borderRadius: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { backgroundColor: '#1e293b', titleColor: '#f0f0f0', bodyColor: '#a0a0a0' }
                },
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(64,64,64,0.3)' }, ticks: { color: '#a0a0a0', callback: v => '$' + v } },
                    x: { grid: { display: false }, ticks: { color: '#a0a0a0', maxRotation: 0 } }
                }
            }
        });

        // 2. Cumulative Equity Curve Line Chart
        const equityCtx = document.getElementById('equity-chart').getContext('2d');
        let cumInit = 0;
        const cumInitData = rawDailyHistory.map(d => { cumInit += (d.pnl || 0); return parseFloat(cumInit.toFixed(2)); });
        const equityChart = new Chart(equityCtx, {
            type: 'line',
            data: {
                labels: rawDailyHistory.map(d=>d.date),
                datasets: [{
                    label: 'Cumulative Equity',
                    data: cumInitData,
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.12)',
                    fill: true,
                    tension: 0.25,
                    borderWidth: 2,
                    pointRadius: 3,
                    pointBackgroundColor: '#38bdf8'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { backgroundColor: '#1e293b', titleColor: '#f0f0f0', bodyColor: '#a0a0a0' }
                },
                scales: {
                    y: { beginAtZero: false, grid: { color: 'rgba(64,64,64,0.3)' }, ticks: { color: '#a0a0a0', callback: v => '$' + v } },
                    x: { grid: { display: false }, ticks: { color: '#a0a0a0', maxRotation: 0 } }
                }
            }
        });

        function updatePnlChart(h) {
            rawDailyHistory = h;
            // Update Daily Bar Chart
            pnlChart.data.labels = h.map(d=>d.date);
            pnlChart.data.datasets = [{
                label: 'Daily P&L',
                data: h.map(d=>d.pnl),
                backgroundColor: h.map(d=>d.pnl>=0?'rgba(125,189,30,0.6)':'rgba(229,57,53,0.6)'),
                borderColor: h.map(d=>d.pnl>=0?'rgba(125,189,30,1)':'rgba(229,57,53,1)'),
                borderWidth: 1,
                borderRadius: 2
            }];
            pnlChart.update();

            // Update Cumulative Equity Chart
            let cum = 0;
            const cumData = h.map(d => { cum += (d.pnl || 0); return parseFloat(cum.toFixed(2)); });
            equityChart.data.labels = h.map(d=>d.date);
            equityChart.data.datasets = [{
                label: 'Cumulative Equity',
                data: cumData,
                borderColor: '#38bdf8',
                backgroundColor: 'rgba(56, 189, 248, 0.12)',
                fill: true,
                tension: 0.25,
                borderWidth: 2,
                pointRadius: 3,
                pointBackgroundColor: '#38bdf8'
            }];
            equityChart.update();
        }

        // Asset Exposure Doughnut Chart
        const expCtx = document.getElementById('exposure-chart').getContext('2d');
        let exposureChart = new Chart(expCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(initialExposure.by_asset_class || {}),
                datasets: [{
                    data: Object.values(initialExposure.by_asset_class || {}),
                    backgroundColor: ['#f59e0b', '#3b82f6', '#10b981', '#8b5cf6'],
                    borderWidth: 1,
                    borderColor: '#1e293b'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 10, color: '#a0a0a0', font: { size: 10 } } }
                },
                cutout: '65%'
            }
        });

        function updateExposureChart(positions) {
            const byClass = { "Forex": 0.0, "Gold/Metals": 0.0, "Crypto": 0.0, "Indices": 0.0 };
            let totalVol = 0;
            positions.forEach(p => {
                const sym = (p.symbol || '').toUpperCase();
                const vol = parseFloat(p.volume) || 0;
                totalVol += vol;
                if (sym.includes('BTC') || sym.includes('ETH') || sym.includes('SOL')) byClass['Crypto'] += vol;
                else if (sym.includes('XAU') || sym.includes('GOLD')) byClass['Gold/Metals'] += vol;
                else if (sym.includes('US30') || sym.includes('USTEC') || sym.includes('DE40') || sym.includes('UK100')) byClass['Indices'] += vol;
                else byClass['Forex'] += vol;
            });
            const filtered = Object.entries(byClass).filter(([_, v]) => v > 0);
            const emptyMsg = document.getElementById('exposure-empty-msg');
            const expCanvas = document.getElementById('exposure-chart');
            if (!filtered.length) {
                if (emptyMsg) emptyMsg.style.display = 'block';
                if (expCanvas) expCanvas.style.display = 'none';
            } else {
                if (emptyMsg) emptyMsg.style.display = 'none';
                if (expCanvas) expCanvas.style.display = 'block';
                exposureChart.data.labels = filtered.map(([k]) => k);
                exposureChart.data.datasets[0].data = filtered.map(([_, v]) => parseFloat(v.toFixed(2)));
                exposureChart.update();
            }
        }
        updateExposureChart(DASHBOARD_BOOTSTRAP.positions);
        let ws=null,pingInterval=null;
        function setConn(on){const el=document.getElementById('connection-status');if(on){el.className='status-pill status-pill--online';el.innerHTML='<span class="status-dot"></span><span>Connected</span>'}else{el.className='status-pill status-pill--offline';el.innerHTML='<span class="status-dot"></span><span>Disconnected</span>'}}
        function connectWebSocket(){
            const p=window.location.protocol==='https:'?'wss:':'ws:';
            ws=new WebSocket(`${p}//${window.location.host}/ws/dashboard`);
            ws.onopen=()=>{
                setConn(true);
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({type:'subscribe',account_id:selectedAccountId,mode:currentMode}));
                }
                refreshDashboardData();
                if (typeof fetchLeaderboard === 'function') fetchLeaderboard();
                if (pingInterval) clearInterval(pingInterval);
                pingInterval=setInterval(()=>{
                    if(ws.readyState===WebSocket.OPEN)
                        ws.send(JSON.stringify({type:'ping',account_id:selectedAccountId,mode:currentMode}))
                },15000);
            };
            ws.onmessage=(e)=>{
                try {
                    const d=JSON.parse(e.data);
                    if(d.type==='update') {
                        const isAllForMode = (selectedAccountId === 'demo' || selectedAccountId === 'live');
                        const matchesAccount = (!d.account_id) || 
                                               (d.account_id === selectedAccountId) || 
                                               (selectedAccountId === 'all') || 
                                               (isAllForMode && (d.account_id === currentMode || d.account_id === selectedAccountId));
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
                        } else if (selectedAccountId !== 'demo' && selectedAccountId !== 'live' && selectedAccountId !== 'all') {
                            if (d.account_id === currentMode || d.account_id === 'all') {
                                refreshDashboardData();
                                if (typeof fetchLeaderboard === 'function') fetchLeaderboard();
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
            // Update matching row in positions table
            const rows = document.querySelectorAll('#positions-table tr');
            rows.forEach(tr => {
                const symCell = tr.querySelector('.td-mono.font-bold');
                if (symCell && symCell.textContent.trim().toUpperCase() === tick.symbol.toUpperCase()) {
                    const curPriceCell = tr.querySelector('.td-current-price');
                    if (curPriceCell) {
                        const sideBadge = tr.querySelector('.side-chip');
                        const isBuy = sideBadge && sideBadge.textContent.includes('BUY');
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
        function updateDashboard(summary,positions){
            document.getElementById('open-positions').textContent=summary.open_positions;
            const dEl=document.getElementById('daily-pnl');dEl.textContent=formatMoney(summary.daily_pnl);dEl.className=`kpi-value ${pnlClass(summary.daily_pnl)}`;
            const tEl=document.getElementById('total-pnl');tEl.textContent=formatMoney(summary.total_pnl);tEl.className=`kpi-value ${pnlClass(summary.total_pnl)}`;
            document.getElementById('win-rate').textContent=`${summary.win_rate}%`;
            const pfEl=document.getElementById('profit-factor');
            if(pfEl){
                if(summary.profit_factor!==undefined && summary.profit_factor!==null && summary.total_trades>0){
                    pfEl.textContent=Number(summary.profit_factor).toFixed(2);
                    pfEl.className=`kpi-value kpi-value--mono ${summary.profit_factor>=1.5?'kpi-value--profit':(summary.profit_factor<1.0?'kpi-value--loss':'')}`;
                } else {
                    pfEl.textContent='--';
                    pfEl.className='kpi-value kpi-value--mono';
                }
            }
            document.getElementById('trades-today').textContent=summary.trades_today;
            const lEl=document.getElementById('loss-streak');lEl.textContent=summary.loss_streak;lEl.className=`kpi-value ${summary.loss_streak>=3?'kpi-value--warn':''}`;
            document.getElementById('last-updated').textContent=new Date().toLocaleTimeString();
            const isMultiAcc = (selectedAccountId === 'demo' || selectedAccountId === 'live' || selectedAccountId === 'all');
            document.querySelectorAll('.col-account').forEach(el => { isMultiAcc ? el.classList.remove('hidden') : el.classList.add('hidden') });
            const bC=document.getElementById('account-balance'),eC=document.getElementById('account-equity');
            if(bC)bC.textContent=formatMoney(summary.account_balance||0);
            if(eC)eC.textContent=formatMoney(summary.account_equity||0);
            
            const posCountEl = document.getElementById('active-pos-count');
            if (posCountEl) posCountEl.textContent = positions.length ? `${positions.length} Open` : '0 Open';

            const tb=document.getElementById('positions-table'),ah=isMultiAcc?'':'hidden';
            if(!positions.length){
                tb.innerHTML='<tr><td colspan="11" class="empty-state">No active positions</td></tr>';
            } else {
                tb.innerHTML=positions.map(p=>{
                    const curPrice = (p.current_price !== undefined && p.current_price !== null) ? p.current_price : p.entry_price;
                    const priceAge = (typeof p.price_age_seconds === 'number') ? `<span class="td-dim" title="price from the bot's last snapshot"> ·${Math.floor(p.price_age_seconds/60)}m</span>` : '';
                    const pnlCell = pnlCellHtml(p.unrealized_pnl, p.unrealized_pnl_pips);
                    
                    return `<tr data-bot="${escapeHtml(p.bot_id||'')}">
                        <td class="col-account account-cell ${ah}">${accountBadge(p.account_type)}<span class="account-name">${escapeHtml(p.account_label||'')}</span></td>
                        <td>${botBadge(p.bot_id)}</td>
                        <td class="td-mono font-bold">${escapeHtml(p.symbol)}</td>
                        <td>${sideChip(p.side)}</td>
                        <td>${escapeHtml(p.volume)}L</td>
                        <td class="td-mono">${escapeHtml(p.entry_price)}</td>
                        <td class="td-mono td-current-price">${escapeHtml(curPrice)}${priceAge}</td>
                        <td class="td-sltp">${sltpCellHtml(p, true)}</td>
                        <td class="td-pnl-live">${pnlCell}</td>
                        <td class="td-dim">${escapeHtml(p.entry_time)}</td>
                        <td class="td-actions">${closeButtonHtml(p)}</td>
                    </tr>`;
                }).join('');
            }
            if (typeof updateExposureChart === 'function') {
                updateExposureChart(positions);
            }
        }
        // --- Manual close (Close button in Active Positions) ---
        // The dashboard queues the close; the position's bot picks it up within ~2 s, closes it at
        // market and reports back. The existing broadcast then removes the row.
        const closingPositions = new Set();   // row ids with a close in flight (survives re-renders)
        const COMMAND_FAILURE_TEXT = {
            expired: 'The bot did not pick up the command within 15 s - it may be stuck or running an old build. Close the position in cTrader.',
            unconfirmed: 'The bot received the command but never reported back. Check the position in cTrader.',
        };
        function commandFailureText(cmd) {
            return COMMAND_FAILURE_TEXT[cmd.status] || `Close failed: ${cmd.message || cmd.status}`;
        }
        function closeButtonHtml(p) {
            const closing = closingPositions.has(String(p.id));
            const noId = !p.ctrader_id;
            const title = noId ? ' title="No cTrader id recorded for this position - close it in cTrader"' : '';
            return `<button class="log-btn action-close-pos" data-id="${p.id}" data-bot="${escapeHtml(p.bot_id||'')}" data-symbol="${escapeHtml(p.symbol||'')}" data-side="${escapeHtml(p.side||'')}" data-volume="${escapeHtml(p.volume)}" data-live="${p.account_type==='live'?'1':'0'}"${(noId||closing)?' disabled':''}${title} style="background:rgba(229,57,53,0.15); color:var(--loss);">${closing?'Closing…':'Close'}</button>`;
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
            const tr = btn.closest('tr');
            const pnlCell = tr ? tr.querySelector('.td-pnl-live') : null;
            const pnlText = pnlCell ? pnlCell.textContent.trim() : '';
            const prefix = d.live === '1' ? '[LIVE] ' : '';
            if (!confirm(`${prefix}Close ${d.side} ${d.symbol} ${d.volume}L of ${d.bot} at market?\nCurrent P&L: ${pnlText || 'n/a'}`)) return;
            closingPositions.add(String(d.id));
            btn.disabled = true;
            btn.textContent = 'Closing…';
            try {
                const res = await fetch(`/api/positions/${d.id}/close`, { method: 'POST' });
                const data = await res.json();
                if (!data.success) throw new Error(data.message || 'Close refused');
                const cmd = await waitForBotCommand(data.command_id);
                if (cmd.status !== 'done') throw new Error(commandFailureText(cmd));
                refreshDashboardData();   // the broadcast normally removes the row first
            } catch (err) {
                closingPositions.delete(String(d.id));
                // updateDashboard() may have re-rendered the table while this waited, so `btn` can be
                // a detached copy: re-enable whichever button shows this row now.
                document.querySelectorAll(`#positions-table .action-close-pos[data-id="${d.id}"]`)
                    .forEach(b => { b.disabled = false; b.textContent = 'Close'; });
                alert(String((err && err.message) || err));
            } finally {
                closingPositions.delete(String(d.id));
            }
        }
        document.getElementById('positions-table').addEventListener('click', e => {
            const btn = e.target.closest('.action-close-pos');
            if (btn && !btn.disabled) closePosition(btn);
        });

        // Periodic Session Status Refresher
        async function refreshMarketSessions() {
            try {
                const res = await fetch('/api/dashboard/sessions');
                if (!res.ok) return;
                const s = await res.json();
                const setPill = (id, active) => {
                    const el = document.getElementById(id);
                    if (el) el.className = `session-pill ${active ? 'session-pill--active' : ''}`;
                };
                setPill('sess-sydney', s.sessions.sydney.active);
                setPill('sess-tokyo', s.sessions.tokyo.active);
                setPill('sess-london', s.sessions.london.active);
                setPill('sess-ny', s.sessions.new_york.active);

                const fxBadge = document.getElementById('market-forex-badge');
                if (fxBadge) {
                    fxBadge.className = `badge ${s.is_forex_weekend ? 'badge--warn' : 'badge--live'}`;
                    fxBadge.textContent = `Forex: ${s.forex_status}`;
                }
            } catch(e) { }
        }
        setInterval(refreshMarketSessions, 60000);
        function updateTradeHistory(page){
            const history = page.items || [];
            const totalPages = page.total_pages || 1;
            if ((page.page || 1) > totalPages) { historyPage = totalPages; fetchTradeHistory(); return; }
            historyPage = page.page || 1;
            const label=document.getElementById('history-page-label');
            if(label) label.textContent=`Page ${historyPage} / ${totalPages}`;
            const prev=document.getElementById('history-prev'), next=document.getElementById('history-next');
            if(prev) prev.disabled = historyPage <= 1;
            if(next) next.disabled = historyPage >= totalPages;
            const isMultiAcc = (selectedAccountId === 'demo' || selectedAccountId === 'live' || selectedAccountId === 'all');
            const tb=document.getElementById('history-table');if(!tb)return;const ah=isMultiAcc?'':'hidden';
            if(!history.length){
                tb.innerHTML='<tr><td colspan="11" class="empty-state">No trade history</td></tr>';
            } else {
                tb.innerHTML=history.map(t=>`<tr>
                    <td class="col-account account-cell ${ah}">${accountBadge(t.account_type)}<span class="account-name">${escapeHtml(t.account_label||'')}</span></td>
                    <td>${botBadge(t.bot_id)}</td>
                    <td class="td-mono font-bold">${escapeHtml(t.symbol)}</td>
                    <td>${sideChip(t.side)}</td>
                    <td>${escapeHtml(t.volume)}L</td>
                    <td class="td-mono">${escapeHtml(t.entry_price)}</td>
                    <td class="td-mono">${escapeHtml(t.exit_price)}</td>
                    <td class="td-sltp">${sltpCellHtml(t, false)}</td>
                    <td class="${Number(t.pnl)>=0?'pnl-positive':'pnl-negative'} font-bold">${Number(t.pnl)>0?'+':''}${formatMoney(t.pnl)}</td>
                    <td class="td-reason">${closeReasonHtml(t.close_reason)}</td>
                    <td class="td-times">${tradeTimesHtml(t)}</td>
                </tr>`).join('');
            }
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
            } else if (formatted.includes('[ERROR]') || formatted.includes('Error:')) {
                formatted = formatted.replace(/\[ERROR\s*\]|Error:/, '<span class="log-tag-error">$&</span>');
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
                const msg = (currentMode === 'real' || currentMode === 'live')
                    ? 'No LIVE log entries found for this date. (Bots may be outside trading hours or check Demo mode).'
                    : 'No DEMO log entries found for this date. (Bots are currently running on LIVE. Check Real mode or select a past date).';
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
                const base = `/api/dashboard/logs?lines=150&mode=${currentMode}&account_id=${selectedAccountId}`;
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
        const LB_ROLLING = {'1d': 'Last 24 hours', '1w': 'Last 7 days', '1m': 'Last 30 days',
                            '6m': 'Last 6 months', '1y': 'Last 12 months', 'all': 'All time'};
        const LB_CALENDAR = {today: 'Today', yesterday: 'Yesterday', thisweek: 'This week',
                             lastweek: 'Last week', thismonth: 'This month', lastmonth: 'Last month'};
        const LB_DAY_RE = /^\d{4}-\d{2}-\d{2}$/;
        const LB_WEIGHT_HINTS = {
            usd: 'Weight: 30% WinRate + 30% ProfitFactor + 20% NetPnL + 20% Consistency',
            lot: 'Weight: 30% WinRate + 30% ProfitFactor + 20% Return/DD + 20% Consistency · each closed trade over its risk at entry',
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
            if (!from) return `until ${to}`;
            if (!to) return `from ${from}`;
            return from === to ? from : `${from} – ${to}`;
        }

        // What the period button reads: the preset's name, and the days it covers when it has any
        function lbPeriodLabel() {
            if (lbHas(LB_ROLLING, lbPeriod)) return {label: LB_ROLLING[lbPeriod], dates: ''};
            return {label: LB_CALENDAR[lbPeriod] || 'Custom', dates: lbRangeText(lbRangeFor(lbPeriod))};
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
        function lbQuery() {
            const accId = typeof selectedAccountId !== 'undefined' ? selectedAccountId : 'all';
            // Rank strictly inside the active mode: take the type from the selected
            // option (data-type) and fall back to the page mode itself.
            const accSel = document.getElementById('account-selector');
            const accType = (accSel && accSel.selectedOptions[0] && accSel.selectedOptions[0].dataset.type)
                || ((currentMode === 'real' || currentMode === 'live') ? 'live' : 'demo');
            const query = `account_id=${encodeURIComponent(accId)}&account_type=${accType}`;
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
                    renderLeaderboard(data);
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
            const row = colspan => `<tr><td colspan="${colspan}" class="empty-state">Could not load the leaderboard, retrying…</td></tr>`;
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
            if (bot.rank === 1) return '<span class="rank-badge-1">🥇 1</span>';
            if (bot.rank === 2) return '<span class="rank-badge-2">🥈 2</span>';
            if (bot.rank === 3) return '<span class="rank-badge-3">🥉 3</span>';
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
                return `<span class="font-mono font-bold pnl-negative">0.0%</span><div class="td-dim" style="font-size:0.65rem;">0W / ${bot.total_losses}L</div>`;
            }
            const color = bot.win_rate >= 60 ? 'var(--profit)' : (bot.win_rate >= 40 ? '#fbbf24' : 'var(--loss)');
            return `<span class="font-mono font-bold" style="color: ${color};">${bot.win_rate.toFixed(1)}%</span><div class="td-dim" style="font-size:0.65rem;">${bot.total_wins}W / ${bot.total_losses}L</div>`;
        }

        function lbProfitFactorCell(bot) {
            if (bot.total_trades === 0) return '<span class="td-dim">--</span>';
            if (bot.profit_factor === null) return '<span class="font-mono pnl-positive" title="No losing trades yet">∞</span>';
            if (bot.profit_factor === 0) return '<span class="font-mono pnl-negative" title="No winning trades">0.00</span>';
            return `<span class="font-mono">${bot.profit_factor.toFixed(2)}</span>`;
        }

        function lbTradesCell(bot) {
            const full = (lbData && lbData.full_sample_trades) || 10;
            const small = bot.total_trades > 0 && bot.total_trades < full;
            return `<td class="font-mono">${bot.total_trades}${small
                ? `<div class="td-dim" style="font-size:0.65rem;" title="Fewer than ${full} closed trades: the score is pulled toward 50 until the sample is big enough">small n</div>`
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
            const unit = bot.basis === 'risk' ? 'P&amp;L per lot per stop pip' : 'P&amp;L per lot';
            const title = `Net ${bot.net_units.toFixed(2)} · Max DD ${bot.max_dd_units.toFixed(2)} (${unit})`;
            let cell;
            if (bot.return_dd === null) {
                cell = bot.net_units > 0
                    ? `<span class="font-mono pnl-positive" title="No drawdown yet · ${title}">∞</span>`
                    : `<span class="font-mono td-dim" title="${title}">0.00</span>`;
            } else {
                const cls = bot.return_dd > 0 ? 'pnl-positive' : (bot.return_dd < 0 ? 'pnl-negative' : 'td-dim');
                cell = `<span class="font-mono ${cls}" title="${title}">${bot.return_dd.toFixed(2)}</span>`;
            }
            if (bot.basis === 'lot') {
                cell += '<div class="td-dim" style="font-size:0.65rem;" title="Some trades have no stop distance on record, so every trade is taken per lot instead">per lot</div>';
            }
            return cell;
        }

        function lbEmptyRow(colspan) {
            const msg = lbPeriod === 'all' ? 'No bot trading history recorded yet' : 'No bot activity in this period';
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
                topPerfEl.textContent = top ? `${top.bot_name} (${top.composite_score}/100)` : 'N/A';
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
                            : bot.payoff_ratio === null ? '<span class="font-mono pnl-positive" title="No losing trades yet">∞</span>'
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
            lbDateError.textContent = reversed ? 'The first day is after the last day' : '';
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
                btn.title = `${lbShortDay(range.from, true)} – ${lbShortDay(range.to, true)}, Vietnam time`;
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
