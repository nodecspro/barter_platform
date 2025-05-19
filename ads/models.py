from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Ad(models.Model):
    CONDITION_CHOICES = [
        ("new", "Новый"),
        ("used", "Б/У"),
    ]
    # CATEGORY_CHOICES - you might want to make this a separate model later
    # For simplicity now, let's use CharField with predefined choices or free text
    # Example categories (consider making this a ForeignKey to a Category model for better management)
    CATEGORY_CHOICES = [
        ("electronics", "Электроника"),
        ("clothing", "Одежда"),
        ("furniture", "Мебель"),
        ("books", "Книги"),
        ("other", "Другое"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="ads", verbose_name="Пользователь"
    )
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание товара")
    image_url = models.URLField(
        max_length=500, blank=True, null=True, verbose_name="URL изображения"
    )
    # For actual image uploads, you'd use:
    # image = models.ImageField(upload_to='ad_images/', blank=True, null=True, verbose_name="Изображение")
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
    is_active = models.BooleanField(
        default=True, verbose_name="Активно"
    )  # Useful for soft deletes or temporarily hiding

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
        ("pending", "Ожидает"),
        ("accepted", "Принята"),
        ("rejected", "Отклонена"),
    ]

    # The user who initiated the proposal
    proposer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_proposals",
        verbose_name="Инициатор предложения",
    )
    # The ad offered by the proposer
    ad_sender = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name="proposals_sent",
        verbose_name="Предлагаемый товар",
    )
    # The ad requested by the proposer (owned by another user)
    ad_receiver = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name="proposals_received",
        verbose_name="Запрашиваемый товар",
    )
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="pending", verbose_name="Статус"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Предложение от {self.proposer.username} по {self.ad_receiver.title} (статус: {self.get_status_display()})"

    class Meta:
        verbose_name = "Предложение обмена"
        verbose_name_plural = "Предложения обмена"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["ad_sender", "ad_receiver"], name="unique_proposal_pair"
            )
        ]

    # Ensure proposer owns the ad_sender and does not own ad_receiver
    def clean(self):
        from django.core.exceptions import ValidationError

        if self.ad_sender.user != self.proposer:
            raise ValidationError(
                "Инициатор предложения должен быть владельцем предлагаемого товара (ad_sender)."
            )
        if self.ad_receiver.user == self.proposer:
            raise ValidationError(
                "Нельзя предлагать обмен на свой собственный товар (ad_receiver)."
            )
        if self.ad_sender == self.ad_receiver:
            raise ValidationError(
                "Предлагаемый и запрашиваемый товары должны быть разными."
            )
