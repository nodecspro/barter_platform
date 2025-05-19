from django import forms
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import Ad, ExchangeProposal


class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ["title", "description", "image_url", "category", "condition"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "image_url": forms.URLInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "condition": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "title": "Заголовок",
            "description": "Описание товара",
            "image_url": "URL изображения (опционально)",
            "category": "Категория",
            "condition": "Состояние товара",
        }


class ExchangeProposalForm(forms.ModelForm):
    # ad_sender will be a choice of the current user's ads
    # ad_receiver will typically be fixed (the ad being viewed)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            # User must have ads to propose an exchange
            self.fields["ad_sender"].queryset = Ad.objects.filter(
                user=user, is_active=True
            )
            self.fields["ad_sender"].empty_label = "Выберите ваш товар для обмена"
            if not self.fields["ad_sender"].queryset.exists():
                self.fields["ad_sender"].widget.attrs["disabled"] = True
                self.fields["ad_sender"].help_text = (
                    "У вас нет активных объявлений для предложения обмена."
                )

    class Meta:
        model = ExchangeProposal
        fields = [
            "ad_sender",
            "comment",
        ]  # ad_receiver and proposer will be set in the view
        widgets = {
            "ad_sender": forms.Select(attrs={"class": "form-select"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
        labels = {
            "ad_sender": "Ваш товар для обмена",
            "comment": "Комментарий (опционально)",
        }


class CustomUserCreationForm(UserCreationForm):
    username = UsernameField(
        label=_("Имя пользователя (логин)"),
        widget=forms.TextInput(attrs={"autofocus": True}),
        help_text="",
    )
    email = forms.EmailField(
        required=True,
        label=_("Email"),
        help_text="",
    )
    first_name = forms.CharField(
        max_length=150,
        required=False,
        label=_("Имя"),
        help_text="",
    )
    last_name = (
        forms.CharField(
            max_length=150,
            required=False,
            label=_("Фамилия"),
            help_text="",
        ),
    )
    password = forms.CharField(
        label=_("Пароль"),
        widget=forms.PasswordInput,
        help_text="",
        strip=False,
    )
    password2 = forms.CharField(
        label=_("Подтверждение пароля"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name")
        labels = {
            "username": _("Имя пользователя (логин)"),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
