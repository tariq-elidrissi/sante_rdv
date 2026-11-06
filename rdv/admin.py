from django.contrib import admin
from .models import Specialite, Medecin, Disponibilite, RendezVous, Indisponibilite, Avis

for m in (Specialite, Medecin, Disponibilite, RendezVous, Indisponibilite, Avis):
    admin.site.register(m)
