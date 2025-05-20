// Функция для обработки ошибок загрузки основного изображения объявления
function handleImageError(imageElement, placeholderId) {
    if (imageElement) {
        // Скрываем "сломанное" изображение
        imageElement.style.display = 'none';
    }
    const placeholder = document.getElementById(placeholderId);
    if (placeholder) {
        // Показываем плейсхолдер ошибки
        placeholder.classList.remove('initially-hidden'); // Удаляем класс, который его скрывал
    }
}

// Код, который у вас уже был, для стилизации формы предложения
document.addEventListener('DOMContentLoaded', function () {
    const proposalForm = document.querySelector('.proposal-section form');
    if (proposalForm) {
        const formElements = proposalForm.querySelectorAll(
            'select, textarea, input:not([type="hidden"]):not([type="checkbox"]):not([type="radio"]):not([type="file"]):not([type="submit"]):not([type="reset"]):not([type="button"])'
        );

        formElements.forEach(function (el) {
            const tagName = el.tagName.toLowerCase();
            if (tagName === 'select') {
                if (!el.classList.contains('form-select')) {
                    el.classList.add('form-select');
                }
            } else { // textarea, input (text, email, url, etc.)
                if (!el.classList.contains('form-control')) {
                    el.classList.add('form-control');
                }
            }

            // Для form-floating
            // Проверяем, является ли родитель элементом .form-floating
            const parentIsFloating = el.parentElement && el.parentElement.classList.contains('form-floating');
            if (parentIsFloating && el.value === '' && !el.hasAttribute('placeholder')) {
                // Не добавляем placeholder для select, т.к. у него empty_label из Django
                if (tagName !== 'select') {
                    el.setAttribute('placeholder', ' '); // Пробел как плейсхолдер для активации floating label
                }
            }
        });
    }
});