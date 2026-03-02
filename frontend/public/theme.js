(function () {
    const theme = localStorage.getItem('theme') || 'dark';
    if (theme === 'light') {
        document.documentElement.classList.add('light-mode');
    }

    window.toggleTheme = function () {
        const isLight = document.documentElement.classList.toggle('light-mode');
        const newTheme = isLight ? 'light' : 'dark';
        localStorage.setItem('theme', newTheme);

        // Dispatch custom event for charts or other listeners
        window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: newTheme } }));
    };
})();
