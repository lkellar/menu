before = document.getElementsByClassName('before');
lastBefore = before[before.length - 1];
if (lastBefore) {
    lastBefore.classList.add('visible');
}

after = document.getElementsByClassName('after');
firstAfter = after[after.length + 1];
if (firstAfter) {
    firstAfter.classList.add('visible');
}