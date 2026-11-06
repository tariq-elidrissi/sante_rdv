from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth
from . import views

urlpatterns = [
    path("inscription/", views.register, name="register"),
    path("connexion/", auth.LoginView.as_view(template_name="form.html",
         extra_context={"titre": "Connexion"}), name="login"),
    path("deconnexion/", auth.LogoutView.as_view(), name="logout"),
    path("redirection/", views.redirection, name="redirection"),
    path("profil/", views.profil, name="profil"),
    path("mot-de-passe/", auth.PasswordChangeView.as_view(
        template_name="form.html", extra_context={"titre": "Changer le mot de passe"},
        success_url=reverse_lazy("profil")), name="password"),
]
