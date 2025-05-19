from django.contrib import admin
from .models import Ad, ExchangeProposal


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "category", "condition", "created_at", "is_active")
    list_filter = ("category", "condition", "user", "created_at", "is_active")
    search_fields = ("title", "description", "user__username")
    readonly_fields = ("created_at",)


@admin.register(ExchangeProposal)
class ExchangeProposalAdmin(admin.ModelAdmin):
    list_display = (
        "proposer",
        "ad_sender_title",
        "ad_receiver_title",
        "status",
        "created_at",
    )
    list_filter = ("status", "proposer", "ad_receiver__user", "created_at")
    search_fields = (
        "proposer__username",
        "ad_sender__title",
        "ad_receiver__title",
        "comment",
    )
    readonly_fields = ("created_at",)
    autocomplete_fields = ["proposer", "ad_sender", "ad_receiver"]

    def ad_sender_title(self, obj):
        return obj.ad_sender.title

    ad_sender_title.short_description = "Предлагаемый товар"
    ad_sender_title.admin_order_field = "ad_sender__title"

    def ad_receiver_title(self, obj):
        return obj.ad_receiver.title

    ad_receiver_title.short_description = "Запрашиваемый товар"
    ad_receiver_title.admin_order_field = "ad_receiver__title"
