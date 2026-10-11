from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from doctors.serializers import DoctorSerializer

from .models import PatientDoctorMapping


class MappingSerializer(serializers.ModelSerializer):
    """Used to create and list mappings (patient and doctor given as IDs)."""

    class Meta:
        model = PatientDoctorMapping
        fields = ["id", "patient", "doctor"]
        read_only_fields = ["id"]
        # Duplicate (patient, doctor) pairs are rejected with a 400 by the
        # UniqueTogetherValidator DRF derives from the model's UniqueConstraint.

    def validate_patient(self, patient):
        # Users may only assign doctors to patients they created.
        if patient.created_by_id != self.context["request"].user.id:
            raise PermissionDenied("You do not have permission to access this patient.")
        return patient


class PatientDoctorSerializer(serializers.ModelSerializer):
    """Mapping with the full doctor details (used for a patient's doctors)."""

    doctor = DoctorSerializer(read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = ["id", "patient", "doctor"]
