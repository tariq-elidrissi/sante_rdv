# SantéRDV — Réservation de rendez-vous médicaux (Django)

## Installation
    python3 -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py createsuperuser     # devient automatiquement "admin"
    python manage.py runserver

## Photo de fond
`static/img/medecin.jpg` (remplaçable par une image plus grande pour un rendu plus net).

## Base de données
SQLite : fichier `db.sqlite3` créé à la racine par `migrate`.
Tables : accounts_user, rdv_specialite, rdv_medecin, rdv_disponibilite,
rdv_rendezvous, rdv_indisponibilite, rdv_avis (+ tables internes Django).

## Fonctionnalités
- 3 rôles : patient, médecin, admin
- Patient : recherche de médecins, réservation, report, annulation, avis (étoiles), export Excel
- Médecin : tableau de bord, calendrier, disponibilités, congés, confirmation/refus, export Excel
- Admin : statistiques + graphiques, création de médecins, export Excel complet (4 feuilles)
- E-mails de notification (affichés dans le terminal), profil et mot de passe
- Tests : `python manage.py test`

## Documentation (dossier `docs/`)
- `diagramme_classes.png` — diagramme de classes UML
- `diagramme_cas_utilisation.png` — diagramme de cas d'utilisation
- `schema_base_de_donnees.png` — schéma relationnel (tables, PK, FK)
- `DOC_BASE_DE_DONNEES.md` — fonctionnement de la base de données
- `DESIGN_SYSTEM.md` — tokens et composants de l'interface
- `classes.dot`, `erd.dot`, `usecase.py` — sources des diagrammes (`dot -Tpng fichier.dot -o image.png`)
