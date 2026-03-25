const formatTime = seconds =>
    `${String(Math.floor(seconds / 60)).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`;

// chrono avec warning *************************************************************************************************
const start_chrono = (areaTime, areaWarning, countdownTime = 120) => {
    let elapsed = 0;
    areaTime.innerHTML = formatTime(elapsed);

    const intervalId = setInterval(() => {
        elapsed += 1;
        areaTime.innerHTML = formatTime(elapsed);

        if (elapsed === countdownTime) {
            start_warning(areaWarning);
        }
    }, 1000);

    return intervalId;
};

const start_warning = (areaWarning) => {
    let visible = true;
    return setInterval(() => {
        areaWarning.style.visibility = visible ? "hidden" : "visible";
        visible = !visible;
    }, 1000);
};

// Compte à rebours ****************************************************************************************************
const stop_countdown = (intervalId, area, onEnd) => {
    clearInterval(intervalId);
    area.innerHTML = formatTime(0);
    if (typeof onEnd === 'function') onEnd();
};

const start_timer = (area, countdown, onEnd = null) => {
    let current = countdown;
    area.innerHTML = formatTime(current);
    const intervalId = setInterval(() => {
        current -= 1;
        if (current < 0) {
            stop_countdown(intervalId, area, onEnd);
        } else {
            area.innerHTML = formatTime(current);
        }
    }, 1000);
    return intervalId;
};
