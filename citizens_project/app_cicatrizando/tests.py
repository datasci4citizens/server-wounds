"""
How to run this app test suite:

1) Run all tests via quickstart:
	python quickstart.py test

2) Run a specific test class:
	python quickstart.py test [Classname]

3) Run a specific test method:
	python quickstart.py test [Classname].[method_name]

Note:
- Run these commands from the server-wounds/ directory.
- for more information on commands, check server-wounds/quickstart.py docstring 
"""

from unittest.mock import patch
from datetime import date
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework.exceptions import APIException
from app_cicatrizando.models import Provider, Patient, WoundsUser


class BaseAuthenticationFlowTests(APITestCase):
	firebase_login_url = "/auth/login/firebase/"
	role_selection_url = "/auth/login/role/"
	provider_profile_url = "/auth/login/provider/"
	patient_profile_url = "/auth/login/patient/"
	me_url = "/auth/me/"

	def _create_user_with_wounds_profile(self, *, email, role, birth_date):
		user = get_user_model().objects.create_user(username=email, email=email)
		wounds_user = WoundsUser.objects.create(
			user=user,
			birth_date=birth_date,
			state="",
			city="",
			role=role,
		)
		return user, wounds_user

	def _auth_headers(self, access_token):
		return {"HTTP_AUTHORIZATION": f"Bearer {access_token}"}


class AuthenticationErrorTests(BaseAuthenticationFlowTests):
	def test_me_requires_authentication(self):
		response = self.client.get(self.me_url)

		self.assertEqual(response.status_code, 401)

	def test_role_selection_requires_authentication(self):
		response = self.client.post(
			self.role_selection_url,
			{"role": WoundsUser.Provider},
			format="json",
		)

		self.assertEqual(response.status_code, 401)

	def test_firebase_login_requires_firebase_token(self):
		response = self.client.post(
			self.firebase_login_url,
			{},
			format="json",
		)

		self.assertEqual(response.status_code, 400)
		self.assertIn("firebase_token", response.data)

	@patch("app_cicatrizando.views.firebase_get_user_data")
	def test_firebase_login_fails_when_email_is_missing(self, mock_firebase_get_user_data):
		mock_firebase_get_user_data.side_effect = APIException("Firebase token does not contain email")

		response = self.client.post(
			self.firebase_login_url,
			{"firebase_token": "token-without-email"},
			format="json",
		)

		self.assertEqual(response.status_code, 500)

	def test_provider_profile_requires_professional_id(self):
		user, _ = self._create_user_with_wounds_profile(
			email="provider.missing.id@example.com",
			role=WoundsUser.Provider,
			birth_date=date(1991, 1, 1),
		)

		self.client.force_authenticate(user=user)
		response = self.client.post(
			self.provider_profile_url,
			{
				"provider": {
					"contact_email": "provider.extra@example.com",
					"contact_number": "11999999999",
				},
			},
			format="json",
		)

		self.assertEqual(response.status_code, 400)
		self.assertFalse(Provider.objects.filter(wounds_user=user).exists())


class AuthenticationFlowTests(BaseAuthenticationFlowTests):
	@patch("app_cicatrizando.views.firebase_get_user_data")
	def test_firebase_login_creates_patient_and_me_works(self, mock_firebase_get_user_data):
		mock_firebase_get_user_data.return_value = {
			"email": "firebase.patient@example.com",
			"given_name": "Firebase",
			"family_name": "Patient",
			"sub": "firebase-sub-patient-001",
		}

		login_response = self.client.post(
			self.firebase_login_url,
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
			self.me_url,
			**self._auth_headers(access_token),
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
			self.firebase_login_url,
			{
				"firebase_token": "firebase-id-token-provider",
			},
			format="json",
		)

		self.assertEqual(login_response.status_code, 200)
		access_token = login_response.data["access"]
		role_response = self.client.post(
			self.role_selection_url,
			{"role": WoundsUser.Provider},
			format="json",
			**self._auth_headers(access_token),
		)

		self.assertEqual(role_response.status_code, 200)
		self.assertEqual(role_response.data["role"], "provider")
		self.assertTrue(role_response.data["profile_completion_required"])

		user = get_user_model().objects.get(email="firebase.provider@example.com")
		wounds_user = WoundsUser.objects.get(user=user)
		self.assertFalse(Provider.objects.filter(wounds_user=user).exists())
		self.assertEqual(wounds_user.role, WoundsUser.Provider)

	def test_provider_profile_updates_wounds_user_optional_data(self):
		user, wounds_user = self._create_user_with_wounds_profile(
			email="complete.provider@example.com",
			role=WoundsUser.Patient,
			birth_date=date(1990, 1, 1),
		)

		self.client.force_authenticate(user=user)
		role_response = self.client.post(
			self.role_selection_url,
			{"role": WoundsUser.Provider},
			format="json",
		)
		self.assertEqual(role_response.status_code, 200)

		response = self.client.post(
			self.provider_profile_url,
			{
				"wounds_user": {
					"state": "SP",
					"city": "São Paulo",
				},
				"provider": {
					"professional_id": "12345",
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
		self.assertEqual(provider.Professional_ID, "12345")
		self.assertEqual(provider.contact_email, "provider.extra@example.com")
		self.assertEqual(provider.contact_number, "11999999999")

	def test_patient_profile_updates_patient_and_rejects_wrong_role(self):
		user, wounds_user = self._create_user_with_wounds_profile(
			email="complete.patient@example.com",
			role=WoundsUser.Provider,
			birth_date=date(1992, 2, 2),
		)

		self.client.force_authenticate(user=user)

		invalid_response = self.client.post(
			self.patient_profile_url,
			{
				"patient": {"contact_email": "x@example.com"},
			},
			format="json",
		)
		self.assertEqual(invalid_response.status_code, 400)

		role_response = self.client.post(
			self.role_selection_url,
			{"role": WoundsUser.Patient},
			format="json",
		)
		self.assertEqual(role_response.status_code, 200)

		response = self.client.post(
			self.patient_profile_url,
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
		self.assertEqual(patient.contact_number, "21988888888")