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
from datetime import date

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from app_cicatrizando.models import Provider, WoundsUser


class AuthenticationFlowTests(APITestCase):
	@patch("app_cicatrizando.views.google_get_user_data")
	def test_google_login_creates_patient_profile_and_me_works(self, mock_google_get_user_data):
		mock_google_get_user_data.return_value = {
			"email": "teste.auth@example.com",
			"given_name": "Teste",
			"family_name": "Auth",
			"sub": "google-sub-123",
		}

		login_response = self.client.post(
			"/auth/login/google/",
			{
				"token": "google-id-token-fake",
				"role": WoundsUser.Patient,
				"birth_date": "1995-05-20",
			},
			format="json",
		)

		self.assertEqual(login_response.status_code, 200)
		self.assertIn("access", login_response.data)
		self.assertIn("refresh", login_response.data)
		self.assertEqual(login_response.data["role"], "patient")
		self.assertIsNotNone(login_response.data["patient_data"])
		self.assertIsNone(login_response.data["provider_data"])

		user = get_user_model().objects.get(email="teste.auth@example.com")
		wounds_user = WoundsUser.objects.get(user=user)
		self.assertEqual(wounds_user.name, "Teste Auth")
		self.assertEqual(wounds_user.email, "teste.auth@example.com")
		self.assertEqual(wounds_user.birth_date.isoformat(), "1995-05-20")
		self.assertEqual(wounds_user.role, WoundsUser.Patient)

		access_token = login_response.data["access"]
		me_response = self.client.get(
			"/auth/me/",
			HTTP_AUTHORIZATION=f"Bearer {access_token}",
		)
		self.assertEqual(me_response.status_code, 200)
		self.assertTrue(me_response.data["authenticated"])
		self.assertEqual(me_response.data["email"], "teste.auth@example.com")

	@patch("app_cicatrizando.views.google_get_user_data")
	def test_google_login_creates_provider_when_role_is_pr(self, mock_google_get_user_data):
		mock_google_get_user_data.return_value = {
			"email": "teste.provider@example.com",
			"given_name": "Provider",
			"family_name": "Test",
			"sub": "google-sub-provider-123",
		}

		login_response = self.client.post(
			"/auth/login/google/",
			{
				"token": "google-id-token-provider",
				"role": WoundsUser.Provider,
				"birth_date": "1988-12-01",
			},
			format="json",
		)

		self.assertEqual(login_response.status_code, 200)
		self.assertEqual(login_response.data["role"], "provider")
		self.assertIsNotNone(login_response.data["provider_data"])
		self.assertIsNone(login_response.data["patient_data"])

		user = get_user_model().objects.get(email="teste.provider@example.com")
		wounds_user = WoundsUser.objects.get(user=user)
		provider = Provider.objects.get(wounds_user=wounds_user)

		self.assertEqual(provider.pk, wounds_user.pk)
		self.assertEqual(login_response.data["provider_data"]["provider_id"], provider.pk)
		self.assertEqual(login_response.data["provider_data"]["provider_name"], wounds_user.name)

	@patch("app_cicatrizando.views.google_get_user_data")
	def test_google_login_updates_existing_wounds_user_fields(self, mock_google_get_user_data):
		user = get_user_model().objects.create_user(
			username="existente@example.com",
			email="existente@example.com",
		)
		wounds_user = WoundsUser.objects.create(
			user=user,
			name="Nome Antigo",
			email="antigo@example.com",
			birth_date=date(2000, 1, 1),
			role=WoundsUser.Patient,
		)

		mock_google_get_user_data.return_value = {
			"email": "existente@example.com",
			"given_name": "Nome",
			"family_name": "Novo",
			"sub": "google-sub-existing",
		}

		login_response = self.client.post(
			"/auth/login/google/",
			{
				"token": "google-id-token-existing",
				"role": WoundsUser.Provider,
				"birth_date": "1999-02-03",
			},
			format="json",
		)

		self.assertEqual(login_response.status_code, 200)
		self.assertEqual(login_response.data["role"], "provider")

		wounds_user.refresh_from_db()
		self.assertEqual(wounds_user.name, "Nome Novo")
		self.assertEqual(wounds_user.email, "existente@example.com")
		self.assertEqual(wounds_user.birth_date.isoformat(), "1999-02-03")
		self.assertEqual(wounds_user.role, WoundsUser.Provider)
		self.assertTrue(Provider.objects.filter(wounds_user=wounds_user).exists())
