import pytest
from django.urls import reverse
from rest_framework import status
from apps.users.models import User
from apps.wallets.models import Wallet

@pytest.mark.django_db
class TestAuthentication:
    def test_user_registration_creates_wallet(self, client):
        url = reverse('register')
        data = {
            "email": "tester@example.com",
            "password": "SecurePassword123!",
            "first_name": "Tester"
        }
        response = client.post(url, data, content_type='application/json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email="tester@example.com").exists()
        
        user = User.objects.get(email="tester@example.com")
        assert Wallet.objects.filter(owner=user).exists()

    def test_login_returns_jwt_tokens(self, client, db):
        # Create user through service to ensure wallet exists
        from apps.users.services import IdentityService
        IdentityService.register_user(email="login@example.com", password="password123")
        
        url = reverse('login')
        data = {"email": "login@example.com", "password": "password123"}
        response = client.post(url, data, content_type='application/json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
