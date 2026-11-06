from django.conf import settings
from django.db import models
from django.db.models import Avg


class Specialite(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom


class Medecin(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="medecin")
    specialite = models.ForeignKey(Specialite, on_delete=models.PROTECT)
    bio = models.TextField(blank=True)
    tarif = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def __str__(self):
        return f"Dr {self.user.get_full_name()}"

    def moyenne(self):
        m = Avis.objects.filter(rdv__medecin=self).aggregate(m=Avg("note"))["m"]
        return round(m, 1) if m else None

    def nb_avis(self):
        return Avis.objects.filter(rdv__medecin=self).count()


class Disponibilite(models.Model):
    JOURS = [(0, "Lundi"), (1, "Mardi"), (2, "Mercredi"), (3, "Jeudi"),
             (4, "Vendredi"), (5, "Samedi"), (6, "Dimanche")]
    medecin = models.ForeignKey(Medecin, on_delete=models.CASCADE, related_name="dispos")
    jour = models.PositiveSmallIntegerField(choices=JOURS)
    debut = models.TimeField()
    fin = models.TimeField()

    class Meta:
        ordering = ["jour", "debut"]


class RendezVous(models.Model):
    class Statut(models.TextChoices):
        ATTENTE = "attente", "En attente"
        CONFIRME = "confirme", "Confirmé"
        ANNULE = "annule", "Annulé"
        TERMINE = "termine", "Terminé"

    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rdvs")
    medecin = models.ForeignKey(Medecin, on_delete=models.CASCADE, related_name="rdvs")
    date = models.DateField()
    heure = models.TimeField()
    motif = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    statut = models.CharField(max_length=10, choices=Statut.choices, default=Statut.ATTENTE)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "heure"]


class Indisponibilite(models.Model):
    """Congés ou jours où le médecin ne reçoit pas."""
    medecin = models.ForeignKey(Medecin, on_delete=models.CASCADE, related_name="conges")
    debut = models.DateField()
    fin = models.DateField()
    motif = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["debut"]


class Avis(models.Model):
    rdv = models.OneToOneField(RendezVous, on_delete=models.CASCADE, related_name="avis")
    note = models.PositiveSmallIntegerField(choices=[(i, "★" * i) for i in range(1, 6)])
    commentaire = models.TextField(blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)
