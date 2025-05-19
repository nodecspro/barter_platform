# ads/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Ad, ExchangeProposal


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class AdSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)
    # For write operations, we'll set the user from request
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="user", write_only=True, required=False
    )
    # Display choice value
    condition_display = serializers.CharField(
        source="get_condition_display", read_only=True
    )
    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )

    class Meta:
        model = Ad
        fields = [
            "id",
            "user",
            "user_id",
            "title",
            "description",
            "image_url",
            "category",
            "category_display",
            "condition",
            "condition_display",
            "created_at",
            "is_active",
        ]
        read_only_fields = ["id", "created_at", "user"]

    def create(self, validated_data):
        # user_id is popped because we set it from the request context in the view
        if "user_id" in validated_data:  # Should not happen if user is set in view
            validated_data.pop("user_id")
        return super().create(validated_data)


class ExchangeProposalSerializer(serializers.ModelSerializer):
    proposer = UserSimpleSerializer(read_only=True)
    ad_sender = AdSerializer(read_only=True)
    ad_receiver = AdSerializer(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    # For write operations
    proposer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="proposer", write_only=True, required=False
    )
    ad_sender_id = serializers.PrimaryKeyRelatedField(
        queryset=Ad.objects.all(), source="ad_sender", write_only=True
    )
    ad_receiver_id = serializers.PrimaryKeyRelatedField(
        queryset=Ad.objects.all(), source="ad_receiver", write_only=True
    )

    class Meta:
        model = ExchangeProposal
        fields = [
            "id",
            "proposer",
            "proposer_id",
            "ad_sender",
            "ad_sender_id",
            "ad_receiver",
            "ad_receiver_id",
            "comment",
            "status",
            "status_display",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "proposer",
            "ad_sender",
            "ad_receiver",
            "status",
        ]  # Status updated via separate action

    def validate(self, data):
        # User will be set from request in viewset's perform_create
        request_user = self.context["request"].user
        ad_sender = data.get("ad_sender")
        ad_receiver = data.get("ad_receiver")

        if not ad_sender:
            raise serializers.ValidationError({"ad_sender_id": "Это поле обязательно."})
        if not ad_receiver:
            raise serializers.ValidationError(
                {"ad_receiver_id": "Это поле обязательно."}
            )

        if ad_sender.user != request_user:
            raise serializers.ValidationError(
                {"ad_sender_id": "Вы должны быть владельцем предлагаемого товара."}
            )
        if ad_receiver.user == request_user:
            raise serializers.ValidationError(
                {"ad_receiver_id": "Нельзя предлагать обмен на свой собственный товар."}
            )
        if ad_sender == ad_receiver:
            raise serializers.ValidationError(
                "Предлагаемый и запрашиваемый товары должны быть разными."
            )
        if (
            ExchangeProposal.objects.filter(
                ad_sender=ad_sender, ad_receiver=ad_receiver, proposer=request_user
            )
            .exclude(status="rejected")
            .exists()
        ):
            raise serializers.ValidationError(
                "Вы уже отправили предложение по этому товару с этим вашим товаром."
            )
        return data

    def create(self, validated_data):
        # proposer_id is popped because we set it from the request context in the view
        if "proposer_id" in validated_data:
            validated_data.pop("proposer_id")
        # status is set to pending by default in the model
        return super().create(validated_data)
