from datetime import datetime, timedelta, date


def creneaux_libres(medecin, jour):
    """Créneaux de 30 min libres pour un médecin à une date donnée."""
    if medecin.conges.filter(debut__lte=jour, fin__gte=jour).exists():
        return []
    pris = set(medecin.rdvs.filter(date=jour).exclude(statut="annule")
               .values_list("heure", flat=True))
    maintenant = datetime.now().time()
    res = []
    for d in medecin.dispos.filter(jour=jour.weekday()):
        t, fin = datetime.combine(jour, d.debut), datetime.combine(jour, d.fin)
        while t + timedelta(minutes=30) <= fin:
            if t.time() not in pris and (jour > date.today() or t.time() > maintenant):
                res.append(t.time())
            t += timedelta(minutes=30)
    return sorted(res)
