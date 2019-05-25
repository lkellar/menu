function changeWeek(add) {
    let url = new URL(window.location.href);
    let weeks = Number(url.searchParams.get('weeks'));
    if (add) {
        weeks += 1
    } else {
        weeks -= 1;
    }
    url.searchParams.set('weeks', weeks.toString());
    console.log(url);
    window.location.href = url.toString();
}

function keyDown(oToCheckField, oKeyEvent) {
    if (oKeyEvent.key === 'ArrowRight' || oKeyEvent.key === 'd') {
        changeWeek(true)
    } else if (oKeyEvent.key === 'ArrowLeft' || oKeyEvent.key === 'a') {
        changeWeek(false)
    }
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
                changeWeek(true)
            } else {
                changeWeek(false)
            }
        }
    }
    /* reset values */
    xDown = null;
    yDown = null;
}

document.addEventListener('touchstart', handleTouchStart, false);
document.addEventListener('touchmove', handleTouchMove, false);

let xDown = null;
let yDown = null;