from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

REGISTER_URL = "/api/auth/register/"
LOGIN_URL = "/api/auth/login/"
VALID_PASSWORD = "StrongPass#2024"


def valid_payload(**overrides):
    payload = {"name": "Alice Smith", "email": "alice@example.com", "password": VALID_PASSWORD}
    payload.update(overrides)
    return payload


class RegisterTests(APITestCase):
    def test_register_success(self):
        response = self.client.post(REGISTER_URL, valid_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], "alice@example.com")
        self.assertEqual(response.data["name"], "Alice Smith")
        self.assertNotIn("password", response.data)

    def test_password_is_hashed(self):
        self.client.post(REGISTER_URL, valid_payload(), format="json")
        user = User.objects.get(email="alice@example.com")
        self.assertNotEqual(user.password, VALID_PASSWORD)
        self.assertTrue(user.check_password(VALID_PASSWORD))

    def test_missing_fields(self):
        for field in ("name", "email", "password"):
            payload = valid_payload()
            payload.pop(field)
            response = self.client.post(REGISTER_URL, payload, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, field)
            self.assertIn(field, response.data)

    def test_invalid_email(self):
        response = self.client.post(REGISTER_URL, valid_payload(email="not-an-email"), format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_weak_password_rejected(self):
        response = self.client.post(REGISTER_URL, valid_payload(password="123"), format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_email_rejected(self):
        self.client.post(REGISTER_URL, valid_payload(), format="json")
        response = self.client.post(REGISTER_URL, valid_payload(name="Other"), format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(User.objects.count(), 1)

    def test_duplicate_email_is_case_insensitive(self):
        self.client.post(REGISTER_URL, valid_payload(), format="json")
        response = self.client.post(
            REGISTER_URL, valid_payload(email="ALICE@Example.com"), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

    def test_register_with_invalid_token_header_still_works(self):
        response = self.client.post(
            REGISTER_URL, valid_payload(), format="json", HTTP_AUTHORIZATION="Bearer garbage"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class LoginTests(APITestCase):
    def setUp(self):
        self.client.post(REGISTER_URL, valid_payload(), format="json")

    def test_login_success_returns_jwt_tokens(self):
        response = self.client.post(
            LOGIN_URL, {"email": "alice@example.com", "password": VALID_PASSWORD}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertNotIn("password", response.data)

    def test_login_email_is_case_insensitive(self):
        response = self.client.post(
            LOGIN_URL, {"email": "ALICE@example.com", "password": VALID_PASSWORD}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_wrong_password(self):
        response = self.client.post(
            LOGIN_URL, {"email": "alice@example.com", "password": "wrong-password"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access", response.data)

    def test_login_unknown_email(self):
        response = self.client.post(
            LOGIN_URL, {"email": "nobody@example.com", "password": VALID_PASSWORD}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_fields(self):
        response = self.client.post(LOGIN_URL, {"email": "alice@example.com"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.post(LOGIN_URL, {"password": VALID_PASSWORD}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class JWTAuthenticationTests(APITestCase):
    """End-to-end check that a SimpleJWT access token authorises requests."""

    def setUp(self):
        self.client.post(REGISTER_URL, valid_payload(), format="json")
        login = self.client.post(
            LOGIN_URL, {"email": "alice@example.com", "password": VALID_PASSWORD}, format="json"
        )
        self.access = login.data["access"]

    def test_valid_token_grants_access(self):
        response = self.client.get(
            "/api/patients/", HTTP_AUTHORIZATION=f"Bearer {self.access}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_missing_token_is_rejected(self):
        response = self.client.get("/api/patients/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_token_is_rejected(self):
        response = self.client.get("/api/patients/", HTTP_AUTHORIZATION="Bearer not.a.token")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
