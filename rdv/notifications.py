from django.core.mail import send_mail


def prevenir(destinataire, sujet, message):
    """Envoie un e-mail si le destinataire a une adresse."""
    if destinataire.email:
        send_mail(f"SantéRDV — {sujet}", message, None, [destinataire.email], fail_silently=True)
