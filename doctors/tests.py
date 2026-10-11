from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Doctor

User = get_user_model()

LIST_URL = "/api/doctors/"


def detail_url(pk):
    return f"/api/doctors/{pk}/"


def doctor_payload(**overrides):
    payload = {
        "name": "Dr. Gregory House",
        "specialization": "Diagnostics",
        "email": "house@example.com",
        "phone": "555-0100",
    }
    payload.update(overrides)
    return payload


class DoctorAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("u1@example.com", "u1@example.com", "pass-12345-xyz")
        self.other = User.objects.create_user("u2@example.com", "u2@example.com", "pass-12345-xyz")
        self.client.force_authenticate(self.user)

    def test_create_doctor(self):
        response = self.client.post(LIST_URL, doctor_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Doctor.objects.filter(pk=response.data["id"]).exists())

    def test_create_requires_authentication(self):
        self.client.force_authenticate(None)
        response = self.client.post(LIST_URL, doctor_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_missing_required_fields(self):
        response = self.client.post(LIST_URL, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for field in ("name", "specialization", "email"):
            self.assertIn(field, response.data)

    def test_create_invalid_email(self):
        response = self.client.post(LIST_URL, doctor_payload(email="bad"), format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_list_returns_all_doctors(self):
        Doctor.objects.create(**doctor_payload(name="A"))
        Doctor.objects.create(**doctor_payload(name="B"))
        # Doctors are shared: another authenticated user sees them as well.
        self.client.force_authenticate(self.other)
        response = self.client.get(LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([d["name"] for d in response.data], ["A", "B"])

    def test_list_requires_authentication(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(LIST_URL).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_doctor(self):
        doctor = Doctor.objects.create(**doctor_payload())
        response = self.client.get(detail_url(doctor.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["specialization"], "Diagnostics")

    def test_retrieve_nonexistent_doctor(self):
        self.assertEqual(self.client.get(detail_url(9999)).status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_requires_authentication(self):
        doctor = Doctor.objects.create(**doctor_payload())
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(detail_url(doctor.pk)).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_doctor(self):
        doctor = Doctor.objects.create(**doctor_payload())
        response = self.client.put(
            detail_url(doctor.pk), doctor_payload(specialization="Cardiology"), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        doctor.refresh_from_db()
        self.assertEqual(doctor.specialization, "Cardiology")

    def test_update_invalid_data(self):
        doctor = Doctor.objects.create(**doctor_payload())
        response = self.client.put(detail_url(doctor.pk), doctor_payload(name=""), format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_nonexistent_doctor(self):
        response = self.client.put(detail_url(9999), doctor_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_requires_authentication(self):
        doctor = Doctor.objects.create(**doctor_payload())
        self.client.force_authenticate(None)
        response = self.client.put(detail_url(doctor.pk), doctor_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_doctor(self):
        doctor = Doctor.objects.create(**doctor_payload())
        response = self.client.delete(detail_url(doctor.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Doctor.objects.filter(pk=doctor.pk).exists())

    def test_delete_nonexistent_doctor(self):
        self.assertEqual(self.client.delete(detail_url(9999)).status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_requires_authentication(self):
        doctor = Doctor.objects.create(**doctor_payload())
        self.client.force_authenticate(None)
        self.assertEqual(self.client.delete(detail_url(doctor.pk)).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Doctor.objects.filter(pk=doctor.pk).exists())

    def test_patch_is_not_allowed(self):
        doctor = Doctor.objects.create(**doctor_payload())
        response = self.client.patch(detail_url(doctor.pk), {"name": "X"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
