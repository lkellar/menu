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