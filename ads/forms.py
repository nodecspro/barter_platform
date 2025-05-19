# ads/forms.py
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import (
    validate_password,
)  # Для валидации пароля
from .models import Ad, ExchangeProposal  # Import the Ad and ExchangeProposal models


class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ["title", "description", "image_url", "category", "condition"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }
        labels = {  # Можете переопределить метки здесь, если стандартные не устраивают
            "title": "Заголовок объявления",
            "description": "Подробное описание товара",
            "image_url": "URL изображения (необязательно)",
            "category": "Категория товара",
            "condition": "Состояние товара",
        }
        help_texts = {  # Если хотите добавить help_text, они будут отображены под полями
            "image_url": "Укажите прямую ссылку на изображение (например, https://example.com/image.jpg).",
            "description": "Опишите товар как можно подробнее, это поможет быстрее найти покупателя/обменщика.",
        }


class ExchangeProposalForm(forms.ModelForm):
    class Meta:
        model = ExchangeProposal
        fields = "__all__"  # Placeholder, can be adjusted later


class CustomUserRegistrationForm(forms.ModelForm):  # Наследуемся от ModelForm
    username = forms.CharField(
        label=_("Имя пользователя (логин)"),
        widget=forms.TextInput(attrs={"autofocus": True}),
        help_text="",  # Убираем help_text, будем делать сами
        max_length=150,
        validators=[
            User._meta.get_field("username").validators[0]
        ],  # Стандартный валидатор Django для username
    )
    email = forms.EmailField(required=True, label=_("Email"), help_text="")
    first_name = forms.CharField(
        max_length=150, required=False, label=_("Имя"), help_text=""
    )
    last_name = forms.CharField(
        max_length=150, required=False, label=_("Фамилия"), help_text=""
    )
    password = forms.CharField(
        label=_("Пароль"),
        widget=forms.PasswordInput,
        help_text="",  # Убираем стандартный help_text
        strip=False,
        validators=[
            validate_password
        ],  # Используем стандартные валидаторы пароля Django
    )

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password")

    def save(self, commit=True):
        user = super().save(
            commit=False
        )  # Создаем пользователя, но пароль еще не установлен правильно
        user.set_password(
            self.cleaned_data["password"]
        )  # Устанавливаем пароль правильно
        if commit:
            user.save()
        return user
