/* Dashboard login (app/auth.py): once the session ends, the API answers 401 with X-Login-Required. Go back to the
 * login page, and return here after it, instead of leaving every panel on an error.
 *
 * Loaded without `defer`, before the dashboard scripts, so their fetch calls all go through this wrapper. */
(function () {
    const originalFetch = window.fetch.bind(window);
    let redirecting = false;
    window.fetch = async (...args) => {
        const res = await originalFetch(...args);
        if (res.status === 401 && res.headers.get('X-Login-Required') && !redirecting) {
            redirecting = true;
            location.href = '/login?next=' + encodeURIComponent(location.pathname + location.search + location.hash);
        }
        return res;
    };
})();
