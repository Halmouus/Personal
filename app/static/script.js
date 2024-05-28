function displayDateTime() {
    var now = new Date();
    var dateTimeString = now.toLocaleString();
    document.getElementById('currentDateTime').innerHTML = dateTimeString;
}
setInterval(displayDateTime, 1000);

function toggleDarkMode() {
    var darkModeEnabled = document.body.classList.toggle('dark-mode');
    fetch('/toggle-dark-mode', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ dark_mode: darkModeEnabled })
    }).then(response => {
        if (response.ok) {
            localStorage.setItem('darkMode', darkModeEnabled);
        }
    });
}

window.onload = function() {
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
        document.getElementById('darkModeToggle').checked = true;
    }
};

document.addEventListener('DOMContentLoaded', function() {
    const socket = io();

    socket.on('new_notification', function(data) {
        if (data.recipient_id === '{{ current_user.id }}') {
            alert(`You received ${data.amount} tokens from ${data.sender}`);
        }
    });

    // Fetch offline notifications
    fetch('/notifications')
        .then(response => response.json())
        .then(notifications => {
            notifications.forEach(notification => {
                alert(`You received ${notification.amount} tokens from ${notification.sender} at ${notification.timestamp}`);
            });
        });

    const links = document.querySelectorAll('nav a');
    links.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            const target = event.target.getAttribute('href');
            const currentPage = document.querySelector('.page');
            currentPage.classList.add('page-exit-active');

            setTimeout(() => {
                window.location.href = target;
            }, 500);
        });
    });

    window.addEventListener('load', function() {
        const newPage = document.querySelector('.page');
        newPage.classList.add('page-enter');
        setTimeout(() => {
            newPage.classList.remove('page-enter');
            newPage.classList add('page-enter-active');
        }, 0);
    });
});
