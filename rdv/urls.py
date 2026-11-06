from django.urls import path
from . import views

urlpatterns = [
    path("", views.accueil, name="home"),
    path("medecins/", views.medecins, name="medecins"),
    path("export/rendez-vous.xlsx", views.export_excel, name="export_excel"),
    # patient
    path("rdv/nouveau/<int:pk>/", views.prendre_rdv, name="prendre_rdv"),
    path("rdv/mes-rendez-vous/", views.mes_rdv, name="mes_rdv"),
    path("rdv/<int:pk>/annuler/", views.annuler, name="annuler"),
    path("rdv/<int:pk>/reporter/", views.reporter, name="reporter"),
    path("rdv/<int:pk>/noter/", views.noter, name="noter"),
    # médecin
    path("medecin/tableau/", views.tableau_medecin, name="tableau_medecin"),
    path("medecin/rdv/<int:pk>/<str:action>/", views.changer_statut, name="changer_statut"),
    path("medecin/disponibilites/", views.disponibilites, name="disponibilites"),
    path("medecin/disponibilites/<int:pk>/supprimer/", views.suppr_dispo, name="suppr_dispo"),
    path("medecin/conges/", views.conges, name="conges"),
    path("medecin/conges/<int:pk>/supprimer/", views.suppr_conge, name="suppr_conge"),
    path("medecin/calendrier/", views.calendrier, name="calendrier"),
    path("medecin/evenements/", views.evenements, name="evenements"),
    # admin
    path("gestion/", views.tableau_admin, name="tableau_admin"),
    path("gestion/medecin/nouveau/", views.creer_medecin, name="creer_medecin"),
]
