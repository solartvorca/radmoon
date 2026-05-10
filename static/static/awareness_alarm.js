// Будильник осознавания для всех страниц
function playAwarenessSound() {
    // Можно заменить на свой звук
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    o.type = 'sine';
    o.frequency.value = 660;
    g.gain.value = 0.1;
    o.connect(g);
    g.connect(ctx.destination);
    o.start();
    setTimeout(() => { o.stop(); ctx.close(); }, 700);
}

function showNotification() {
    if (Notification.permission === 'granted') {
        new Notification('Будильник осознавания', {
            body: 'Вспомни, что осознаёт этот момент. Ты — не объект внимания, а источник.',
        });
    }
}

function startAwarenessAlarm(intervalMin) {
    if (window.awarenessAlarmTimer) clearInterval(window.awarenessAlarmTimer);
    window.awarenessAlarmTimer = setInterval(() => {
        playAwarenessSound();
        showNotification();
        alert('Будильник осознавания!\n\nВспомни, что осознаёт этот момент. Ты — не объект внимания, а источник.');
    }, intervalMin * 60 * 1000);
}

function stopAwarenessAlarm() {
    if (window.awarenessAlarmTimer) clearInterval(window.awarenessAlarmTimer);
}

document.addEventListener('DOMContentLoaded', function() {
    const alarmToggle = document.getElementById('alarm-toggle');
    const alarmSlider = document.getElementById('alarm-slider');
    const alarmInterval = document.getElementById('alarm-interval');

    // Запросить разрешение на уведомления
    if (Notification && Notification.permission !== 'granted') {
        Notification.requestPermission();
    }

    let interval = parseInt(alarmSlider.value);
    alarmInterval.textContent = interval;
    if (alarmToggle.checked) startAwarenessAlarm(interval);

    alarmToggle.addEventListener('change', function() {
        if (alarmToggle.checked) {
            startAwarenessAlarm(interval);
        } else {
            stopAwarenessAlarm();
        }
    });
    alarmSlider.addEventListener('input', function() {
        interval = parseInt(alarmSlider.value);
        alarmInterval.textContent = interval;
        if (alarmToggle.checked) {
            startAwarenessAlarm(interval);
        }
    });
});