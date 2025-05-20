; (function () {
    'use strict';

    const THEME_KEY = 'theme';
    const DARK_THEME_VALUE = 'dark';
    const LIGHT_THEME_VALUE = 'light';
    const NO_TRANSITION_CLASS = 'no-theme-transition-on-load';

    const ICONS = {
        light: '<i class="bi bi-moon-stars-fill"></i>', // Показана луна -> можно переключить на темную
        dark: '<i class="bi bi-sun-fill"></i>'         // Показано солнце -> можно переключить на светлую
    };

    const ARIA_LABELS = {
        light: 'Переключить на темную тему',
        dark: 'Переключить на светлую тему'
    };

    const htmlElement = document.documentElement;
    const themeToggleButton = document.getElementById('theme-toggle-btn');
    const themeIconElement = document.getElementById('theme-icon');

    // Флаг, чтобы гарантировать однократное выполнение пост-загрузочной логики
    let postLoadLogicExecuted = false;

    function updateButtonState(currentTheme) {
        if (themeIconElement) {
            // Иконка отражает, на какую тему МОЖНО переключиться
            // Если текущая темная, показываем иконку солнца (намек на светлую)
            // Если текущая светлая, показываем иконку луны (намек на темную)
            themeIconElement.innerHTML = (currentTheme === DARK_THEME_VALUE) ? ICONS.dark : ICONS.light;
        }
        if (themeToggleButton) {
            // Aria-label отражает действие, которое произойдет
            themeToggleButton.setAttribute('aria-label', (currentTheme === DARK_THEME_VALUE) ? ARIA_LABELS.dark : ARIA_LABELS.light);
        }
    }

    function applyTheme(newTheme) {
        htmlElement.setAttribute('data-bs-theme', newTheme);
        localStorage.setItem(THEME_KEY, newTheme);
        updateButtonState(newTheme); // Обновляем иконку и aria-label
    }

    function initializeUIFromExistingTheme() {
        if (!themeToggleButton && !themeIconElement) return; // Нечего обновлять

        let currentTheme = htmlElement.getAttribute('data-bs-theme');

        // Резервная логика: если inline-скрипт не установил data-bs-theme
        // (Это не должно происходить при нормальной работе)
        if (!currentTheme) {
            console.warn('Inline theme script did not set data-bs-theme. Initializing from theme_switcher.js');
            const storedTheme = localStorage.getItem(THEME_KEY);
            const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
            currentTheme = storedTheme || (prefersDark ? DARK_THEME_VALUE : LIGHT_THEME_VALUE);
            htmlElement.setAttribute('data-bs-theme', currentTheme); // Устанавливаем, если не было
        }
        updateButtonState(currentTheme);
    }

    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', () => {
            // NO_TRANSITION_CLASS должен быть уже удален к этому моменту
            // через postLoadSetup. Нет необходимости удалять его здесь снова.
            const currentTheme = htmlElement.getAttribute('data-bs-theme');
            const newTheme = (currentTheme === DARK_THEME_VALUE) ? LIGHT_THEME_VALUE : DARK_THEME_VALUE;
            applyTheme(newTheme);
        });
    }

    // Логика, выполняемая после того, как DOM готов и начальная тема (из inline-скрипта) применена
    function postLoadSetup() {
        if (postLoadLogicExecuted) return; // Выполняем только один раз

        initializeUIFromExistingTheme(); // Обновляем иконку/aria-label на основе темы, установленной inline-скриптом

        // Удаляем класс для отключения анимаций после того, как начальная тема применена
        // и браузер имел шанс отрисовать страницу.
        requestAnimationFrame(() => {
            if (htmlElement.classList.contains(NO_TRANSITION_CLASS)) {
                htmlElement.classList.remove(NO_TRANSITION_CLASS);
            }
        });
        postLoadLogicExecuted = true;
    }

    // Запуск пост-загрузочной логики
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', postLoadSetup);
    } else {
        // DOM уже загружен (например, скрипт без defer или async, или подключен в конце body)
        postLoadSetup();
    }

})();