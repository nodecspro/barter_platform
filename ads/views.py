from django import forms  # Нужен для forms.ValidationError
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

from rest_framework import (
    viewsets,
    permissions,
    status as drf_status,
    filters,
)  # Переименовал status в drf_status
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
        # Убедимся, что is_active есть в модели Ad
        queryset = (
            Ad.objects.filter(is_active=True)
            .select_related("user")
            .order_by("-created_at")
        )
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
        # Убедимся, что эти атрибуты есть у модели Ad или определены где-то еще
        context["categories"] = getattr(Ad, "CATEGORY_CHOICES", [])
        context["conditions"] = getattr(Ad, "CONDITION_CHOICES", [])
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
        # Убедимся, что у Ad есть поле user
        if self.request.user.is_authenticated and self.object.user != self.request.user:
            context["proposal_form"] = ExchangeProposalForm(user=self.request.user)
            existing_proposals = ExchangeProposal.objects.filter(
                proposer=self.request.user, ad_receiver=self.object
            ).exclude(
                status="rejected"
            )  # 'rejected' - убедитесь, что это значение соответствует модели
            context["existing_proposals"] = existing_proposals
        return context


class AdCreateView(LoginRequiredMixin, CreateView):
    model = Ad
    form_class = AdForm
    template_name = "ads/ad_form.html"
    # success_url = reverse_lazy("ads:ad_list") # Или get_absolute_url модели Ad

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Объявление успешно создано!")
        return super().form_valid(form)

    def get_success_url(self):
        # После создания объявления, перенаправляем на страницу деталей этого объявления
        return self.object.get_absolute_url()

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

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Редактировать объявление"
        return context


class AdDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Ad
    template_name = "ads/ad_confirm_delete.html"
    success_url = reverse_lazy("ads:my_ads")
    context_object_name = "object"  # Можно использовать 'ad' для ясности

    def test_func(self):
        ad = self.get_object()
        return self.request.user == ad.user

    # form_valid не нужен для DeleteView, если не нужна кастомная логика перед удалением.
    # Сообщение об успехе лучше добавлять через SuccessMessageMixin или переопределяя delete()
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, "Объявление успешно удалено!")
        return response


@login_required
def my_ads_view(request):
    # Убедимся, что у Ad есть поле user и created_at
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

    if request.method == "POST":
        form = ExchangeProposalForm(request.POST, user=request.user)
        if form.is_valid():
            ad_sender = form.cleaned_data.get("ad_sender")
            if (
                not ad_sender
            ):  # Эта проверка дублирует form.is_valid(), если ad_sender required=True
                # Но полезна, если ad_sender неактивно (disabled) и не передается
                messages.error(
                    request,
                    "Пожалуйста, выберите ваш товар для обмена. Если список пуст или неактивен, у вас нет подходящих активных объявлений.",
                )
                # Передаем форму обратно с ошибками, если они есть
                return render(
                    request,
                    "ads/proposal_form.html",
                    {"form": form, "ad_receiver": ad_receiver},
                )

            # Создаем объект, но не сохраняем в базу данных
            proposal = form.save(commit=False)

            # Устанавливаем обязательные поля, которые не пришли из формы
            proposal.proposer = request.user
            proposal.ad_receiver = ad_receiver
            # proposal.status по умолчанию 'pending' (если так задано в модели)

            # Проверка на дублирующее активное предложение (с теми же товарами)
            # Убедимся, что ad_sender - это объект, а не ID
            if (
                ExchangeProposal.objects.filter(
                    proposer=request.user,
                    ad_sender=ad_sender,  # Используем ad_sender из cleaned_data
                    ad_receiver=ad_receiver,
                )
                .exclude(status="rejected")
                .exists()
            ):
                messages.warning(
                    request,
                    "Вы уже отправляли активное предложение обмена этого вашего товара на этот запрашиваемый товар.",
                )
                return redirect("ads:ad_detail", pk=ad_receiver_pk)

            try:
                # Валидация на уровне модели. Все поля (proposer, ad_receiver) уже должны быть установлены.
                proposal.full_clean()
                proposal.save()  # Теперь сохраняем в базу
                messages.success(
                    request,
                    f"Предложение обмена для '{ad_receiver.title}' успешно отправлено!",
                )
                return redirect("ads:ad_detail", pk=ad_receiver_pk)
            except (
                forms.ValidationError
            ) as e:  # forms.ValidationError из django.core.exceptions
                # Ошибки из full_clean() (включая ошибки из model.clean()) попадут сюда
                # Сбор всех ошибок для отображения
                error_messages = []
                if hasattr(e, "message_dict"):
                    for field, errors in e.message_dict.items():
                        for error in errors:
                            error_messages.append(
                                f"{field if field != '__all__' else 'Общая ошибка'}: {error}"
                            )
                else:
                    error_messages.append(str(e))
                messages.error(
                    request, "Ошибка валидации: " + "; ".join(error_messages)
                )
                # Форма уже содержит ошибки, если они возникли на этапе form.is_valid()
                # Если ошибка из model.clean(), нужно ее как-то добавить в форму для отображения,
                # либо просто показать общее сообщение, как сейчас.
                # form.add_error(None, e) # Это добавит ошибку non-field error в форму

    else:  # GET request
        form = ExchangeProposalForm(user=request.user)

    return render(
        request, "ads/proposal_form.html", {"form": form, "ad_receiver": ad_receiver}
    )


@login_required
def my_proposals_view(request):
    sent_proposals = (
        ExchangeProposal.objects.filter(proposer=request.user)
        .select_related(
            "ad_sender", "ad_receiver", "ad_receiver__user", "proposer"
        )  # Добавил proposer для полноты
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

    # Убедимся, что у Ad есть поле user
    if proposal.ad_receiver.user != request.user:
        messages.error(
            request, "Только получатель предложения может изменить его статус."
        )
        return redirect("ads:my_proposals")

    # Убедимся, что значения статусов соответствуют модели
    if (
        new_status not in dict(ExchangeProposal.STATUS_CHOICES).keys()
    ):  # Проверка по ключам из choices
        messages.error(request, "Недопустимый статус.")
        return redirect("ads:my_proposals")

    if proposal.status != "pending":  # 'pending'
        messages.warning(request, "Статус этого предложения уже был изменен.")
        return redirect("ads:my_proposals")

    proposal.status = new_status
    proposal.save()

    if new_status == "accepted":  # 'accepted'
        messages.success(
            request, f"Предложение по товару '{proposal.ad_sender.title}' принято!"
        )
        # Optional: Deactivate ads logic
    elif new_status == "rejected":  # 'rejected'
        messages.info(
            request, f"Предложение по товару '{proposal.ad_sender.title}' отклонено."
        )

    return redirect("ads:my_proposals")


# --- DRF API Views (ViewSets) ---
# (Оставляю DRF часть без изменений, так как проблема была в HTML views)


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
        instance.delete()


class ExchangeProposalViewSet(viewsets.ModelViewSet):
    serializer_class = ExchangeProposalSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsProposalOwnerOrReceiver,
    ]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = {
        "status": ["exact"],
        "proposer__username": ["exact"],
        "ad_receiver__user__username": ["exact"],
        "ad_sender__id": ["exact"],
        "ad_receiver__id": ["exact"],
    }
    ordering_fields = ["created_at", "status"]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return ExchangeProposal.objects.none()
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
        serializer.save(proposer=self.request.user)

    @action(
        detail=True, methods=["post"], permission_classes=[IsReceiverOfAdForProposal]
    )
    def accept(self, request, pk=None):
        proposal = self.get_object()
        if proposal.status != "pending":
            return Response(
                {"detail": "Предложение уже обработано."},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )
        proposal.status = "accepted"
        proposal.save()
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
                status=drf_status.HTTP_400_BAD_REQUEST,
            )
        proposal.status = "rejected"
        proposal.save()
        return Response(
            ExchangeProposalSerializer(proposal, context={"request": request}).data
        )

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def cancel(self, request, pk=None):
        proposal = self.get_object()
        if proposal.proposer != request.user:
            return Response(
                {"detail": "Только инициатор может отменить предложение."},
                status=drf_status.HTTP_403_FORBIDDEN,
            )
        if proposal.status != "pending":
            return Response(
                {"detail": "Нельзя отменить уже обработанное предложение."},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )
        proposal.delete()
        return Response(
            {"detail": "Предложение отменено."}, status=drf_status.HTTP_204_NO_CONTENT
        )


class SignUpView(CreateView):
    form_class = CustomUserRegistrationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

    def form_valid(self, form):
        # user = form.save() # Метод save в CustomUserRegistrationForm уже обрабатывает сохранение
        super().form_valid(
            form
        )  # Вызываем родительский form_valid, который вызовет form.save()
        messages.success(
            self.request, "Регистрация прошла успешно! Пожалуйста, войдите."
        )
        # Редирект на success_url будет выполнен автоматически из CreateView
        return redirect(self.get_success_url())  # Явный редирект после сообщения
