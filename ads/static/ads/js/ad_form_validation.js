document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('adForm');
    if (!form) return;

    const formElements = Array.from(form.querySelectorAll('.form-floating > input:not([type="hidden"]), .form-floating > select, .form-floating > textarea'));

    formElements.forEach(function (el) {
        if (el.tagName.toLowerCase() === 'select') {
            if (!el.classList.contains('form-select')) el.classList.add('form-select');
        } else {
            if (!el.classList.contains('form-control')) el.classList.add('form-control');
        }

        if (el.tagName.toLowerCase() !== 'select' && el.value === '' && !el.hasAttribute('placeholder') && (['text', 'email', 'password', 'url', 'number'].includes(el.type) || el.tagName.toLowerCase() === 'textarea')) {
            el.setAttribute('placeholder', ' ');
        }

        const fieldContainer = el.closest('.field-container-' + el.name); // Используем уникальный класс
        if (!fieldContainer) return; // Добавил проверку

        const djangoErrorDiv = fieldContainer.querySelector('.django-error');
        const jsErrorDiv = fieldContainer.querySelector('.custom-error-message');

        const eventType = (el.tagName.toLowerCase() === 'select' || el.type === 'checkbox' || el.type === 'radio') ? 'change' : 'input';

        el.addEventListener(eventType, function () {
            if (djangoErrorDiv && djangoErrorDiv.offsetParent !== null && djangoErrorDiv.textContent.toLowerCase().includes('this field is required')) {
                djangoErrorDiv.style.display = 'none';
            }
            if (jsErrorDiv && jsErrorDiv.offsetParent !== null && jsErrorDiv.textContent.includes('Это поле обязательно для заполнения')) {
                hideJsError(jsErrorDiv);
            }
            updateAdFieldOverallValidity(el);
        });

        el.addEventListener('blur', function () {
            const isRequired = el.hasAttribute('required') || el.required;
            let isEmpty;
            if (el.tagName.toLowerCase() === 'select') {
                isEmpty = el.value === '';
            } else {
                isEmpty = el.value.trim() === '';
            }

            if (isEmpty && isRequired) {
                showJsError(jsErrorDiv, 'Это поле обязательно для заполнения.');
                el.classList.add('is-invalid'); el.classList.remove('is-valid');
                if (djangoErrorDiv) djangoErrorDiv.style.display = 'none';
            } else {
                if (jsErrorDiv && jsErrorDiv.textContent.includes('Это поле обязательно для заполнения')) {
                    hideJsError(jsErrorDiv);
                }
            }
            updateAdFieldOverallValidity(el);
        });

        if (djangoErrorDiv && djangoErrorDiv.offsetParent !== null) {
            el.classList.add('is-invalid');
        }
    });

    function updateAdFieldOverallValidity(fieldElement) {
        const fieldContainer = fieldElement.closest('.field-container-' + fieldElement.name);
        if (!fieldContainer) return;

        const djangoErrorDiv = fieldContainer.querySelector('.django-error');
        const jsErrorDiv = fieldContainer.querySelector('.custom-error-message');
        const isRequired = fieldElement.hasAttribute('required') || fieldElement.required;

        let isFieldValidByJs = true; // По умолчанию считаем поле валидным по JS
        const fieldValue = fieldElement.value; // Не тримим для select, для text тримим при проверке

        if (fieldElement.name === 'image_url' && fieldValue.trim() !== '') {
            try {
                new URL(fieldValue); // Попытка создать URL
                if (jsErrorDiv && jsErrorDiv.textContent.includes('Некорректный формат URL')) hideJsError(jsErrorDiv);
            } catch (_) {
                isFieldValidByJs = false;
                showJsError(jsErrorDiv, 'Некорректный формат URL.');
            }
        } else if (fieldElement.name === 'image_url' && fieldValue.trim() === '') {
            // Если image_url не обязательный и пустой, он валиден (убираем ошибку формата)
            if (jsErrorDiv && jsErrorDiv.textContent.includes('Некорректный формат URL')) hideJsError(jsErrorDiv);
        }

        const djangoErrorIsVisible = djangoErrorDiv && djangoErrorDiv.offsetParent !== null;
        const jsSpecificErrorIsVisible = jsErrorDiv && jsErrorDiv.offsetParent !== null && !jsErrorDiv.textContent.includes('Это поле обязательно для заполнения');
        const jsRequiredErrorIsVisible = jsErrorDiv && jsErrorDiv.offsetParent !== null && jsErrorDiv.textContent.includes('Это поле обязательно для заполнения');

        let currentValueIsEmpty;
        if (fieldElement.tagName.toLowerCase() === 'select') {
            currentValueIsEmpty = fieldValue === '';
        } else {
            currentValueIsEmpty = fieldValue.trim() === '';
        }

        if (currentValueIsEmpty && isRequired) {
            fieldElement.classList.add('is-invalid');
            fieldElement.classList.remove('is-valid');
        } else if (isFieldValidByJs && !djangoErrorIsVisible && !jsSpecificErrorIsVisible && !jsRequiredErrorIsVisible) {
            fieldElement.classList.remove('is-invalid');
            if (!currentValueIsEmpty || (!isRequired && currentValueIsEmpty)) {
                fieldElement.classList.add('is-valid');
            } else {
                fieldElement.classList.remove('is-valid');
            }
        } else {
            fieldElement.classList.add('is-invalid');
            fieldElement.classList.remove('is-valid');
        }
    }

    function showJsError(errorDiv, message) { if (!errorDiv) return; errorDiv.textContent = message; errorDiv.style.display = 'block'; }
    function hideJsError(errorDiv) { if (!errorDiv) return; errorDiv.textContent = ''; errorDiv.style.display = 'none'; }

});