from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models


class Patient(models.Model):
    class Gender(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
        OTHER = "other", "Other"

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patients",
    )
    name = models.CharField(max_length=255)
    age = models.PositiveIntegerField(validators=[MaxValueValidator(150)])
    gender = models.CharField(max_length=10, choices=Gender.choices)
    address = models.TextField(blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name
