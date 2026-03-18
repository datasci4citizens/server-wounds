"""
Como rodar os testes deste app:

1) Rodar todos os testes do Django (dentro do container web):
	docker compose --env-file .env -f docker/docker-compose.yml exec -T web \
	python citizens_project/manage.py test

2) Rodar uma classe específica de testes:
	docker compose --env-file .env -f docker/docker-compose.yml exec -T web \
	python citizens_project/manage.py test app_cicatrizando.tests.[Classname]

Observação:
- Execute os comandos a partir da pasta server-wounds/.
"""



from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from app_cicatrizando.models import ProviderNonClinicalInfos
from app_cicatrizando.omop.omop_models import Provider


class AuthenticationFlowTests(APITestCase):
	@patch("app_cicatrizando.views.google_get_user_data")
	def test_google_login_generates_jwt_and_authenticates_me_endpoint(self, mock_google_get_user_data):
		mock_google_get_user_data.return_value = {
			"email": "teste.auth@example.com",
			"given_name": "Teste",
			"family_name": "Auth",
			"sub": "google-sub-123",
		}

		login_response = self.client.post(
			"/api/auth/login/google/",
			{"token": "google-id-token-fake"},
			format="json",
		)

		self.assertEqual(login_response.status_code, 200)
		self.assertIn("access", login_response.data)
		self.assertIn("refresh", login_response.data)

		access_token = login_response.data["access"]
		me_response = self.client.get(
			"/api/auth/me/",
			HTTP_AUTHORIZATION=f"Bearer {access_token}",
		)

		self.assertEqual(me_response.status_code, 200)
		self.assertTrue(me_response.data["authenticated"])
		self.assertEqual(me_response.data["email"], "teste.auth@example.com")

		user_exists = get_user_model().objects.filter(
			email="teste.auth@example.com"
		).exists()
		self.assertTrue(user_exists)

	@patch("app_cicatrizando.views.google_get_user_data")
	def test_google_login_returns_provider_role_when_provider_profile_exists(self, mock_google_get_user_data):
		user = get_user_model().objects.create_user(
			username="teste.provider@example.com",
			email="teste.provider@example.com",
		)
		provider = Provider.objects.create(provider_name="Dr. Provider Test")
		ProviderNonClinicalInfos.objects.create(
			provider=provider,
			user=user,
			name="Dr. Provider Test",
		)

		mock_google_get_user_data.return_value = {
			"email": "teste.provider@example.com",
			"given_name": "Provider",
			"family_name": "Test",
			"sub": "google-sub-provider-123",
		}

		login_response = self.client.post(
			"/api/auth/login/google/",
			{"token": "google-id-token-provider"},
			format="json",
		)

		self.assertEqual(login_response.status_code, 200)
		self.assertEqual(login_response.data["role"], "provider")
		self.assertIsNotNone(login_response.data["provider_data"])
		self.assertEqual(login_response.data["provider_data"]["provider_id"], provider.provider_id)
