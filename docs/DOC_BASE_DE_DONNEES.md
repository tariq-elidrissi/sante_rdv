# Comment fonctionne la base de données de SantéRDV

## 1. Principe
- Le projet utilise **SQLite** : toute la base est **un seul fichier**, `db.sqlite3`, créé à la racine du projet par `python manage.py migrate`.
- On n'écrit presque jamais de SQL : on décrit les tables en Python dans `models.py` (c'est l'**ORM** de Django).
- Chaîne de travail :  `models.py`  →  `makemigrations` (fichier de migration)  →  `migrate` (création/modification des tables dans `db.sqlite3`).

## 2. Les tables
| Table | Rôle | Clés |
|---|---|---|
| `accounts_user` | Tous les comptes (patient, médecin, admin) avec leur `role` | PK `id` |
| `rdv_specialite` | Liste des spécialités | PK `id` |
| `rdv_medecin` | Fiche d'un médecin (bio, tarif) | FK `user_id` (unique), FK `specialite_id` |
| `rdv_disponibilite` | Horaires hebdomadaires d'un médecin (ex. lundi 09:00–12:00) | FK `medecin_id` |
| `rdv_indisponibilite` | Congés / jours sans consultation | FK `medecin_id` |
| `rdv_rendezvous` | Les rendez-vous (date, heure, statut, notes) | FK `patient_id`, FK `medecin_id` |
| `rdv_avis` | Note de 1 à 5 laissée après une consultation terminée | FK `rdv_id` (unique) |

Django ajoute aussi ses tables internes (sessions, permissions, journal de l'admin…).

## 3. Les relations
- Un **User** peut être **un seul Médecin** (relation 1–0..1) ; un User patient n'a pas de fiche médecin.
- Une **Spécialité** a plusieurs **Médecins** (1–N).
- Un **Médecin** a plusieurs **Disponibilités**, **Indisponibilités** et **RendezVous** (1–N).
- Un **User patient** prend plusieurs **RendezVous** (1–N).
- Un **RendezVous** a **au plus un Avis** (1–0..1).
- Une **clé étrangère (FK)** est une colonne qui contient l'`id` d'une ligne d'une autre table : c'est ce qui relie les tables.

## 4. Pourquoi les créneaux libres ne sont pas stockés
Les créneaux de 30 minutes sont **calculés à la demande** (`rdv/utils.py`) :
`créneaux = horaires du médecin ce jour-là − congés − rendez-vous déjà pris (non annulés) − heures passées`.
Ainsi, annuler un rendez-vous libère automatiquement le créneau, sans mise à jour supplémentaire.

## 5. Exemple : que se passe-t-il quand un patient réserve ?
1. Le patient choisit un médecin et une date.
2. Django lit (SQL équivalent) :
```sql
SELECT jour, debut, fin FROM rdv_disponibilite WHERE medecin_id = 1 AND jour = 3;
SELECT heure FROM rdv_rendezvous WHERE medecin_id = 1 AND date = '2026-11-12' AND statut <> 'annule';
```
3. Il affiche les créneaux restants. Le patient en choisit un, Django réécrit la vérification puis :
```sql
INSERT INTO rdv_rendezvous (patient_id, medecin_id, date, heure, motif, statut, notes, cree_le)
VALUES (5, 1, '2026-11-12', '09:30', 'Contrôle', 'attente', '', CURRENT_TIMESTAMP);
```
4. Le médecin confirme : `UPDATE rdv_rendezvous SET statut = 'confirme' WHERE id = 12;`
5. Après la consultation (`statut = 'termine'`), le patient peut ajouter une ligne dans `rdv_avis`.

## 6. Sécurité et intégrité
- Les mots de passe sont **hachés** (jamais stockés en clair).
- Les **FK** et les contraintes **unique** empêchent les données incohérentes (deux fiches pour le même médecin, deux avis pour le même rendez-vous).
- Les droits (patient / médecin / admin) sont vérifiés dans les vues (`@role_required`), pas dans la base.
- `on_delete=CASCADE` : supprimer un médecin supprime ses horaires et rendez-vous ; `PROTECT` empêche de supprimer une spécialité encore utilisée.

## 7. Regarder la base soi-même
```bash
python manage.py dbshell          # ouvre sqlite3
.tables                           # liste des tables
.schema rdv_rendezvous            # structure d'une table
SELECT * FROM rdv_rendezvous;     # contenu
.quit
```
Ou ouvrir `db.sqlite3` avec l'application gratuite **DB Browser for SQLite**.
Pour passer à MySQL : changer `DATABASES` dans `config/settings.py` et installer `mysqlclient` ; les modèles ne changent pas.
