// Check and apply dark mode preference from local storage
function applyDarkModePreference() {

    // get the dark mode preference value from localStorage. default to light if no value is found
    const darkModePreference = localStorage.getItem('dark-mode') || 'light';
    document.documentElement.setAttribute('data-bs-theme', darkModePreference);
}

// Toggle dark mode and update local storage
function toggleDarkMode() {
    const currentTheme = document.documentElement.getAttribute('data-bs-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    document.documentElement.setAttribute('data-bs-theme', newTheme);
    localStorage.setItem('dark-mode', newTheme === 'dark' ? 'dark' : 'light');
}

// Apply dark mode preference on page load
window.addEventListener('load', function() {
    applyDarkModePreference();
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    darkModeToggle.onclick = toggleDarkMode;
    console.log('loaded')
});
