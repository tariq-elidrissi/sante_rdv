# Design system SantéRDV

## Tokens (définis dans `templates/base.html`, bloc `:root`)
| Catégorie | Tokens |
|---|---|
| Couleurs | `--c-primary #6f4297`, `--c-primary-d`, `--c-primary-l`, `--c-success #2f9e6f`, `--c-danger #c0392b`, `--c-warn #e0a800`, `--c-text`, `--c-muted`, `--c-bg`, `--c-surface`, `--c-border` |
| Typographie | `--font` Poppins (texte), `--font-title` Playfair Display (titres) |
| Espacement | `--sp-1` 4px · `--sp-2` 8px · `--sp-3` 12px · `--sp-4` 16px · `--sp-5` 24px · `--sp-6` 40px |
| Rayons | `--r-sm` 8px · `--r-md` 12px · `--r-lg` 18px · `--r-full` 999px |
| Ombres | `--sh-1` (carte) · `--sh-2` (survol) |

## Composant : Bouton `.btn`
**Usage** : toute action cliquable (lien ou `<button>`).

| Variante | Classe | À utiliser pour |
|---|---|---|
| Primaire | `.btn` | Action principale neutre |
| Succès | `.btn g` | Réserver, confirmer, ajouter, exporter |
| Danger | `.btn r` | Annuler, supprimer, refuser |
| Contour | `.btn o` | Action secondaire |
| Blanc / contour blanc | `.btn w` / `.btn ow` | Sur fond sombre (hero, bandeau) |
| Tailles | `.btn s` (petit) · `.btn l` (grand) | Tableaux / appels à l'action |

| État | Rendu |
|---|---|
| Défaut | Pilule colorée, texte blanc |
| Survol | Fond plus foncé, remonte de 2 px, ombre |
| Actif | Revient en place, sans ombre |
| Focus clavier | Anneau violet de 3 px |
| Désactivé | `disabled` : 50 % d'opacité, non cliquable |

**Accessibilité** : rôle natif `button`/`link` ; Tab pour atteindre, Entrée ou Espace pour activer ; le texte décrit l'action (« Confirmer le report », pas « OK »).

| ✅ À faire | ❌ À éviter |
|---|---|
| Un seul bouton `g` ou primaire par zone | Plusieurs boutons de même importance côte à côte |
| `r` uniquement pour les actions destructives | Utiliser le rouge pour une action positive |
| Les actions destructives en `POST` + jeton CSRF | Un lien `GET` qui supprime |

## Autres composants
- **Carte** `.card` : fond blanc, rayon `--r-lg`, ombre `--sh-1` ; `a.card` se soulève au survol.
- **Badge** `.badge` + statut (`attente`, `confirme`, `termine`, `annule`) : couleur selon l'état du rendez-vous.
- **Hero** `.hero` : photo en `background` (`static/img/medecin.jpg`) avec dégradé violet pour garder le texte lisible.
- **Formulaires** : champs arrondis, anneau de focus violet.
