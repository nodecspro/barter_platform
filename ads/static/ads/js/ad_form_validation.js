document.addEventListener('DOMContentLoaded', function () {
    // Form configuration constants
    const AD_FORM_ID = 'adForm';
    const FORM_ELEMENT_SELECTOR = '.form-floating > input:not([type="hidden"]), .form-floating > select, .form-floating > textarea';

    // CSS class names for form styling
    const CSS_CLASSES = {
        FORM_CONTROL: 'form-control',
        FORM_SELECT: 'form-select',
        IS_INVALID: 'is-invalid',
        IS_VALID: 'is-valid',
    };

    // Selector definitions for error messages
    const SELECTORS = {
        DJANGO_ERROR: '.django-error',
        JS_ERROR: '.custom-error-message',
    };

    // Validation error messages
    const ERROR_MESSAGES = {
        REQUIRED_FIELD: 'Это поле обязательно для заполнения.',
        INVALID_URL: 'Некорректный формат URL.',
    };

    // Input types that should have placeholders for floating labels
    const PLACEHOLDER_INPUT_TYPES = ['text', 'email', 'password', 'url', 'number'];
    const EMPTY_PLACEHOLDER = ' ';

    // Fields that should not receive valid styling
    const FIELDS_EXCLUDED_FROM_VALID_STYLING = ['image_url', 'category'];

    // Get the form element
    const form = document.getElementById(AD_FORM_ID);
    if (!form) {
        console.warn(`Form with ID "${AD_FORM_ID}" not found.`);
        return;
    }

    // Get all form elements
    const formElements = Array.from(form.querySelectorAll(FORM_ELEMENT_SELECTOR));

    // Check if an element is visible in the DOM
    function isElementVisible(element) {
        return element && element.offsetParent !== null && element.style.display !== 'none';
    }

    // Show JavaScript validation error
    function showJsError(errorDiv, message) {
        if (!errorDiv) return;
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }

    // Hide JavaScript validation error
    function hideJsError(errorDiv) {
        if (!errorDiv) return;
        errorDiv.textContent = '';
        errorDiv.style.display = 'none';
    }

    // Update field validation state considering both Django and JS errors
    function updateAdFieldOverallValidity(fieldElement, djangoErrorDiv, jsErrorDiv) {
        const isRequired = fieldElement.hasAttribute('required') || fieldElement.required;
        const fieldValue = fieldElement.value;
        const fieldName = fieldElement.name;
        const isSelect = fieldElement.tagName.toLowerCase() === 'select';
        const isEffectivelyEmpty = isSelect ? fieldValue === '' : fieldValue.trim() === '';

        let fieldIsValidByJsSpecificChecks = true;

        // Perform specific validations for certain fields
        if (fieldName === 'image_url') {
            if (!isEffectivelyEmpty) {
                try {
                    new URL(fieldValue);
                    if (jsErrorDiv && jsErrorDiv.textContent === ERROR_MESSAGES.INVALID_URL) {
                        hideJsError(jsErrorDiv);
                    }
                } catch (_) {
                    fieldIsValidByJsSpecificChecks = false;
                    showJsError(jsErrorDiv, ERROR_MESSAGES.INVALID_URL);
                }
            } else {
                if (jsErrorDiv && jsErrorDiv.textContent === ERROR_MESSAGES.INVALID_URL) {
                    hideJsError(jsErrorDiv);
                }
            }
        }

        // Determine overall validity based on error visibility
        const djangoErrorIsVisible = isElementVisible(djangoErrorDiv);
        const anyJsErrorIsVisible = isElementVisible(jsErrorDiv);

        let isFieldConsideredInvalid = false;

        if (djangoErrorIsVisible) {
            isFieldConsideredInvalid = true;
        } else if (!fieldIsValidByJsSpecificChecks) {
            isFieldConsideredInvalid = true;
        } else if (anyJsErrorIsVisible) {
            isFieldConsideredInvalid = true;
        }

        // Apply appropriate Bootstrap validation classes
        if (isFieldConsideredInvalid) {
            fieldElement.classList.add(CSS_CLASSES.IS_INVALID);
            fieldElement.classList.remove(CSS_CLASSES.IS_VALID);
        } else {
            fieldElement.classList.remove(CSS_CLASSES.IS_INVALID);

            const shouldApplyValidStyle = !isEffectivelyEmpty &&
                !FIELDS_EXCLUDED_FROM_VALID_STYLING.includes(fieldName);

            if (shouldApplyValidStyle) {
                fieldElement.classList.add(CSS_CLASSES.IS_VALID);
            } else {
                fieldElement.classList.remove(CSS_CLASSES.IS_VALID);
            }
        }
    }

    // Process each form element
    formElements.forEach(function (el) {
        // Add Bootstrap classes to inputs and selects
        if (el.tagName.toLowerCase() === 'select') {
            if (!el.classList.contains(CSS_CLASSES.FORM_SELECT)) el.classList.add(CSS_CLASSES.FORM_SELECT);
        } else {
            if (!el.classList.contains(CSS_CLASSES.FORM_CONTROL)) el.classList.add(CSS_CLASSES.FORM_CONTROL);
        }

        // Add empty placeholder for floating labels if needed
        if (el.tagName.toLowerCase() !== 'select' && el.value === '' && !el.hasAttribute('placeholder') &&
            (PLACEHOLDER_INPUT_TYPES.includes(el.type) || el.tagName.toLowerCase() === 'textarea')) {
            el.setAttribute('placeholder', EMPTY_PLACEHOLDER);
        }

        // Find field container and error elements
        const fieldContainer = el.closest('.field-container-' + el.name);
        if (!fieldContainer) {
            console.warn(`Field container for "${el.name}" not found.`);
            return;
        }

        const djangoErrorDiv = fieldContainer.querySelector(SELECTORS.DJANGO_ERROR);
        const jsErrorDiv = fieldContainer.querySelector(SELECTORS.JS_ERROR);

        // Determine validation event type based on field type
        const eventType = (el.tagName.toLowerCase() === 'select' || el.type === 'checkbox' || el.type === 'radio') ? 'change' : 'input';

        // Add input/change event listener
        el.addEventListener(eventType, function () {
            // Hide Django "required" error if user starts typing
            if (djangoErrorDiv && isElementVisible(djangoErrorDiv) && djangoErrorDiv.textContent.toLowerCase().includes('this field is required')) {
                djangoErrorDiv.style.display = 'none';
            }
            // Hide JS "required" error if user starts typing
            if (jsErrorDiv && isElementVisible(jsErrorDiv) && jsErrorDiv.textContent === ERROR_MESSAGES.REQUIRED_FIELD) {
                hideJsError(jsErrorDiv);
            }
            updateAdFieldOverallValidity(el, djangoErrorDiv, jsErrorDiv);
        });

        // Add blur event listener for validation on focus loss
        el.addEventListener('blur', function () {
            const isRequired = el.hasAttribute('required') || el.required;
            const isSelect = el.tagName.toLowerCase() === 'select';
            const isEmpty = isSelect ? el.value === '' : el.value.trim() === '';

            if (isEmpty && isRequired) {
                const djangoErrorIsPresent = isElementVisible(djangoErrorDiv);
                const otherJsErrorIsPresent = isElementVisible(jsErrorDiv) && jsErrorDiv.textContent !== ERROR_MESSAGES.REQUIRED_FIELD;

                if (!djangoErrorIsPresent && !otherJsErrorIsPresent) {
                    showJsError(jsErrorDiv, ERROR_MESSAGES.REQUIRED_FIELD);
                }
            } else {
                if (jsErrorDiv && jsErrorDiv.textContent === ERROR_MESSAGES.REQUIRED_FIELD) {
                    hideJsError(jsErrorDiv);
                }
            }
            updateAdFieldOverallValidity(el, djangoErrorDiv, jsErrorDiv);
        });

        // Initial validation state on page load
        if (isElementVisible(djangoErrorDiv)) {
            el.classList.add(CSS_CLASSES.IS_INVALID);
            el.classList.remove(CSS_CLASSES.IS_VALID);
        }
        updateAdFieldOverallValidity(el, djangoErrorDiv, jsErrorDiv);
    });
});