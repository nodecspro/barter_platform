from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend


from .models import Ad, ExchangeProposal
from .forms import AdForm, ExchangeProposalForm, CustomUserRegistrationForm
from .serializers import AdSerializer, ExchangeProposalSerializer
from .permissions import (
    IsOwnerOrReadOnly,
    IsProposalOwnerOrReceiver,
    IsReceiverOfAdForProposal,
)


# --- HTML Views (Django CBV) ---


class AdListView(ListView):
    model = Ad
    template_name = "ads/ad_list.html"
    context_object_name = "ads"
    paginate_by = 10

    def get_queryset(self):
        queryset = Ad.objects.filter(is_active=True).select_related("user")
        query = self.request.GET.get("q")
        category = self.request.GET.get("category")
        condition = self.request.GET.get("condition")

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
        if category:
            queryset = queryset.filter(category=category)
        if condition:
            queryset = queryset.filter(condition=condition)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Ad.CATEGORY_CHOICES
        context["conditions"] = Ad.CONDITION_CHOICES
        context["current_query"] = self.request.GET.get("q", "")
        context["current_category"] = self.request.GET.get("category", "")
        context["current_condition"] = self.request.GET.get("condition", "")
        return context


class AdDetailView(DetailView):
    model = Ad
    template_name = "ads/ad_detail.html"
    context_object_name = "ad"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated and self.object.user != self.request.user:
            # Only show proposal form if user is logged in and not the owner
            context["proposal_form"] = ExchangeProposalForm(user=self.request.user)
            # Check if user already proposed for this ad with any of their items
            existing_proposals = ExchangeProposal.objects.filter(
                proposer=self.request.user, ad_receiver=self.object
            ).exclude(status="rejected")
            context["existing_proposals"] = existing_proposals
        return context


class AdCreateView(LoginRequiredMixin, CreateView):
    model = Ad
    form_class = AdForm
    template_name = "ads/ad_form.html"

    def form_valid(self, form):
        user = form.save()
        form.instance.user = self.request.user
        messages.success(self.request, "Объявление успешно создано!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Создать объявление"
        return context


class AdUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Ad
    form_class = AdForm
    template_name = "ads/ad_form.html"

    def test_func(self):
        ad = self.get_object()
        return self.request.user == ad.user

    def form_valid(self, form):
        messages.success(self.request, "Объявление успешно обновлено!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Редактировать объявление"
        return context


class AdDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Ad
    template_name = "ads/ad_confirm_delete.html"
    success_url = reverse_lazy("ads:my_ads")  # Redirect to user's ads list

    def test_func(self):
        ad = self.get_object()
        return self.request.user == ad.user

    def form_valid(self, form):
        # Instead of full delete, maybe soft delete?
        # self.object.is_active = False
        # self.object.save()
        # messages.success(self.request, "Объявление было удалено (деактивировано).")
        # return redirect(self.success_url)
        messages.success(self.request, "Объявление успешно удалено!")
        return super().form_valid(form)


@login_required
def my_ads_view(request):
    user_ads = Ad.objects.filter(user=request.user).order_by("-created_at")
    paginator = Paginator(user_ads, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "ads/my_ads_list.html", {"page_obj": page_obj})


# --- Exchange Proposal HTML Views ---


@login_required
def create_exchange_proposal(request, ad_receiver_pk):
    ad_receiver = get_object_or_404(Ad, pk=ad_receiver_pk, is_active=True)

    if ad_receiver.user == request.user:
        messages.error(
            request, "Вы не можете предложить обмен на свой собственный товар."
        )
        return redirect("ads:ad_detail", pk=ad_receiver_pk)

    # Check if a non-rejected proposal already exists from this user for this ad_receiver
    # (allowing multiple proposals if different ad_senders are used)
    # Or, enforce only one active proposal per (proposer, ad_receiver) pair
    # current_proposal_exists = ExchangeProposal.objects.filter(
    #     proposer=request.user,
    #     ad_receiver=ad_receiver
    # ).exclude(status='rejected').exists()
    # if current_proposal_exists:
    #    messages.warning(request, "У вас уже есть активное предложение для этого товара.")
    #    return redirect('ads:ad_detail', pk=ad_receiver_pk)

    if request.method == "POST":
        form = ExchangeProposalForm(request.POST, user=request.user)
        if form.is_valid():
            if not form.cleaned_data.get("ad_sender"):
                messages.error(
                    request,
                    "Пожалуйста, выберите ваш товар для обмена. Если список пуст, у вас нет активных объявлений.",
                )
                return render(
                    request,
                    "ads/proposal_form.html",
                    {"form": form, "ad_receiver": ad_receiver},
                )

            proposal = form.save(commit=False)
            proposal.proposer = request.user
            proposal.ad_receiver = ad_receiver

            # Double check for existing non-rejected proposal with the same ad_sender and ad_receiver
            if (
                ExchangeProposal.objects.filter(
                    proposer=request.user,
                    ad_sender=proposal.ad_sender,
                    ad_receiver=ad_receiver,
                )
                .exclude(status="rejected")
                .exists()
            ):
                messages.warning(
                    request,
                    "Вы уже отправили такое же предложение (с этим вашим товаром на этот запрашиваемый товар).",
                )
                return redirect("ads:ad_detail", pk=ad_receiver_pk)

            try:
                proposal.full_clean()  # Run model-level validation
                proposal.save()
                messages.success(
                    request,
                    f"Предложение обмена для '{ad_receiver.title}' успешно отправлено!",
                )
                return redirect("ads:ad_detail", pk=ad_receiver_pk)
            except forms.ValidationError as e:
                messages.error(request, f"Ошибка валидации: {e}")

        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = ExchangeProposalForm(user=request.user)

    return render(
        request, "ads/proposal_form.html", {"form": form, "ad_receiver": ad_receiver}
    )


@login_required
def my_proposals_view(request):
    sent_proposals = (
        ExchangeProposal.objects.filter(proposer=request.user)
        .select_related("ad_sender", "ad_receiver", "ad_receiver__user")
        .order_by("-created_at")
    )
    received_proposals = (
        ExchangeProposal.objects.filter(ad_receiver__user=request.user)
        .select_related("ad_sender", "ad_sender__user", "ad_receiver", "proposer")
        .order_by("-created_at")
    )

    context = {
        "sent_proposals": sent_proposals,
        "received_proposals": received_proposals,
    }
    return render(request, "ads/my_proposals_list.html", context)


@login_required
def update_proposal_status(request, proposal_pk, new_status):
    proposal = get_object_or_404(ExchangeProposal, pk=proposal_pk)

    if proposal.ad_receiver.user != request.user:
        messages.error(
            request, "Только получатель предложения может изменить его статус."
        )
        return redirect("ads:my_proposals")

    if new_status not in ["accepted", "rejected"]:
        messages.error(request, "Недопустимый статус.")
        return redirect("ads:my_proposals")

    if proposal.status != "pending":
        messages.warning(request, "Статус этого предложения уже был изменен.")
        return redirect("ads:my_proposals")

    proposal.status = new_status
    proposal.save()

    if new_status == "accepted":
        messages.success(
            request, f"Предложение по товару '{proposal.ad_sender.title}' принято!"
        )
        # Optional: Deactivate both ads involved in the accepted exchange
        # proposal.ad_sender.is_active = False
        # proposal.ad_sender.save()
        # proposal.ad_receiver.is_active = False
        # proposal.ad_receiver.save()
        # messages.info(request, "Оба объявления, участвующие в обмене, были деактивированы.")
    elif new_status == "rejected":
        messages.info(
            request, f"Предложение по товару '{proposal.ad_sender.title}' отклонено."
        )

    return redirect("ads:my_proposals")


# --- DRF API Views (ViewSets) ---


class AdViewSet(viewsets.ModelViewSet):
    queryset = (
        Ad.objects.filter(is_active=True).select_related("user").order_by("-created_at")
    )
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["category", "condition", "user__username"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "title"]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        # Soft delete example for API, or actual delete
        # instance.is_active = False
        # instance.save()
        instance.delete()  # Default behavior


class ExchangeProposalViewSet(viewsets.ModelViewSet):
    serializer_class = ExchangeProposalSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsProposalOwnerOrReceiver,
    ]  # Basic auth + custom for object level
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = {
        "status": ["exact"],
        "proposer__username": ["exact"],
        "ad_receiver__user__username": ["exact"],
        "ad_sender__id": ["exact"],  # Filter by user's ad offered
        "ad_receiver__id": ["exact"],  # Filter by ad requested
    }
    ordering_fields = ["created_at", "status"]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return ExchangeProposal.objects.none()
        # Users can see proposals they sent or proposals for their ads
        return (
            ExchangeProposal.objects.filter(
                Q(proposer=user) | Q(ad_receiver__user=user)
            )
            .select_related(
                "proposer",
                "ad_sender",
                "ad_sender__user",
                "ad_receiver",
                "ad_receiver__user",
            )
            .distinct()
        )

    def perform_create(self, serializer):
        # ad_sender must belong to self.request.user
        # ad_receiver must not belong to self.request.user
        # These are validated in serializer's validate method
        serializer.save(proposer=self.request.user)

    @action(
        detail=True, methods=["post"], permission_classes=[IsReceiverOfAdForProposal]
    )
    def accept(self, request, pk=None):
        proposal = self.get_object()
        if proposal.status != "pending":
            return Response(
                {"detail": "Предложение уже обработано."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        proposal.status = "accepted"
        proposal.save()
        # Optional: Deactivate ads
        # proposal.ad_sender.is_active = False
        # proposal.ad_sender.save()
        # proposal.ad_receiver.is_active = False
        # proposal.ad_receiver.save()
        return Response(
            ExchangeProposalSerializer(proposal, context={"request": request}).data
        )

    @action(
        detail=True, methods=["post"], permission_classes=[IsReceiverOfAdForProposal]
    )
    def reject(self, request, pk=None):
        proposal = self.get_object()
        if proposal.status != "pending":
            return Response(
                {"detail": "Предложение уже обработано."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        proposal.status = "rejected"
        proposal.save()
        return Response(
            ExchangeProposalSerializer(proposal, context={"request": request}).data
        )

    # Proposer might want to cancel their own pending proposal
    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )  # Custom check inside
    def cancel(self, request, pk=None):
        proposal = self.get_object()
        if proposal.proposer != request.user:
            return Response(
                {"detail": "Только инициатор может отменить предложение."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if proposal.status != "pending":
            return Response(
                {"detail": "Нельзя отменить уже обработанное предложение."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Instead of deleting, could mark as 'cancelled' if you add that status
        proposal.delete()
        return Response(
            {"detail": "Предложение отменено."}, status=status.HTTP_204_NO_CONTENT
        )


class SignUpView(CreateView):
    form_class = CustomUserRegistrationForm
    success_url = reverse_lazy(
        "login"
    )  # Or 'ads:ad_list' if you want to redirect to main page
    template_name = "registration/signup.html"

    def form_valid(self, form):
        user = form.save()
        messages.success(
            self.request, "Регистрация прошла успешно! Пожалуйста, войдите."
        )
        return super().form_valid(form)  # This will redirect to success_url
