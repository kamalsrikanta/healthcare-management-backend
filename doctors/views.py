from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Doctor
from .serializers import DoctorSerializer


class DoctorListCreateView(generics.ListCreateAPIView):
    """GET /api/doctors/ (all doctors) and POST /api/doctors/."""

    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]


class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET / PUT / DELETE /api/doctors/<id>/."""

    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "put", "delete", "head", "options"]
