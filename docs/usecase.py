import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle, Circle

V, G, RD, GR, OR = "#6f4297", "#2f9e6f", "#c0392b", "#6b6b7b", "#e0a800"
fig, ax = plt.subplots(figsize=(17, 12))
ax.set_xlim(0, 17); ax.set_ylim(-0.7, 12.2); ax.axis("off")
ax.add_patch(Rectangle((2.8, 0.0), 11.4, 11.7, fill=False, ec=V, lw=2, zorder=1))
ax.text(8.5, 11.3, "Système SantéRDV — réservation de rendez-vous médicaux", ha="center",
        fontsize=14, fontweight="bold", color=V)

def acteur(x, y, nom, c):
    ax.add_patch(Circle((x, y + 0.75), 0.22, fill=False, ec=c, lw=2, zorder=3))
    ax.plot([x, x], [y + 0.53, y - 0.05], c=c, lw=2, zorder=3)
    ax.plot([x - 0.4, x + 0.4], [y + 0.35, y + 0.35], c=c, lw=2, zorder=3)
    ax.plot([x, x - 0.35], [y - 0.05, y - 0.65], c=c, lw=2, zorder=3)
    ax.plot([x, x + 0.35], [y - 0.05, y - 0.65], c=c, lw=2, zorder=3)
    ax.text(x, y - 0.95, nom, ha="center", va="top", fontsize=13, fontweight="bold", color=c)

P = {}
def uc(key, x, y, texte, c, w=3.7, h=0.8):
    e = Ellipse((x, y), w, h, fc="white", ec=c, lw=1.7, zorder=4)
    ax.add_patch(e)
    ax.text(x, y, texte, ha="center", va="center", fontsize=10.5, zorder=5)
    P[key] = (x, y, w, e)

def lien(src, key, c):
    x, y, w, _ = P[key]
    ex = x - w / 2 if src[0] < x else x + w / 2
    ax.plot([src[0], ex], [src[1], y], c=c, lw=1.2, zorder=2)

L, R = 4.9, 12.1
# --- gauche : visiteur puis patient
uc("insc", L, 10.2, "S'inscrire", V)
uc("conn", L, 9.2, "Se connecter", V)
uc("cons", L, 8.2, "Consulter les médecins", V)
uc("resa", L, 7.0, "Réserver un rendez-vous", V)
uc("repo", L, 6.0, "Reporter un rendez-vous", V)
uc("annu", L, 5.0, "Annuler un rendez-vous", V)
uc("note", L, 4.0, "Noter un médecin\n(après consultation)", V, h=0.95)
uc("prof", L, 3.0, "Modifier son profil", V)
uc("xp", L, 2.0, "Exporter ses RDV en Excel", V)
# --- droite : médecin puis admin
uc("disp", R, 10.2, "Gérer ses disponibilités", G)
uc("cong", R, 9.2, "Gérer ses congés", G)
uc("cale", R, 8.2, "Consulter son calendrier", G)
uc("conf", R, 7.0, "Confirmer / refuser un RDV", G)
uc("term", R, 6.0, "Terminer la consultation", G)
uc("xm", R, 5.0, "Exporter ses RDV en Excel", G)
uc("crea", R, 3.7, "Créer un compte médecin", RD)
uc("stat", R, 2.7, "Consulter les statistiques", RD)
uc("spec", R, 1.7, "Gérer spécialités / utilisateurs", RD)
uc("xa", R, 0.7, "Exporter toutes les données", RD)
# --- centre : notification
uc("mail", 8.5, 6.0, "Envoyer un e-mail\nde notification", GR, w=2.3, h=1.1)

# acteurs
av = (1.3, 9.2); ap = (1.3, 4.6); am = (15.7, 7.6); aa = (15.7, 2.2)
acteur(*av, "Visiteur", V); acteur(*ap, "Patient", V)
acteur(*am, "Médecin", G); acteur(*aa, "Administrateur", RD)
for k in ("insc", "conn", "cons"): lien((av[0] + 0.45, av[1] + 0.3), k, V)
for k in ("resa", "repo", "annu", "note", "prof", "xp"): lien((ap[0] + 0.45, ap[1] + 0.3), k, V)
for k in ("disp", "cong", "cale", "conf", "term", "xm"): lien((am[0] - 0.45, am[1] + 0.3), k, G)
for k in ("crea", "stat", "spec", "xa"): lien((aa[0] - 0.45, aa[1] + 0.3), k, RD)

# include (dépendances) vers la notification e-mail
for src in ("resa", "repo", "annu", "conf"):
    x, y, w, e = P[src]; mx, my, mw, me = P["mail"]
    ax.annotate("", xy=(mx, my), xytext=(x, y), zorder=3,
                arrowprops=dict(arrowstyle="->", ls="--", color=GR, lw=1.3, patchA=e, patchB=me, shrinkA=0, shrinkB=0))
ax.text(7.55, 7.35, "«include»", fontsize=9, style="italic", color=GR, ha="center",
        bbox=dict(fc="white", ec="none", pad=0.6), zorder=6)
ax.text(9.45, 7.35, "«include»", fontsize=9, style="italic", color=GR, ha="center",
        bbox=dict(fc="white", ec="none", pad=0.6), zorder=6)

ax.text(8.5, -0.45, "Remarque : toutes les actions, sauf « S'inscrire » et « Consulter les médecins », exigent « Se connecter » "
        "(médecin et administrateur aussi).", ha="center", fontsize=10, style="italic", color=GR)
plt.savefig("diagramme_cas_utilisation.png", dpi=130, bbox_inches="tight", facecolor="white")
