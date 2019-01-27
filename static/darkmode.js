function setCookie(name, value) {
    document.cookie = name + '=' + value  + `; path=/; domain=${topLevelDomain()}`;
}

function topLevelDomain() {
    const parts = location.hostname.split('.');
    parts.shift();
    return parts.join('.');
}

function getCookie(c_name) {
    let c_start;
    let c_end;
    if (document.cookie.length > 0) {
        c_start = document.cookie.indexOf(c_name + '=');
        if (c_start !== -1) {
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(';', c_start);
            if (c_end === -1) {
                c_end = document.cookie.length;
            }
            return unescape(document.cookie.substring(c_start, c_end));
        }
    }
    return null;
}

function triggerDarkMode(on) {
    if (on) {
        setCookie('darkmode', 'true');
    } else {
        setCookie('darkmode', 'false');
    }
    document.body.classList.toggle('darkmode');
}

function toggle() {
    const cookie = getCookie('darkmode');
    if (cookie === 'true') {
      triggerDarkMode(false);
    } else {
        triggerDarkMode(true);
    }
}

function darkTest(e) {
    if (e.matches) {
        triggerDarkMode(true);
    } else {
        triggerDarkMode(false);
    }
}

function init() {
    const cookie = getCookie('darkmode');
    const mql = window.matchMedia('(prefers-color-scheme: dark)');
    mql.addListener(darkTest);
    if (cookie === 'true' || mql.matches) {
        triggerDarkMode(true);
    }
}

init();