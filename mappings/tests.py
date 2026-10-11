from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from doctors.models import Doctor
from patients.models import Patient

from .models import PatientDoctorMapping

User = get_user_model()

LIST_URL = "/api/mappings/"


def detail_url(pk):
    return f"/api/mappings/{pk}/"


class MappingAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("u1@example.com", "u1@example.com", "pass-12345-xyz")
        self.other = User.objects.create_user("u2@example.com", "u2@example.com", "pass-12345-xyz")
        self.patient = Patient.objects.create(created_by=self.user, name="P1", age=30, gender="male")
        self.other_patient = Patient.objects.create(created_by=self.other, name="P2", age=31, gender="female")
        self.doctor1 = Doctor.objects.create(name="D1", specialization="Cardiology", email="d1@example.com")
        self.doctor2 = Doctor.objects.create(name="D2", specialization="Neurology", email="d2@example.com")
        self.client.force_authenticate(self.user)

    # --- create -----------------------------------------------------------
    def test_assign_doctor_to_patient(self):
        response = self.client.post(
            LIST_URL, {"patient": self.patient.pk, "doctor": self.doctor1.pk}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["patient"], self.patient.pk)
        self.assertEqual(response.data["doctor"], self.doctor1.pk)
        self.assertEqual(PatientDoctorMapping.objects.count(), 1)

    def test_assign_requires_authentication(self):
        self.client.force_authenticate(None)
        response = self.client.post(
            LIST_URL, {"patient": self.patient.pk, "doctor": self.doctor1.pk}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_assign_missing_fields(self):
        response = self.client.post(LIST_URL, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("patient", response.data)
        self.assertIn("doctor", response.data)

    def test_assign_nonexistent_patient(self):
        response = self.client.post(LIST_URL, {"patient": 9999, "doctor": self.doctor1.pk}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("patient", response.data)

    def test_assign_nonexistent_doctor(self):
        response = self.client.post(LIST_URL, {"patient": self.patient.pk, "doctor": 9999}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("doctor", response.data)

    def test_assign_invalid_reference_type(self):
        response = self.client.post(LIST_URL, {"patient": "abc", "doctor": "xyz"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assign_duplicate_rejected(self):
        PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor1)
        response = self.client.post(
            LIST_URL, {"patient": self.patient.pk, "doctor": self.doctor1.pk}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(PatientDoctorMapping.objects.count(), 1)

    def test_assign_to_other_users_patient_forbidden(self):
        response = self.client.post(
            LIST_URL, {"patient": self.other_patient.pk, "doctor": self.doctor1.pk}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(PatientDoctorMapping.objects.count(), 0)

    # --- list -------------------------------------------------------------
    def test_list_mappings_only_for_own_patients(self):
        mine = PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor1)
        PatientDoctorMapping.objects.create(patient=self.other_patient, doctor=self.doctor1)
        response = self.client.get(LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([m["id"] for m in response.data], [mine.pk])

    def test_list_requires_authentication(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(LIST_URL).status_code, status.HTTP_401_UNAUTHORIZED)

    # --- doctors of a patient (GET /api/mappings/<patient_id>/) ------------
    def test_get_doctors_for_patient(self):
        m1 = PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor1)
        m2 = PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor2)
        response = self.client.get(detail_url(self.patient.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([m["id"] for m in response.data], [m1.pk, m2.pk])
        self.assertEqual(response.data[0]["doctor"]["name"], "D1")
        self.assertEqual(response.data[1]["doctor"]["specialization"], "Neurology")

    def test_get_doctors_for_patient_without_doctors(self):
        response = self.client.get(detail_url(self.patient.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_get_doctors_for_nonexistent_patient(self):
        self.assertEqual(self.client.get(detail_url(9999)).status_code, status.HTTP_404_NOT_FOUND)

    def test_get_doctors_for_other_users_patient_forbidden(self):
        PatientDoctorMapping.objects.create(patient=self.other_patient, doctor=self.doctor1)
        response = self.client.get(detail_url(self.other_patient.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_doctors_for_patient_requires_authentication(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(detail_url(self.patient.pk)).status_code, status.HTTP_401_UNAUTHORIZED)

    # --- delete -----------------------------------------------------------
    def test_remove_mapping(self):
        mapping = PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor1)
        response = self.client.delete(detail_url(mapping.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(PatientDoctorMapping.objects.filter(pk=mapping.pk).exists())
        # The patient and doctor themselves are untouched.
        self.assertTrue(Patient.objects.filter(pk=self.patient.pk).exists())
        self.assertTrue(Doctor.objects.filter(pk=self.doctor1.pk).exists())

    def test_remove_nonexistent_mapping(self):
        self.assertEqual(self.client.delete(detail_url(9999)).status_code, status.HTTP_404_NOT_FOUND)

    def test_remove_other_users_mapping_forbidden(self):
        mapping = PatientDoctorMapping.objects.create(patient=self.other_patient, doctor=self.doctor1)
        self.assertEqual(self.client.delete(detail_url(mapping.pk)).status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(PatientDoctorMapping.objects.filter(pk=mapping.pk).exists())

    def test_remove_requires_authentication(self):
        mapping = PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor1)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.delete(detail_url(mapping.pk)).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(PatientDoctorMapping.objects.filter(pk=mapping.pk).exists())

    def test_put_and_patch_not_allowed_on_mapping(self):
        mapping = PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor1)
        self.assertEqual(self.client.put(detail_url(mapping.pk), {}, format="json").status_code, 405)
        self.assertEqual(self.client.patch(detail_url(mapping.pk), {}, format="json").status_code, 405)

    # --- cascade behaviour --------------------------------------------------
    def test_deleting_patient_removes_its_mappings(self):
        PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor1)
        self.client.delete(f"/api/patients/{self.patient.pk}/")
        self.assertEqual(PatientDoctorMapping.objects.count(), 0)

    def test_deleting_doctor_removes_its_mappings(self):
        PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor1)
        self.client.delete(f"/api/doctors/{self.doctor1.pk}/")
        self.assertEqual(PatientDoctorMapping.objects.count(), 0)
