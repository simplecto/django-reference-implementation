// Check and apply dark mode preference from local storage
function applyDarkModePreference() {
    // get the dark mode preference value from localStorage. default to light if no value is found
    const darkModePreference = localStorage.getItem('dark-mode') || 'light';

    if (darkModePreference === 'dark') {
        document.documentElement.classList.add('dark');
    } else {
        document.documentElement.classList.remove('dark');
    }
}

// Toggle dark mode and update local storage
function toggleDarkMode() {
    const isDark = document.documentElement.classList.contains('dark');

    if (isDark) {
        document.documentElement.classList.remove('dark');
        localStorage.setItem('dark-mode', 'light');
    } else {
        document.documentElement.classList.add('dark');
        localStorage.setItem('dark-mode', 'dark');
    }
}

// Apply dark mode preference on page load
window.addEventListener('load', function() {
    applyDarkModePreference();
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    if (darkModeToggle) {
        darkModeToggle.onclick = toggleDarkMode;
    }
});
