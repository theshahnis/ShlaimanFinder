document.addEventListener('DOMContentLoaded', function () {
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function () {
            toggleDarkMode();
        });
    }

    // Apply general dark mode based on saved preference
    if (localStorage.getItem('darkMode') === 'enabled') {
        enableDarkMode();
    } else {
        disableDarkMode();
    }

    // Highlight the current page's navigation button
    const navButtons = document.querySelectorAll('.nav-button');
    const currentPath = window.location.pathname;

    navButtons.forEach(button => {
        const url = button.querySelector('a').getAttribute('href');
        if (currentPath === url) {
            button.classList.add('selected');
        } else if (currentPath.startsWith(url) && !currentPath.includes('/show/my-shows')) {
            button.classList.add('selected');
        }
    });

    // Explicitly handle the "My Shows" page
    const myShowsButton = document.querySelector('.nav-button a[href="/show/my-shows"]');
    if (currentPath === '/show/my-shows' && myShowsButton) {
        myShowsButton.parentElement.classList.add('selected');
    }
});

function toggleDarkMode() {
    const darkModeStylesheet = document.getElementById('dark-mode-stylesheet');
    if (darkModeStylesheet.disabled) {
        enableDarkMode();
    } else {
        disableDarkMode();
    }
}

function enableDarkMode() {
    const darkModeStylesheet = document.getElementById('dark-mode-stylesheet');
    darkModeStylesheet.disabled = false;
    localStorage.setItem('darkMode', 'enabled');
}

function disableDarkMode() {
    const darkModeStylesheet = document.getElementById('dark-mode-stylesheet');
    darkModeStylesheet.disabled = true;
    localStorage.setItem('darkMode', 'disabled');
}