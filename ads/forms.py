# ads/forms.py
from django import forms
from django.contrib.auth.models import User  # Используем стандартную модель User
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from .models import Ad, ExchangeProposal


class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        # Убедитесь, что все эти поля ('image_url', 'category', 'condition') есть в вашей модели Ad
        fields = ["title", "description", "image_url", "category", "condition"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "image_url": forms.URLInput(
                attrs={"class": "form-control"}
            ),  # Используем URLInput для URL
            "category": forms.Select(attrs={"class": "form-select"}),
            "condition": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "title": "Заголовок объявления",
            "description": "Подробное описание товара",
            "image_url": "URL изображения (необязательно)",
            "category": "Категория товара",
            "condition": "Состояние товара",
        }
        help_texts = {
            "image_url": "Укажите прямую ссылку на изображение (например, https://example.com/image.jpg).",
            "description": "Опишите товар как можно подробнее, это поможет быстрее найти покупателя/обменщика.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.required and not isinstance(field.widget, forms.CheckboxInput):
                field.label_suffix = " *"


class ExchangeProposalForm(forms.ModelForm):
    # Определяем поле ad_sender здесь, чтобы контролировать его queryset и виджет
    ad_sender = forms.ModelChoiceField(
        queryset=Ad.objects.none(),  # Изначально пустой queryset
        label="Ваш товар для обмена",
        help_text="Выберите одно из ваших активных объявлений.",
        empty_label="-- Выберите ваш товар --",
        widget=forms.Select(attrs={"class": "form-select"}),
        required=True,  # Поле обязательно для заполнения
    )

    class Meta:
        model = ExchangeProposal
        # Указываем поля, которые пользователь должен заполнить в форме.
        # 'proposer' и 'ad_receiver' будут установлены во view.
        # 'status' будет иметь значение по умолчанию или не будет в форме.
        fields = ["ad_sender", "comment"]
        widgets = {
            "comment": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Ваш комментарий к предложению (необязательно)",
                    "class": "form-control",
                }
            ),
        }
        labels = {
            "comment": "Комментарий",
            "ad_sender": "Мой товар, который я предлагаю на обмен",
        }

    def __init__(self, *args, **kwargs):
        # Извлекаем 'user' из kwargs ПЕРЕД вызовом super().__init__
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)  # Вызываем родительский конструктор

        if user and user.is_authenticated:
            # Фильтруем queryset для поля ad_sender
            queryset = Ad.objects.filter(
                user=user, is_active=True
            )  # Предполагаем, что у Ad есть поле is_active
            self.fields["ad_sender"].queryset = queryset

            if not queryset.exists():
                # Генерируем URL для создания объявления. Убедитесь, что 'ads:ad_create' - правильное имя.
                try:
                    create_ad_url = forms.models.resolve_to_name(
                        "ads:ad_create"
                    )  # Было resolve_url, теперь resolve_to_name
                except Exception:  # Если URL не найден, просто не добавляем ссылку
                    create_ad_url = None

                help_text_parts = ["У вас нет активных объявлений для обмена."]
                if create_ad_url:
                    help_text_parts.append(
                        f" <a href='{forms.utils.escape(create_ad_url)}'>Создайте объявление</a>, чтобы предложить его."
                    )  # forms.utils.escape для безопасности

                self.fields["ad_sender"].help_text = "".join(help_text_parts)
                self.fields["ad_sender"].widget.attrs["disabled"] = True
        else:
            self.fields["ad_sender"].queryset = Ad.objects.none()
            self.fields["ad_sender"].widget.attrs["disabled"] = True
            self.fields["ad_sender"].help_text = (
                "Войдите в систему, чтобы выбрать товар для обмена."
            )

        # Если форма создается для существующего объекта (редактирование),
        # и ad_sender уже установлен, убедимся, что он есть в queryset.
        if self.instance and self.instance.pk and self.instance.ad_sender:
            current_ad_sender_qs = Ad.objects.filter(pk=self.instance.ad_sender.pk)
            # Объединяем текущий queryset (активные объявления пользователя)
            # с уже выбранным объявлением, чтобы оно было в списке, даже если стало неактивным.
            # Но пользователь не сможет выбрать другие неактивные объявления.
            self.fields["ad_sender"].queryset = (
                self.fields["ad_sender"].queryset | current_ad_sender_qs
            ).distinct()

        # Добавляем звездочку к обязательным полям
        for field_name, field in self.fields.items():
            if field.required and not isinstance(field.widget, forms.CheckboxInput):
                field.label_suffix = " *"


class CustomUserRegistrationForm(forms.ModelForm):
    username = forms.CharField(
        label=_("Имя пользователя (логин)"),
        widget=forms.TextInput(attrs={"autofocus": True, "class": "form-control"}),
        help_text=_(
            "Обязательное поле. 150 символов или меньше. Только буквы, цифры и символы @/./+/-/_."
        ),
        max_length=150,
        # Валидаторы username уже должны быть на модели User, ModelForm их подхватит.
        # Если нужно добавить специфичные, можно сделать так:
        # validators=[User._meta.get_field("username").validators[0]], # Пример
    )
    email = forms.EmailField(
        required=True,
        label=_("Email"),
        help_text=_("Обязательное поле."),
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
    first_name = forms.CharField(
        max_length=150,
        required=False,
        label=_("Имя"),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        label=_("Фамилия"),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    password = forms.CharField(
        label=_("Пароль"),
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        help_text=_(
            "<ul>"
            "<li>Ваш пароль не должен слишком походить на другую вашу личную информацию.</li>"
            "<li>Ваш пароль должен содержать как минимум 8 символов.</li>"
            "<li>Ваш пароль не может быть слишком распространённым.</li>"
            "<li>Ваш пароль не может состоять только из цифр.</li>"
            "</ul>"
        ),
        strip=False,
        validators=[validate_password],
    )
    password_confirm = forms.CharField(  # Добавляем поле для подтверждения пароля
        label=_("Подтверждение пароля"),
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        strip=False,
        help_text=_("Введите тот же пароль, что и выше, для проверки."),
    )

    class Meta:
        model = User  # Используем стандартную модель User Django
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
        )  # password_confirm не из модели

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем звездочку к обязательным полям
        for field_name, field in self.fields.items():
            if field.required:
                field.label_suffix = " *"
            # Добавляем классы Bootstrap ко всем виджетам, если они еще не заданы
            if "class" not in field.widget.attrs:
                field.widget.attrs.update({"class": "form-control"})
            field.widget.attrs.update(
                {"class": field.widget.attrs.get("class", "") + " mb-2"}
            )

    def clean_password_confirm(self):  # Метод для валидации подтверждения пароля
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError(_("Пароли не совпадают."))
        return password_confirm

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
