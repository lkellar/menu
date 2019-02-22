function triggerDarkMode(on) {
    if (on) {
        localStorage.setItem('darkmode', 'true');
    } else {
        localStorage.setItem('darkmode', 'false');
    }
    document.body.classList.toggle('darkmode');
}

function toggle() {
    const darkValue = localStorage.getItem('darkmode');
    if (darkValue === 'true') {
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
    const darkValue = localStorage.getItem('darkmode');
    const mql = window.matchMedia('(prefers-color-scheme: dark)');
    mql.addListener(darkTest);
    if (darkValue === 'true' || mql.matches) {
        triggerDarkMode(true);
    }
}

init();