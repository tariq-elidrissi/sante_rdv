from datetime import date, datetime, timedelta
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from accounts.decorators import role_required
from .exports import classeur, reponse
from .forms import DisponibiliteForm, MedecinCreationForm, IndisponibiliteForm, AvisForm
from .models import Specialite, Medecin, Disponibilite, RendezVous, Indisponibilite
from .notifications import prevenir
from .utils import creneaux_libres

User = get_user_model()


def _jour(request):
    try:
        j = date.fromisoformat(request.GET.get("date", ""))
    except ValueError:
        j = date.today()
    return max(j, date.today())


def _heure(request):
    try:
        return datetime.strptime(request.POST.get("heure", ""), "%H:%M").time()
    except ValueError:
        return None


def _txt(rdv):
    return f"{rdv.date:%d/%m/%Y} à {rdv.heure:%H:%M} avec {rdv.medecin}"


def accueil(request):
    return render(request, "home.html", {"specialites": Specialite.objects.all()[:8]})


def medecins(request):
    qs = Medecin.objects.select_related("user", "specialite")
    if request.GET.get("specialite"):
        qs = qs.filter(specialite_id=request.GET["specialite"])
    if request.GET.get("q"):
        qs = qs.filter(user__last_name__icontains=request.GET["q"])
    return render(request, "medecins.html", {"medecins": qs, "specialites": Specialite.objects.all()})


# ---------- Patient ----------
@role_required("patient")
def prendre_rdv(request, pk):
    medecin = get_object_or_404(Medecin, pk=pk)
    jour = _jour(request)
    creneaux = creneaux_libres(medecin, jour)
    if request.method == "POST":
        heure = _heure(request)
        if heure in creneaux:
            rdv = RendezVous.objects.create(patient=request.user, medecin=medecin, date=jour,
                                            heure=heure, motif=request.POST.get("motif", ""))
            prevenir(request.user, "Demande reçue", f"Votre demande de rendez-vous {_txt(rdv)} est en attente de confirmation.")
            prevenir(medecin.user, "Nouvelle demande", f"{request.user.get_full_name()} demande un rendez-vous le {rdv.date:%d/%m/%Y} à {rdv.heure:%H:%M}.")
            messages.success(request, "Demande envoyée, en attente de confirmation.")
            return redirect("mes_rdv")
        messages.error(request, "Ce créneau n'est plus disponible.")
    return render(request, "prendre_rdv.html", {"medecin": medecin, "jour": jour,
                  "creneaux": creneaux, "today": date.today()})


@role_required("patient")
def reporter(request, pk):
    rdv = get_object_or_404(RendezVous, pk=pk, patient=request.user, statut__in=["attente", "confirme"])
    jour = _jour(request)
    creneaux = creneaux_libres(rdv.medecin, jour)
    if request.method == "POST":
        heure = _heure(request)
        if heure in creneaux:
            rdv.date, rdv.heure, rdv.statut = jour, heure, "attente"
            rdv.save()
            prevenir(request.user, "Rendez-vous reporté", f"Votre rendez-vous est reporté : {_txt(rdv)} (en attente de confirmation).")
            prevenir(rdv.medecin.user, "Rendez-vous reporté", f"{request.user.get_full_name()} a reporté son rendez-vous au {rdv.date:%d/%m/%Y} à {rdv.heure:%H:%M}.")
            messages.success(request, "Rendez-vous reporté, en attente de confirmation.")
            return redirect("mes_rdv")
        messages.error(request, "Ce créneau n'est plus disponible.")
    return render(request, "prendre_rdv.html", {"medecin": rdv.medecin, "jour": jour, "creneaux": creneaux,
                  "today": date.today(), "rdv": rdv})


@role_required("patient")
def mes_rdv(request):
    rdvs = request.user.rdvs.select_related("medecin__user", "medecin__specialite", "avis")
    statut = request.GET.get("statut")
    if statut:
        rdvs = rdvs.filter(statut=statut)
    return render(request, "mes_rdv.html", {"rdvs": rdvs, "statut": statut,
                                            "statuts": RendezVous.Statut.choices})


@require_POST
@role_required("patient")
def annuler(request, pk):
    rdv = get_object_or_404(RendezVous, pk=pk, patient=request.user)
    if rdv.statut in ("attente", "confirme"):
        rdv.statut = "annule"
        rdv.save()
        prevenir(rdv.medecin.user, "Rendez-vous annulé", f"{request.user.get_full_name()} a annulé le rendez-vous du {rdv.date:%d/%m/%Y} à {rdv.heure:%H:%M}.")
        messages.success(request, "Rendez-vous annulé.")
    return redirect("mes_rdv")


@role_required("patient")
def noter(request, pk):
    rdv = get_object_or_404(RendezVous, pk=pk, patient=request.user, statut="termine")
    if hasattr(rdv, "avis"):
        messages.info(request, "Vous avez déjà noté ce rendez-vous.")
        return redirect("mes_rdv")
    form = AvisForm(request.POST or None)
    if form.is_valid():
        avis = form.save(commit=False)
        avis.rdv = rdv
        avis.save()
        messages.success(request, "Merci pour votre avis !")
        return redirect("mes_rdv")
    return render(request, "form.html", {"form": form, "titre": f"Noter {rdv.medecin}"})


# ---------- Médecin ----------
@role_required("medecin")
def tableau_medecin(request):
    m = request.user.medecin
    rdvs = m.rdvs.select_related("patient")
    stats = {"attente": rdvs.filter(statut="attente").count(),
             "aujourdhui": rdvs.filter(date=date.today()).exclude(statut="annule").count(),
             "total": rdvs.count(), "note": m.moyenne()}
    return render(request, "tableau_medecin.html", {"rdvs": rdvs.exclude(statut="annule"), "stats": stats})


@require_POST
@role_required("medecin")
def changer_statut(request, pk, action):
    rdv = get_object_or_404(RendezVous, pk=pk, medecin=request.user.medecin)
    nouveau = {"confirmer": "confirme", "refuser": "annule", "terminer": "termine"}.get(action)
    if nouveau:
        rdv.statut = nouveau
        rdv.notes = request.POST.get("notes", rdv.notes)
        rdv.save()
        prevenir(rdv.patient, f"Rendez-vous : {rdv.get_statut_display()}", f"Votre rendez-vous {_txt(rdv)} est maintenant : {rdv.get_statut_display()}.")
    return redirect("tableau_medecin")


@role_required("medecin")
def disponibilites(request):
    m = request.user.medecin
    form = DisponibiliteForm(request.POST or None)
    if form.is_valid():
        d = form.save(commit=False)
        d.medecin = m
        d.save()
        return redirect("disponibilites")
    return render(request, "disponibilites.html", {"form": form, "dispos": m.dispos.all()})


@require_POST
@role_required("medecin")
def suppr_dispo(request, pk):
    get_object_or_404(Disponibilite, pk=pk, medecin=request.user.medecin).delete()
    return redirect("disponibilites")


@role_required("medecin")
def conges(request):
    m = request.user.medecin
    form = IndisponibiliteForm(request.POST or None)
    if form.is_valid():
        c = form.save(commit=False)
        c.medecin = m
        c.save()
        messages.success(request, "Période d'indisponibilité ajoutée.")
        return redirect("conges")
    return render(request, "conges.html", {"form": form, "conges": m.conges.all()})


@require_POST
@role_required("medecin")
def suppr_conge(request, pk):
    get_object_or_404(Indisponibilite, pk=pk, medecin=request.user.medecin).delete()
    return redirect("conges")


@role_required("medecin")
def calendrier(request):
    return render(request, "calendrier.html")


@role_required("medecin")
def evenements(request):
    couleurs = {"attente": "#e0a800", "confirme": "#2f9e6f", "termine": "#6f4297"}
    ev = []
    for r in request.user.medecin.rdvs.exclude(statut="annule").select_related("patient"):
        debut = datetime.combine(r.date, r.heure)
        ev.append({"title": r.patient.get_full_name() or r.patient.username,
                   "start": debut.isoformat(), "end": (debut + timedelta(minutes=30)).isoformat(),
                   "color": couleurs[r.statut]})
    return JsonResponse(ev, safe=False)


# ---------- Admin ----------
@role_required("admin")
def tableau_admin(request):
    stats = {"patients": User.objects.filter(role="patient").count(),
             "medecins": Medecin.objects.count(),
             "rdv": RendezVous.objects.count(),
             "attente": RendezVous.objects.filter(statut="attente").count()}
    par_mois = RendezVous.objects.annotate(m=TruncMonth("date")).values("m").annotate(n=Count("id")).order_by("m")
    par_spec = RendezVous.objects.values("medecin__specialite__nom").annotate(n=Count("id")).order_by("-n")
    graph = {"mois": [x["m"].strftime("%m/%Y") for x in par_mois], "n_mois": [x["n"] for x in par_mois],
             "spec": [x["medecin__specialite__nom"] for x in par_spec], "n_spec": [x["n"] for x in par_spec]}
    return render(request, "tableau_admin.html", {
        "stats": stats, "graph": graph,
        "medecins": Medecin.objects.select_related("user", "specialite"),
        "rdvs": RendezVous.objects.select_related("patient", "medecin__user").order_by("-cree_le")[:15]})


@role_required("admin")
def creer_medecin(request):
    form = MedecinCreationForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Médecin créé.")
        return redirect("tableau_admin")
    return render(request, "form.html", {"form": form, "titre": "Nouveau médecin"})


# ---------- Export Excel (tous rôles) ----------
@login_required
def export_excel(request):
    u = request.user
    qs = RendezVous.objects.select_related("patient", "medecin__user", "medecin__specialite")
    if u.role == "patient":
        qs = qs.filter(patient=u)
    elif u.role == "medecin":
        qs = qs.filter(medecin=u.medecin)
    if request.GET.get("statut"):
        qs = qs.filter(statut=request.GET["statut"])
    return reponse(classeur(u, qs), f"rendez-vous_{date.today():%Y%m%d}.xlsx")
