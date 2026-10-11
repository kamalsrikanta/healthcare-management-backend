from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Patient
from .permissions import IsPatientOwner
from .serializers import PatientSerializer


class PatientListCreateView(generics.ListCreateAPIView):
    """GET /api/patients/ (own patients only) and POST /api/patients/."""

    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Patient.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET / PUT / DELETE /api/patients/<id>/ (owner only)."""

    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsPatientOwner]
    http_method_names = ["get", "put", "delete", "head", "options"]
