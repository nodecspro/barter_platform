# ads/models.py
from django.db import models
from django.contrib.auth.models import User  # Используем стандартную User
from django.urls import reverse
from django.conf import settings  # Лучше использовать settings.AUTH_USER_MODEL
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class Ad(models.Model):
    CONDITION_CHOICES = [
        ("new", "Новый"),
        ("used", "Б/У"),
    ]
    CATEGORY_CHOICES = [
        ("electronics", "Электроника"),
        ("clothing", "Одежда"),
        ("furniture", "Мебель"),
        ("books", "Книги"),
        ("other", "Другое"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Заменено на settings.AUTH_USER_MODEL
        on_delete=models.CASCADE,
        related_name="ads",
        verbose_name="Пользователь",
    )
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание товара")
    image_url = models.URLField(
        max_length=500, blank=True, null=True, verbose_name="URL изображения"
    )
    # image = models.ImageField(upload_to='ad_images/', blank=True, null=True, verbose_name="Изображение") # Если будете использовать загрузку файлов
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="other",
        verbose_name="Категория",
    )
    condition = models.CharField(
        max_length=10, choices=CONDITION_CHOICES, verbose_name="Состояние"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    is_active = models.BooleanField(default=True, verbose_name="Активно")

    def __str__(self):
        return f"{self.title} (от {self.user.username})"

    def get_absolute_url(self):
        return reverse("ads:ad_detail", kwargs={"pk": self.pk})

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ["-created_at"]


class ExchangeProposal(models.Model):
    STATUS_CHOICES = [
        ("pending", "Ожидает ответа"),  # Изменено для соответствия вашему views.py
        ("accepted", "Принято"),  # Изменено
        ("rejected", "Отклонено"),  # Изменено
    ]

    proposer = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Заменено на settings.AUTH_USER_MODEL
        on_delete=models.CASCADE,
        related_name="sent_proposals",
        verbose_name="Инициатор предложения",
    )
    ad_sender = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name="proposals_sent_with_this_ad",  # Более точное related_name
        verbose_name="Предлагаемый товар (от инициатора)",
    )
    ad_receiver = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name="proposals_received_for_this_ad",  # Более точное related_name
        verbose_name="Запрашиваемый товар (получателя)",
    )
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="pending", verbose_name="Статус"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Дата обновления"
    )  # Добавлено поле updated_at

    def __str__(self):
        # Используем username, если proposer установлен, иначе placeholder
        proposer_username = (
            self.proposer.username
            if hasattr(self, "proposer") and self.proposer
            else "[неизвестный инициатор]"
        )
        ad_receiver_title = (
            self.ad_receiver.title
            if hasattr(self, "ad_receiver") and self.ad_receiver
            else "[неизвестный товар]"
        )
        return f"Предложение от {proposer_username} по '{ad_receiver_title}' (статус: {self.get_status_display()})"

    class Meta:
        verbose_name = "Предложение обмена"
        verbose_name_plural = "Предложения обмена"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "proposer",
                    "ad_sender",
                    "ad_receiver",
                ],  # Добавил proposer для большей уникальности
                condition=models.Q(status="pending") | models.Q(status="accepted"),
                name="unique_active_proposal_for_ads_by_user",
            )
        ]

    def clean(self):
        # Вызываем родительский clean в первую очередь
        super().clean()

        if (
            hasattr(self, "ad_sender")
            and self.ad_sender
            and hasattr(self, "ad_receiver")
            and self.ad_receiver
        ):
            if (
                self.ad_sender_id == self.ad_receiver_id
            ):  # Сравниваем ID для эффективности
                raise ValidationError(
                    _("Предлагаемый и запрашиваемый товары должны быть разными.")
                )

        if (
            hasattr(self, "proposer")
            and self.proposer
            and hasattr(self, "ad_sender")
            and self.ad_sender
        ):
            if self.ad_sender.user != self.proposer:
                # Эта ошибка должна быть привязана к полю ad_sender, если возможно.
                # Если эта логика не обрабатывается в форме, то здесь.
                raise ValidationError(
                    {
                        "ad_sender": _(
                            "Инициатор предложения должен быть владельцем предлагаемого товара."
                        )
                    }
                )

        if (
            hasattr(self, "proposer")
            and self.proposer
            and hasattr(self, "ad_receiver")
            and self.ad_receiver
        ):
            if self.ad_receiver.user == self.proposer:
                # Эта ошибка относится к общей логике предложения.
                raise ValidationError(
                    _(
                        "Нельзя предлагать обмен на товар, который уже принадлежит вам (инициатору предложения)."
                    )
                )
