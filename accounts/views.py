from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import RegisterForm, ProfilForm


def register(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        login(request, form.save())  # role = patient par défaut
        return redirect("redirection")
    return render(request, "form.html", {"form": form, "titre": "Créer un compte"})


@login_required
def redirection(request):
    cible = {"patient": "mes_rdv", "medecin": "tableau_medecin", "admin": "tableau_admin"}
    return redirect(cible[request.user.role])


@login_required
def profil(request):
    form = ProfilForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, "Profil mis à jour.")
        return redirect("profil")
    return render(request, "form.html", {"form": form, "titre": "Mon profil",
                                          "lien": ("password", "Changer mon mot de passe")})
