(function () { // Оборачиваем в IIFE для изоляции области видимости

    const THEME_KEY = 'theme';
    const DARK_THEME_VALUE = 'dark';
    const LIGHT_THEME_VALUE = 'light';
    const NO_TRANSITION_CLASS = 'no-theme-transition-on-load';

    const htmlElement = document.documentElement;
    const themeToggleButton = document.getElementById('theme-toggle-btn');
    const themeIcon = document.getElementById('theme-icon'); // Предполагаем, что есть элемент для иконки

    function applyTheme(theme) {
        htmlElement.setAttribute('data-bs-theme', theme);
        if (themeIcon) {
            updateThemeIcon(theme);
        }
    }

    function updateThemeIcon(theme) {
        if (!themeIcon) return;
        if (theme === DARK_THEME_VALUE) {
            themeIcon.innerHTML = '<i class="bi bi-sun-fill"></i>'; // Показываем солнце, значит текущая тема темная
        } else {
            themeIcon.innerHTML = '<i class="bi bi-moon-stars-fill"></i>'; // Показываем луну, значит текущая тема светлая
        }
    }

    function getPreferredTheme() {
        const storedTheme = localStorage.getItem(THEME_KEY);
        if (storedTheme) {
            return storedTheme;
        }
        // Если в localStorage нет, используем системные настройки
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? DARK_THEME_VALUE : LIGHT_THEME_VALUE;
    }

    // --- Инициализация темы при загрузке скрипта ---
    // Этот блок может дублировать инлайн-скрипт в <head>, но инлайн-скрипт важнее для предотвращения мерцания.
    // Этот блок здесь больше для установки иконки и как резервный.
    const initialTheme = getPreferredTheme();
    applyTheme(initialTheme); // Применяем тему (атрибут) и обновляем иконку

    // --- Обработчик для кнопки переключения ---
    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', () => {
            // Удаляем класс, который отключал анимацию при загрузке, если он еще есть
            // (хотя он должен удаляться другим скриптом по DOMContentLoaded)
            if (htmlElement.classList.contains(NO_TRANSITION_CLASS)) {
                htmlElement.classList.remove(NO_TRANSITION_CLASS);
            }

            let currentTheme = htmlElement.getAttribute('data-bs-theme');
            // Если атрибута нет, берем из localStorage или системных (на случай, если инлайн-скрипт не сработал)
            if (!currentTheme) {
                currentTheme = getPreferredTheme();
            }

            const newTheme = currentTheme === DARK_THEME_VALUE ? LIGHT_THEME_VALUE : DARK_THEME_VALUE;
            localStorage.setItem(THEME_KEY, newTheme);
            applyTheme(newTheme);
        });
    }

    // --- Удаление класса no-transition после загрузки ---
    // Этот обработчик гарантирует, что анимации будут включены для последующих переключений темы.
    window.addEventListener('DOMContentLoaded', () => {
        // Небольшая задержка, чтобы убедиться, что все начальные стили применились без анимации
        setTimeout(() => {
            if (htmlElement.classList.contains(NO_TRANSITION_CLASS)) {
                htmlElement.classList.remove(NO_TRANSITION_CLASS);
            }
        }, 0);
    });

})();