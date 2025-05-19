// static/js/auth_forms_init.js
function initializeBootstrapFloatingLabels(formId) {
    const form = document.getElementById(formId);
    if (!form) return;

    const formElements = form.querySelectorAll('.form-floating > input:not([type="hidden"]), .form-floating > select, .form-floating > textarea');

    formElements.forEach(function (el) {
        // Добавляем класс form-control или form-select
        if (el.tagName.toLowerCase() === 'select') {
            if (!el.classList.contains('form-select')) {
                el.classList.add('form-select');
            }
        } else {
            if (!el.classList.contains('form-control')) {
                el.classList.add('form-control');
            }
        }

        // Добавляем placeholder для работы form-floating, если поле пустое и у него нет placeholder
        if (el.tagName.toLowerCase() !== 'select' && el.value === '' && !el.hasAttribute('placeholder') &&
            (['text', 'email', 'password', 'url', 'number'].includes(el.type) || el.tagName.toLowerCase() === 'textarea')) {
            el.setAttribute('placeholder', ' ');
        }

        // Добавление is-invalid на основе серверных ошибок Django
        // Это полезно, если JS для "живой" валидации более сложный и находится в другом файле
        const fieldContainer = el.closest('.field-container'); // Предполагаем, что есть .field-container
        if (fieldContainer) {
            const djangoErrorDiv = fieldContainer.querySelector('.django-error.invalid-feedback.d-block');
            if (djangoErrorDiv && djangoErrorDiv.offsetParent !== null) { // offsetParent для проверки видимости
                el.classList.add('is-invalid');
            }
        }
    });
}

// Вызываем для формы логина
document.addEventListener('DOMContentLoaded', function () {
    initializeBootstrapFloatingLabels('loginForm');
    // Если эта же функция будет использоваться для signupForm, то:
    // initializeBootstrapFloatingLabels('signupForm');
    // Или вызывать ее на конкретных страницах.
});