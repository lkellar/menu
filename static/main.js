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
    document.addEventListener('touchstart', handleTouchStart, false);
    document.addEventListener('touchmove', handleTouchMove, false);
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
            const after = document.getElementsByClassName('after')[0];
            if (after) {
            after.classList.add('visible');
            }
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
            const before = beforeList[beforeList.length - 1]
            if (before) {
                before.classList.add('visible');
            }
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

function handleTouchStart(evt) {
    xDown = evt.touches[0].clientX;
    yDown = evt.touches[0].clientY;
}

function handleTouchMove(evt) {
    if ( ! xDown || ! yDown ) {
        return;
    }

    var xUp = evt.touches[0].clientX;
    var yUp = evt.touches[0].clientY;

    var xDiff = xDown - xUp;
    var yDiff = yDown - yUp;

    if ( Math.abs( xDiff ) > Math.abs( yDiff ) ) {/*most significant*/
        if (Math.abs(xDiff) > 10) {
            if (xDiff > 0) {
                change(true)
            } else {
                change(false)
            }
        }
    }
    /* reset values */
    xDown = null;
    yDown = null;
}

function keyPress(oToCheckField, oKeyEvent) {
        if (oKeyEvent.key === 'ArrowRight' || oKeyEvent.key === 'd') {
            change(true)
        } else if (oKeyEvent.key === 'ArrowLeft' || oKeyEvent.key === 'a') {
            change(false)
        }
    }

let xDown = null;
let yDown = null;
init();