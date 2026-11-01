/* In-page confirmation for actions that touch a bot or a position (the <dialog> in templates/dashboard.html).
 *
 * askConfirm({title, body, ok, live, typeWord}) resolves true when the user confirms. A real-money action (live)
 * shows the "Tiền thật" label and, when typeWord is given, keeps the button disabled until that word is typed: a
 * second look that a click on the wrong row cannot skip. confirmWordFor() is pure so tests can run it in node. */

/** The pair a real-money confirmation asks for, upper case as cTrader writes it: the given symbol, else the token of
 *  the bot name that reads as a pair (two currency codes: usdjpy, xauusd, btcusd) or an index (us500, jp225), so
 *  cbot-live-live-gbpjpy-fix-gotobi and cbot-demo-usdjpy-fix-gotobi both give the pair. Else the whole name. */
function confirmWordFor(botName, symbol) {
    const CONFIRM_CCY = 'usd|eur|jpy|gbp|aud|nzd|cad|chf|cnh|sgd|hkd|nok|sek|mxn|zar|try|pln|xau|xag|xpt|xpd|btc|eth|xti|xbr|xng';
    if (symbol) return String(symbol).toUpperCase();
    const pair = new RegExp(`^(${CONFIRM_CCY})(${CONFIRM_CCY})$`);
    const index = /^[a-z]{2,4}\d{2,4}$/;
    const hit = String(botName || '').toLowerCase().split(/[-_]/).find(t => pair.test(t) || index.test(t));
    return hit ? hit.toUpperCase() : String(botName || '');
}

function askConfirm(opts) {
    const dialog = document.getElementById('confirm-dialog');
    const o = opts || {};
    if (!dialog || typeof dialog.showModal !== 'function') return Promise.resolve(false);
    const el = id => document.getElementById(id);
    const okBtn = el('confirm-ok'), input = el('confirm-type-input'), typeWrap = el('confirm-type-wrap');
    el('confirm-title').textContent = o.title || '';
    el('confirm-body').textContent = o.body || '';
    el('confirm-live').hidden = !o.live;
    dialog.classList.toggle('confirm-dialog--live', !!o.live);
    okBtn.textContent = o.ok || 'Đồng ý';
    const word = o.live && o.typeWord ? String(o.typeWord) : '';
    typeWrap.hidden = !word;
    input.value = '';
    el('confirm-type-label').textContent = word ? `Gõ ${word} để xác nhận` : '';
    const check = () => { okBtn.disabled = !!word && input.value.trim().toUpperCase() !== word.toUpperCase(); };
    check();
    input.oninput = check;
    const back = document.activeElement;   // focus goes back to the control that asked, if it is still there
    return new Promise(resolve => {
        dialog.addEventListener('close', () => {
            if (back && back.isConnected && typeof back.focus === 'function') back.focus();
            resolve(dialog.returnValue === 'ok' && !okBtn.disabled);
        }, {once: true});
        dialog.returnValue = '';
        dialog.showModal();
        (word ? input : el('confirm-cancel')).focus();
    });
}
