from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        PATIENT = "patient", "Patient"
        MEDECIN = "medecin", "Médecin"
        ADMIN = "admin", "Administrateur"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.PATIENT)
    telephone = models.CharField(max_length=20, blank=True)

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)
