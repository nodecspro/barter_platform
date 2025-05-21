from django.test import TestCase
from ads.models import Ad
from django.contrib.auth import get_user_model


def test_ad_creation(db):
    User = get_user_model()
    user = User.objects.create_user(username="testuser", password="password")
    ad = Ad.objects.create(
        title="Test Ad",
        description="This is a test ad.",
        user=user,
        category="electronics",
        condition="new",
    )
    assert ad.title == "Test Ad"
    assert ad.user.username == "testuser"
    assert ad.category == "electronics"
    assert ad.condition == "new"


from django.urls import reverse


def test_ad_list_view(client, db):
    url = reverse("ads:ad_list")
    response = client.get(url)
    assert response.status_code == 200
    assert "ads/ad_list.html" in [t.name for t in response.templates]


def test_ad_detail_view(client, db):
    User = get_user_model()
    user = User.objects.create_user(username="testuser", password="password")
    ad = Ad.objects.create(
        title="Test Ad",
        description="This is a test ad.",
        user=user,
        category="electronics",
        condition="new",
    )
    url = reverse("ads:ad_detail", kwargs={"pk": ad.pk})
    response = client.get(url)
    assert response.status_code == 200
    assert "ads/ad_detail.html" in [t.name for t in response.templates]
    assert ad.title.encode() in response.content


def test_ad_create_view_get(client, db):
    User = get_user_model()
    user = User.objects.create_user(username="testuser", password="password")
    client.login(username="testuser", password="password")

    url = reverse("ads:ad_create")
    response = client.get(url)
    assert response.status_code == 200
    assert "ads/ad_form.html" in [t.name for t in response.templates]


from ads.models import ExchangeProposal


def test_exchange_proposal_creation(db):
    User = get_user_model()
    user1 = User.objects.create_user(username="user1", password="password1")
    user2 = User.objects.create_user(username="user2", password="password2")

    ad1 = Ad.objects.create(
        title="Ad 1",
        description="Description 1",
        user=user1,
        category="electronics",
        condition="new",
    )
    ad2 = Ad.objects.create(
        title="Ad 2",
        description="Description 2",
        user=user2,
        category="books",
        condition="used",
    )

    proposal = ExchangeProposal.objects.create(
        proposer=user1, ad_sender=ad1, ad_receiver=ad2, comment="Let's exchange!"
    )

    assert proposal.proposer == user1
    assert proposal.ad_sender == ad1
    assert proposal.ad_receiver == ad2
    assert proposal.comment == "Let's exchange!"
    assert proposal.status == "pending"
