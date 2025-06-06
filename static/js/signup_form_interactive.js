document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("signupForm");
    if (!form) return;

    const passwordField = form.querySelector("#id_password1");

    // --- Добавление кнопок видимости пароля ---
    [passwordField].forEach((field) => {
        if (field) {
            field.classList.add("has-password-toggle");
            const wrapper = field.closest(".form-floating");
            if (wrapper) {
                const toggleBtn = document.createElement("button");
                toggleBtn.setAttribute("type", "button");
                toggleBtn.classList.add("password-toggle-btn");
                toggleBtn.setAttribute("tabindex", "-1");
                toggleBtn.innerHTML = '<i class="bi bi-eye-slash-fill"></i>';
                wrapper.appendChild(toggleBtn);
                toggleBtn.addEventListener("click", function () {
                    if (field.type === "password") {
                        field.type = "text";
                        this.innerHTML = '<i class="bi bi-eye-fill"></i>';
                    } else {
                        field.type = "password";
                        this.innerHTML = '<i class="bi bi-eye-slash-fill"></i>';
                    }
                    field.focus();
                });
            }
        }
    });
    // --- Конец блока кнопок видимости пароля ---

    const formElements = Array.from(form.querySelectorAll('.form-floating > input:not([type="hidden"]), .form-floating > select, .form-floating > textarea'));

    const validationFeedbacks = {
        username: {
            container: document.getElementById("username-feedback"),
            rules: { length: document.getElementById("un-length"), chars: document.getElementById("un-chars") },
            validate: (value, el) => {
                let lenValid = value.length >= 3 && value.length <= 150;
                let charsValid = /^[a-zA-Z0-9@.+_-]*$/.test(value); // * позволяет пустое для начальной валидации
                updateRule(validationFeedbacks.username.rules.length, lenValid, value !== "" || el.classList.contains("is-invalid"));
                updateRule(validationFeedbacks.username.rules.chars, charsValid, value !== "" || el.classList.contains("is-invalid"));
                return (value === "" && !el.required) || (lenValid && charsValid);
            },
        },
        email: {
            container: document.getElementById("email-feedback"),
            rules: { format: document.getElementById("em-format") },
            validate: (value, el) => {
                let formatValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) || value === "";
                updateRule(validationFeedbacks.email.rules.format, formatValid, value !== "" || el.classList.contains("is-invalid"));
                return (value === "" && !el.required) || formatValid;
            },
        },
        password: {
            container: document.getElementById("password-rules-container"),
            rules: { length: document.getElementById("pr-length"), letter: document.getElementById("pr-letter"), number: document.getElementById("pr-number") },
            validate: (value, el) => {
                let lenValid = value.length >= 8;
                let letterValid = /[a-zA-Zа-яА-Я]/.test(value);
                let numValid = /\d/.test(value);
                updateRule(validationFeedbacks.password.rules.length, lenValid, value !== "" || el.classList.contains("is-invalid"));
                updateRule(validationFeedbacks.password.rules.letter, letterValid, value !== "" || el.classList.contains("is-invalid"));
                updateRule(validationFeedbacks.password.rules.number, numValid, value !== "" || el.classList.contains("is-invalid"));
                return (value === "" && !el.required) || (lenValid && letterValid && numValid);
            },
        },
    };

    function updateRule(ruleElement, isValid, hasInteractedOrIsInvalid) {
        if (!ruleElement) return;
        ruleElement.classList.toggle("valid", isValid && hasInteractedOrIsInvalid);
        ruleElement.classList.toggle("invalid", !isValid && hasInteractedOrIsInvalid);
        if (!hasInteractedOrIsInvalid) {
            // Сбрасываем, если нет взаимодействия и не было ошибки
            ruleElement.classList.remove("valid", "invalid");
        }
    }

    function toggleFeedbackVisibility(feedbackContainer, show) {
        if (!feedbackContainer) return;
        feedbackContainer.classList.toggle("visible", show);
    }

    formElements.forEach(function (el) {
        // Базовая настройка
        if (!el.classList.contains("form-control") && el.tagName.toLowerCase() !== "select") {
            el.classList.add("form-control");
        }
        if (el.tagName.toLowerCase() === "select" && !el.classList.contains("form-select")) {
            el.classList.add("form-select");
        }
        if (el.value === "" && !el.hasAttribute("placeholder") && (["text", "email", "password"].includes(el.type) || el.tagName.toLowerCase() === "textarea")) {
            el.setAttribute("placeholder", " ");
        }

        const fieldContainer = el.closest(".field-container");
        if (!fieldContainer) return;
        const fieldName = fieldContainer.dataset.fieldName;
        const currentFeedbackConfig = validationFeedbacks[fieldName];
        const djangoErrorDiv = fieldContainer.querySelector(".django-error");
        const jsErrorDiv = fieldContainer.querySelector(".custom-error-message");

        el.addEventListener("focus", function () {
            if (currentFeedbackConfig && currentFeedbackConfig.container) {
                toggleFeedbackVisibility(currentFeedbackConfig.container, true);
                currentFeedbackConfig.validate(el.value, el);
            }
        });

        el.addEventListener("input", function () {
            if (djangoErrorDiv && djangoErrorDiv.offsetParent !== null) djangoErrorDiv.style.display = "none";
            if (jsErrorDiv && jsErrorDiv.offsetParent !== null) hideJsError(jsErrorDiv);

            if (currentFeedbackConfig) currentFeedbackConfig.validate(el.value, el);

            updateFieldOverallValidity(el, currentFeedbackConfig);
        });

        el.addEventListener("blur", function () {
            const fieldContainer = el.closest(".field-container");
            if (!fieldContainer) return;
            const fieldName = fieldContainer.dataset.fieldName;
            const currentFeedbackConfig = validationFeedbacks[fieldName];
            const djangoErrorDiv = fieldContainer.querySelector(".django-error");
            const jsErrorDiv = fieldContainer.querySelector(".custom-error-message");
            const isRequired = el.hasAttribute("required") || el.required;

            if (el.value.trim() === "" && isRequired) {
                showJsError(jsErrorDiv, "Это поле обязательно для заполнения.");
                el.classList.add("is-invalid");
                el.classList.remove("is-valid");
                if (djangoErrorDiv) djangoErrorDiv.style.display = "none";
                if (currentFeedbackConfig && currentFeedbackConfig.container) {
                    toggleFeedbackVisibility(currentFeedbackConfig.container, true); // Показываем, чтобы видеть invalid у правил
                    if (currentFeedbackConfig.rules) {
                        Object.values(currentFeedbackConfig.rules).forEach((ruleEl) => updateRule(ruleEl, false, true));
                    }
                }
            } else {
                if (jsErrorDiv && jsErrorDiv.textContent.includes("Это поле обязательно для заполнения")) {
                    hideJsError(jsErrorDiv);
                }

                let allRulesForFieldValid = true; // Флаг, что все JS правила для этого поля выполнены
                if (currentFeedbackConfig) {
                    allRulesForFieldValid = currentFeedbackConfig.validate(el.value.trim(), el); // Перепроверяем все правила

                    if (currentFeedbackConfig.container) {
                        if (el.value.trim() === "" && !isRequired) {
                            // Если поле не обязательное и пустое, скрываем фидбек
                            toggleFeedbackVisibility(currentFeedbackConfig.container, false);
                        } else if (allRulesForFieldValid && el.value.trim() !== "") {
                            // Если все правила выполнены и поле не пустое, скрываем фидбек
                            // Можно добавить задержку, чтобы пользователь успел увидеть галочки
                            setTimeout(() => {
                                // Проверяем еще раз, не появилось ли ошибок от Django или JS за это время
                                const stillDjangoError = djangoErrorDiv && djangoErrorDiv.offsetParent !== null;
                                const stillJsError = jsErrorDiv && jsErrorDiv.offsetParent !== null;
                                if (!stillDjangoError && !stillJsError) {
                                    toggleFeedbackVisibility(currentFeedbackConfig.container, false);
                                }
                            }, 200); // Задержка в 1 секунду, можно настроить
                        } else {
                            // Если есть ошибки или поле пустое и обязательное, оставляем фидбек видимым
                            toggleFeedbackVisibility(currentFeedbackConfig.container, true);
                        }
                    }
                }
            }
            updateFieldOverallValidity(el, currentFeedbackConfig); // Обновляем is-valid/is-invalid для поля
        });

        if (djangoErrorDiv && djangoErrorDiv.offsetParent !== null) el.classList.add("is-invalid");
    });

    function updateFieldOverallValidity(fieldElement, feedbackConfig) {
        const djangoErrorDiv = fieldElement.closest(".field-container").querySelector(".django-error");
        const jsErrorDiv = fieldElement.closest(".field-container").querySelector(".custom-error-message");
        let allJSRulesValid = true;
        const isRequired = fieldElement.hasAttribute("required") || fieldElement.required;

        if (feedbackConfig && feedbackConfig.rules) {
            allJSRulesValid = Object.values(feedbackConfig.rules).every((ruleEl) => !ruleEl || ruleEl.classList.contains("valid"));
        } else if (fieldElement.name !== "first_name" && fieldElement.name !== "last_name" && fieldElement.value.trim() === "" && isRequired) {
            // Для полей без детальных правил, но обязательных и пустых
            allJSRulesValid = false;
        }

        const djangoErrorIsVisible = djangoErrorDiv && djangoErrorDiv.offsetParent !== null;
        const jsRequiredErrorIsVisible = jsErrorDiv && jsErrorDiv.offsetParent !== null;

        if (fieldElement.value.trim() === "" && isRequired) {
            fieldElement.classList.add("is-invalid");
            fieldElement.classList.remove("is-valid");
        } else if (allJSRulesValid && !djangoErrorIsVisible && !jsRequiredErrorIsVisible) {
            fieldElement.classList.remove("is-invalid");
            if (fieldElement.value.trim() !== "" || (!isRequired && fieldElement.value.trim() === "")) {
                fieldElement.classList.add("is-valid");
            } else {
                fieldElement.classList.remove("is-valid");
            }
        } else {
            // Есть JS ошибки, или серверные ошибки, или JS ошибка "обязательное"
            fieldElement.classList.add("is-invalid");
            fieldElement.classList.remove("is-valid");
        }
    }

    function showJsError(errorDiv, message) {
        if (!errorDiv) return;
        errorDiv.textContent = message;
        errorDiv.style.display = "block";
    }
    function hideJsError(errorDiv) {
        if (!errorDiv) return;
        errorDiv.textContent = "";
        errorDiv.style.display = "none";
    }
});