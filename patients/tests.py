from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Patient

User = get_user_model()

LIST_URL = "/api/patients/"


def detail_url(pk):
    return f"/api/patients/{pk}/"


def patient_payload(**overrides):
    payload = {"name": "John Doe", "age": 40, "gender": "male", "address": "12 Main Street"}
    payload.update(overrides)
    return payload


class PatientAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("owner@example.com", "owner@example.com", "pass-12345-xyz")
        self.other = User.objects.create_user("other@example.com", "other@example.com", "pass-12345-xyz")
        self.client.force_authenticate(self.user)

    # --- create -----------------------------------------------------------
    def test_create_patient(self):
        response = self.client.post(LIST_URL, patient_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        patient = Patient.objects.get(pk=response.data["id"])
        self.assertEqual(patient.created_by, self.user)
        self.assertEqual(response.data["name"], "John Doe")

    def test_create_ignores_client_supplied_owner(self):
        response = self.client.post(
            LIST_URL, patient_payload(created_by=self.other.id), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Patient.objects.get(pk=response.data["id"]).created_by, self.user)

    def test_create_requires_authentication(self):
        self.client.force_authenticate(None)
        response = self.client.post(LIST_URL, patient_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_missing_required_fields(self):
        response = self.client.post(LIST_URL, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for field in ("name", "age", "gender"):
            self.assertIn(field, response.data)

    def test_create_invalid_values(self):
        response = self.client.post(
            LIST_URL, patient_payload(age=-5, gender="robot"), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("age", response.data)
        self.assertIn("gender", response.data)

    # --- list -------------------------------------------------------------
    def test_list_returns_only_own_patients(self):
        Patient.objects.create(created_by=self.user, **patient_payload(name="Mine 1"))
        Patient.objects.create(created_by=self.user, **patient_payload(name="Mine 2"))
        Patient.objects.create(created_by=self.other, **patient_payload(name="Theirs"))
        response = self.client.get(LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([p["name"] for p in response.data], ["Mine 1", "Mine 2"])

    def test_list_requires_authentication(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(LIST_URL).status_code, status.HTTP_401_UNAUTHORIZED)

    # --- retrieve ---------------------------------------------------------
    def test_retrieve_patient(self):
        patient = Patient.objects.create(created_by=self.user, **patient_payload())
        response = self.client.get(detail_url(patient.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], patient.pk)

    def test_retrieve_nonexistent_patient(self):
        self.assertEqual(self.client.get(detail_url(9999)).status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_other_users_patient_forbidden(self):
        patient = Patient.objects.create(created_by=self.other, **patient_payload())
        self.assertEqual(self.client.get(detail_url(patient.pk)).status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_requires_authentication(self):
        patient = Patient.objects.create(created_by=self.user, **patient_payload())
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(detail_url(patient.pk)).status_code, status.HTTP_401_UNAUTHORIZED)

    # --- update -----------------------------------------------------------
    def test_update_patient(self):
        patient = Patient.objects.create(created_by=self.user, **patient_payload())
        response = self.client.put(
            detail_url(patient.pk), patient_payload(name="Jane Doe", age=41), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        patient.refresh_from_db()
        self.assertEqual((patient.name, patient.age), ("Jane Doe", 41))
        self.assertEqual(patient.created_by, self.user)

    def test_update_invalid_data(self):
        patient = Patient.objects.create(created_by=self.user, **patient_payload())
        response = self.client.put(detail_url(patient.pk), {"name": ""}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_other_users_patient_forbidden(self):
        patient = Patient.objects.create(created_by=self.other, **patient_payload())
        response = self.client.put(detail_url(patient.pk), patient_payload(name="Hacked"), format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        patient.refresh_from_db()
        self.assertEqual(patient.name, "John Doe")

    def test_update_nonexistent_patient(self):
        response = self.client.put(detail_url(9999), patient_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_is_not_allowed(self):
        patient = Patient.objects.create(created_by=self.user, **patient_payload())
        response = self.client.patch(detail_url(patient.pk), {"name": "X"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # --- delete -----------------------------------------------------------
    def test_delete_patient(self):
        patient = Patient.objects.create(created_by=self.user, **patient_payload())
        response = self.client.delete(detail_url(patient.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Patient.objects.filter(pk=patient.pk).exists())

    def test_delete_other_users_patient_forbidden(self):
        patient = Patient.objects.create(created_by=self.other, **patient_payload())
        self.assertEqual(self.client.delete(detail_url(patient.pk)).status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Patient.objects.filter(pk=patient.pk).exists())

    def test_delete_nonexistent_patient(self):
        self.assertEqual(self.client.delete(detail_url(9999)).status_code, status.HTTP_404_NOT_FOUND)
