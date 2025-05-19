document.addEventListener('DOMContentLoaded', function () {
    // Применяем классы Bootstrap к полям формы предложения обмена, если она есть
    const proposalForm = document.querySelector('.proposal-section form');
    if (proposalForm) {
        const formElements = proposalForm.querySelectorAll('select, textarea, input:not([type="hidden"])');
        formElements.forEach(function (el) {
            if (el.tagName.toLowerCase() === 'select') {
                if (!el.classList.contains('form-select')) el.classList.add('form-select');
            } else {
                if (!el.classList.contains('form-control')) el.classList.add('form-control');
            }
            // Для form-floating (если плейсхолдер не задан Django)
            if (el.value === '' && !el.hasAttribute('placeholder') && (el.tagName.toLowerCase() === 'textarea' || ['text', 'url', 'email', 'number'].includes(el.type))) {
                el.setAttribute('placeholder', ' ');
            }
        });
    }
});