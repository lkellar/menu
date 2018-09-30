function init() {
    const before = document.getElementsByClassName('before');
    const lastBefore = before[before.length - 1];
    if (lastBefore) {
        lastBefore.classList.add('visible');
    }

    const current = document.getElementsByClassName('current')[0];
    if (current) {
        current.classList.add('visible');
    }

    const after = document.getElementsByClassName('after')[0];
    if (after) {
        after.classList.add('visible');
    }
}

function change(left) {
    if (left) {
        if (document.getElementsByClassName('after').length > 0) {
            const before = document.getElementsByClassName('before visible')[0];
            if (before) {
                before.classList.remove('visible');
            }
            document.getElementsByClassName('current')[0].classList.replace('current', 'before');
            document.getElementsByClassName('after visible')[0].classList.replace('after', 'current');
            document.getElementsByClassName('after')[0].classList.add('visible');
        }  else {
            changeWeek(true);
        }
    } else {
        if (document.getElementsByClassName('before').length > 0) {
            const after = document.getElementsByClassName('after visible')[0];
            if (after) {
                after.classList.remove('visible');
            }
            document.getElementsByClassName('current')[0].classList.replace('current', 'after');
            document.getElementsByClassName('before visible')[0].classList.replace('before', 'current');
            const beforeList = document.getElementsByClassName('before');
            beforeList[beforeList.length - 1].classList.add('visible');
        }
        else {
            changeWeek(false);
        }
    }
}

function changeWeek(add) {
    let url = new URL(window.location.href);
    let weeks = Number(url.searchParams.get('weeks'));
    if (add) {
        weeks += 1
    } else {
        weeks -= 1;
    }
    url.searchParams.set('weeks', weeks.toString());
    if (add) {
        url.searchParams.set('entry', 'first');
    } else {
        url.searchParams.set('entry', 'last')
    }
    console.log(url);
    window.location.href = url.toString();

}

function keyPress(oToCheckField, oKeyEvent) {
        if (oKeyEvent.key === 'ArrowRight' || oKeyEvent.key === 'd') {
            change(true)
        } else if (oKeyEvent.key === 'ArrowLeft' || oKeyEvent.key === 'a') {
            change(false)
        }
    }

init();