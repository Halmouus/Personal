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
    const userId = document.body.getAttribute('data-user-id');
    const socket = io();
    let recentNotifications = new Set(); // To track recent notifications

    socket.on('new_notification', function(data) {
        if (data.recipient_id === userId && !recentNotifications.has(data.id)) {
            recentNotifications.add(data.id);
            alert(`Yoo! ${data.sender} has sent you ${data.amount} habibas for absolutely no reason! Spend them wisely ;) `);
        }
    });

    // Fetch notifications after a delay to ensure all socket messages are processed
    setTimeout(() => {
        fetch('/notifications')
            .then(response => response.json())
            .then(notifications => {
                notifications.forEach(notification => {
                    if (!recentNotifications.has(notification.id)) {
                        alert(`You received ${notification.amount} tokens from ${notification.sender} at ${notification.timestamp}`);
                    }
                });
            });
    }, 5000);

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
            newPage.classList.add('page-enter-active');
        }, 0);
    });

    // Improved Dropdown toggle functionality
    const dropdownToggles = document.querySelectorAll('.nav-item.dropdown');

    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent default behavior to manage manually
            const menu = this.querySelector('.dropdown-menu');
            const isVisible = menu.style.display === 'block';

            // Close all open menus first
            document.querySelectorAll('.dropdown-menu').forEach(dm => {
                dm.style.display = 'none'; // Close other menus
            });

            // Toggle this menu's visibility based on current state
            menu.style.display = isVisible ? 'none' : 'block';
        });
    });

    // Clicking outside of the dropdown will close it
    document.addEventListener('click', function(event) {
        if (!event.target.closest('.nav-item.dropdown')) {
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                menu.style.display = 'none';
            });
        }
    });
});
