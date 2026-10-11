from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from patients.models import Patient
from patients.permissions import IsPatientOwner

from .models import PatientDoctorMapping
from .permissions import IsMappingPatientOwner
from .serializers import MappingSerializer, PatientDoctorSerializer


class MappingListCreateView(generics.ListCreateAPIView):
    """POST /api/mappings/ (assign) and GET /api/mappings/ (list).

    The list contains the mappings of the authenticated user's patients.
    """

    serializer_class = MappingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PatientDoctorMapping.objects.filter(patient__created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            # Race condition on the unique (patient, doctor) constraint.
            return Response(
                {"non_field_errors": ["This doctor is already assigned to this patient."]},
                status=status.HTTP_400_BAD_REQUEST,
            )


class MappingDetailView(APIView):
    """GET /api/mappings/<patient_id>/ and DELETE /api/mappings/<id>/.

    The same URL shape serves two purposes, as specified by the assignment:
    GET treats the value as a patient ID, DELETE treats it as a mapping ID.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk)
        if not IsPatientOwner().has_object_permission(request, self, patient):
            raise PermissionDenied(IsPatientOwner.message)
        mappings = (
            PatientDoctorMapping.objects.filter(patient=patient)
            .select_related("doctor")
            .order_by("id")
        )
        return Response(PatientDoctorSerializer(mappings, many=True).data)

    def delete(self, request, pk):
        mapping = get_object_or_404(
            PatientDoctorMapping.objects.select_related("patient"), pk=pk
        )
        permission = IsMappingPatientOwner()
        if not permission.has_object_permission(request, self, mapping):
            raise PermissionDenied(permission.message)
        mapping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
