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
from app_cicatrizando.models import Provider, Patient, WoundsUser


class AuthenticationFlowTests(APITestCase):
	@patch("app_cicatrizando.views.firebase_get_user_data")
	def test_firebase_login_creates_patient_and_me_works(self, mock_firebase_get_user_data):
		mock_firebase_get_user_data.return_value = {
			"email": "firebase.patient@example.com",
			"given_name": "Firebase",
			"family_name": "Patient",
			"sub": "firebase-sub-patient-001",
		}

		login_response = self.client.post(
			"/auth/login/firebase/",
			{
				"firebase_token": "firebase-id-token-patient",
			},
			format="json",
		)

		self.assertEqual(login_response.status_code, 200)
		self.assertEqual(login_response.data["full_name"], "Firebase Patient")
		self.assertEqual(login_response.data["email"], "firebase.patient@example.com")
		self.assertEqual(login_response.data["role"], "patient")
		self.assertIsNotNone(login_response.data["patient_data"])
		self.assertIsNone(login_response.data["provider_data"])
		self.assertTrue(login_response.data["profile_completion_required"])

		user = get_user_model().objects.get(email="firebase.patient@example.com")
		wounds_user = WoundsUser.objects.get(user=user)
		self.assertEqual(wounds_user.role, WoundsUser.Patient)

		access_token = login_response.data["access"]
		me_response = self.client.get(
			"/auth/me/",
			HTTP_AUTHORIZATION=f"Bearer {access_token}",
		)
		self.assertEqual(me_response.status_code, 200)
		self.assertTrue(me_response.data["authenticated"])
		self.assertEqual(me_response.data["email"], "firebase.patient@example.com")

	@patch("app_cicatrizando.views.firebase_get_user_data")
	def test_role_selection_sets_provider_and_requires_profile_completion(self, mock_firebase_get_user_data):
		mock_firebase_get_user_data.return_value = {
			"email": "firebase.provider@example.com",
			"given_name": "Firebase",
			"family_name": "Provider",
			"sub": "firebase-sub-provider-001",
		}

		login_response = self.client.post(
			"/auth/login/firebase/",
			{
				"firebase_token": "firebase-id-token-provider",
			},
			format="json",
		)

		self.assertEqual(login_response.status_code, 200)
		access_token = login_response.data["access"]
		role_response = self.client.post(
			"/auth/login/role/",
			{"role": WoundsUser.Provider},
			format="json",
			HTTP_AUTHORIZATION=f"Bearer {access_token}",
		)

		self.assertEqual(role_response.status_code, 200)
		self.assertEqual(role_response.data["role"], "provider")
		self.assertTrue(role_response.data["profile_completion_required"])

		user = get_user_model().objects.get(email="firebase.provider@example.com")
		wounds_user = WoundsUser.objects.get(user=user)
		self.assertFalse(Provider.objects.filter(wounds_user=user).exists())
		self.assertEqual(wounds_user.role, WoundsUser.Provider)

	def test_provider_profile_updates_wounds_user_optional_data(self):
		user = get_user_model().objects.create_user(
			username="complete.provider@example.com",
			email="complete.provider@example.com",
		)
		wounds_user = WoundsUser.objects.create(
			user=user,
			birth_date=date(1990, 1, 1),
			state="",
			city="",
			role=WoundsUser.Patient,
		)

		self.client.force_authenticate(user=user)
		role_response = self.client.post(
			"/auth/login/role/",
			{"role": WoundsUser.Provider},
			format="json",
		)
		self.assertEqual(role_response.status_code, 200)

		response = self.client.post(
			"/auth/login/provider/",
			{
				"wounds_user": {
					"state": "SP",
					"city": "São Paulo",
				},
				"provider": {
					"professional_id": 12345,
					"contact_email": "provider.extra@example.com",
					"contact_number": "11999999999",
				},
			},
			format="json",
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["role"], "provider")
		self.assertIsNotNone(response.data["provider"])
		self.assertIsNone(response.data["patient"])

		wounds_user.refresh_from_db()
		self.assertEqual(wounds_user.role, WoundsUser.Provider)
		self.assertEqual(wounds_user.state, "SP")
		self.assertEqual(wounds_user.city, "São Paulo")

		provider = Provider.objects.get(wounds_user=user)
		self.assertEqual(provider.Professional_ID, 12345)
		self.assertEqual(provider.contact_email, "provider.extra@example.com")
		self.assertEqual(provider.contact_number, "11999999999")

	def test_patient_profile_updates_patient_and_rejects_wrong_role(self):
		user = get_user_model().objects.create_user(
			username="complete.patient@example.com",
			email="complete.patient@example.com",
		)
		wounds_user = WoundsUser.objects.create(
			user=user,
			birth_date=date(1992, 2, 2),
			state="",
			city="",
			role=WoundsUser.Provider,
		)

		self.client.force_authenticate(user=user)

		invalid_response = self.client.post(
			"/auth/login/patient/",
			{
				"patient": {"contact_email": "x@example.com"},
			},
			format="json",
		)
		self.assertEqual(invalid_response.status_code, 400)

		role_response = self.client.post(
			"/auth/login/role/",
			{"role": WoundsUser.Patient},
			format="json",
		)
		self.assertEqual(role_response.status_code, 200)

		response = self.client.post(
			"/auth/login/patient/",
			{
				"wounds_user": {
					"state": "RJ",
					"city": "Rio de Janeiro",
				},
				"patient": {
					"contact_email": "patient.extra@example.com",
					"contact_number": "21988888888",
				},
			},
			format="json",
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["role"], "patient")
		self.assertIsNone(response.data["provider"])
		self.assertIsNotNone(response.data["patient"])

		wounds_user.refresh_from_db()
		self.assertEqual(wounds_user.role, WoundsUser.Patient)
		self.assertEqual(wounds_user.state, "RJ")
		self.assertEqual(wounds_user.city, "Rio de Janeiro")

		patient = Patient.objects.get(WoundsUser=user)
		self.assertEqual(patient.contact_email, "patient.extra@example.com")
		self.assertEqual(patient.contact_numer, "21988888888")
