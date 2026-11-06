from io import BytesIO
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

VIOLET, POLICE = "6F4297", "Arial"
STATUTS = ["En attente", "Confirmé", "Terminé", "Annulé"]


def _feuille(ws, entetes, lignes, formats=None):
    ws.append(entetes)
    for c in ws[1]:
        c.font = Font(name=POLICE, bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=VIOLET)
        c.alignment = Alignment(horizontal="center")
    for ligne in lignes:
        ws.append(ligne)
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.font = Font(name=POLICE)
    for col, fmt in (formats or {}).items():
        for c in ws[col][1:]:
            c.number_format = fmt
    ws.freeze_panes = "A2"
    if ws.max_row > 1:
        ws.auto_filter.ref = ws.dimensions
    for i, col in enumerate(ws.columns, 1):
        ws.column_dimensions[get_column_letter(i)].width = min(
            40, max(len(str(c.value or "")) for c in col) + 3)


def classeur(user, rdvs):
    """Construit le classeur Excel selon le rôle de l'utilisateur."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Rendez-vous"
    entetes = ["Date", "Heure", "Patient", "Téléphone", "Médecin", "Spécialité", "Motif", "Statut"]
    if user.role != "patient":
        entetes.append("Notes")
    lignes = []
    for r in rdvs:
        ligne = [r.date, r.heure.strftime("%H:%M"), r.patient.get_full_name() or r.patient.username,
                 r.patient.telephone, str(r.medecin), r.medecin.specialite.nom, r.motif,
                 r.get_statut_display()]
        if user.role != "patient":
            ligne.append(r.notes)
        lignes.append(ligne)
    _feuille(ws, entetes, lignes, {"A": "DD/MM/YYYY"})

    # Feuille de synthèse avec formules (recalculées par Excel)
    rs = wb.create_sheet("Résumé")
    _feuille(rs, ["Statut", "Nombre"], [[s, None] for s in STATUTS])
    for i in range(2, 2 + len(STATUTS)):
        rs[f"B{i}"] = f"=COUNTIF('Rendez-vous'!$H:$H,A{i})"
        rs[f"B{i}"].font = Font(name=POLICE)
    total = 2 + len(STATUTS)
    rs[f"A{total}"], rs[f"B{total}"] = "Total", f"=SUM(B2:B{total - 1})"
    for c in (rs[f"A{total}"], rs[f"B{total}"]):
        c.font = Font(name=POLICE, bold=True)

    if user.role == "admin":
        from .models import Medecin
        from django.contrib.auth import get_user_model
        U = get_user_model()
        wm = wb.create_sheet("Médecins")
        _feuille(wm, ["Nom", "Spécialité", "E-mail", "Téléphone", "Tarif (DH)", "Note moyenne", "Nb avis"],
                 [[str(m), m.specialite.nom, m.user.email, m.user.telephone, float(m.tarif),
                   m.moyenne(), m.nb_avis()] for m in Medecin.objects.select_related("user", "specialite")],
                 {"E": "#,##0.00"})
        wp = wb.create_sheet("Patients")
        _feuille(wp, ["Nom", "E-mail", "Téléphone", "Nb rendez-vous", "Inscrit le"],
                 [[p.get_full_name() or p.username, p.email, p.telephone, p.rdvs.count(),
                   p.date_joined.date()] for p in U.objects.filter(role="patient")],
                 {"E": "DD/MM/YYYY"})
    return wb


def reponse(wb, nom):
    buf = BytesIO()
    wb.save(buf)
    r = HttpResponse(buf.getvalue(),
                     content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    r["Content-Disposition"] = f'attachment; filename="{nom}"'
    return r
