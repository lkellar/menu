function triggerDarkMode(on, set=true) {
    if (set) {
        localStorage.setItem('darkmode',  on.toString())
    }
    if (document.body.classList.contains('darkmode')) {
        document.body.classList.remove('darkmode');
    } else {
        document.body.classList.add('darkmode');
    }
}

function toggle() {
    if (document.body.classList.contains('darkmode')) {
      triggerDarkMode(false);
    } else {
        triggerDarkMode(true);
    }
}

function darkTest(e) {
    // If the user already has a pref set, we don't want to adjust the color based on system pref
    if (!localStorage.getItem('darkmode')) {
        if (e.matches) {
            triggerDarkMode(true, false);
        } else {
            triggerDarkMode(false, false);
        }
    }
}

function init() {
    const darkPref = localStorage.getItem('darkmode');
    const mql = window.matchMedia('(prefers-color-scheme: dark)');
    mql.addListener(darkTest);

    // Some of the things in the statements below are redundant, but I really want to make sure someone's preference
    // doesn't get messed up.
    if (darkPref) {
        if (darkPref === 'true') {
            triggerDarkMode(true);
        } else if (darkPref === 'false') {
            triggerDarkMode(false);
        }
    } else {
        if (mql.matches) {
            triggerDarkMode(true, false);
        } else {
            triggerDarkMode(false, false);
        }
    }
}

init();