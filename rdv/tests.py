from datetime import date, timedelta
from io import BytesIO
from django.test import TestCase
from django.urls import reverse
from openpyxl import load_workbook
from accounts.models import User
from .models import Specialite, Medecin, Disponibilite, RendezVous, Indisponibilite, Avis
from .utils import creneaux_libres


class FluxTests(TestCase):
    def setUp(self):
        spec = Specialite.objects.create(nom="Dentiste")
        u = User.objects.create_user("doc", password="x", first_name="Ali", last_name="Amrani", role="medecin")
        self.med = Medecin.objects.create(user=u, specialite=spec, tarif=200)
        self.jour = date.today() + timedelta(days=1)
        Disponibilite.objects.create(medecin=self.med, jour=self.jour.weekday(), debut="09:00", fin="10:00")
        self.pat = User.objects.create_user("pat", password="x", role="patient")
        self.adm = User.objects.create_superuser("adm", password="x")

    def reserver(self, heure="09:00"):
        self.client.force_login(self.pat)
        return self.client.post(reverse("prendre_rdv", args=[self.med.pk]) + f"?date={self.jour}", {"heure": heure})

    def test_reservation(self):
        self.reserver()
        self.assertEqual(RendezVous.objects.count(), 1)

    def test_creneau_deja_pris(self):
        self.reserver()
        self.reserver()
        self.assertEqual(RendezVous.objects.count(), 1)

    def test_patient_interdit_dans_administration(self):
        self.client.force_login(self.pat)
        self.assertEqual(self.client.get(reverse("tableau_admin")).status_code, 403)

    def test_medecin_ne_peut_pas_reserver(self):
        self.client.force_login(self.med.user)
        self.assertEqual(self.client.get(reverse("prendre_rdv", args=[self.med.pk])).status_code, 403)

    def test_avis_seulement_apres_consultation(self):
        self.reserver()
        rdv = RendezVous.objects.first()
        self.assertEqual(self.client.get(reverse("noter", args=[rdv.pk])).status_code, 404)
        rdv.statut = "termine"
        rdv.save()
        self.client.post(reverse("noter", args=[rdv.pk]), {"note": 5, "commentaire": "Parfait"})
        self.assertEqual(Avis.objects.count(), 1)
        self.assertEqual(self.med.moyenne(), 5.0)

    def test_report_de_rendez_vous(self):
        self.reserver("09:00")
        rdv = RendezVous.objects.first()
        self.client.post(reverse("reporter", args=[rdv.pk]) + f"?date={self.jour}", {"heure": "09:30"})
        rdv.refresh_from_db()
        self.assertEqual(rdv.heure.strftime("%H:%M"), "09:30")

    def test_conge_bloque_les_creneaux(self):
        Indisponibilite.objects.create(medecin=self.med, debut=self.jour, fin=self.jour)
        self.assertEqual(creneaux_libres(self.med, self.jour), [])

    def test_export_excel(self):
        self.reserver()
        self.client.force_login(self.adm)
        r = self.client.get(reverse("export_excel"))
        self.assertEqual(r.status_code, 200)
        wb = load_workbook(BytesIO(r.content))
        self.assertEqual(wb.sheetnames, ["Rendez-vous", "Résumé", "Médecins", "Patients"])
        self.assertEqual(wb["Rendez-vous"].max_row, 2)
