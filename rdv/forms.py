from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import User
from .models import Disponibilite, Specialite, Medecin, Indisponibilite, Avis


class DisponibiliteForm(forms.ModelForm):
    class Meta:
        model = Disponibilite
        fields = ["jour", "debut", "fin"]
        widgets = {"debut": forms.TimeInput(attrs={"type": "time"}),
                   "fin": forms.TimeInput(attrs={"type": "time"})}


class MedecinCreationForm(UserCreationForm):
    specialite = forms.ModelChoiceField(Specialite.objects.all())
    tarif = forms.DecimalField(min_value=0, initial=0)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "telephone")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "medecin"
        user.save()
        Medecin.objects.create(user=user, specialite=self.cleaned_data["specialite"],
                               tarif=self.cleaned_data["tarif"])
        return user


class IndisponibiliteForm(forms.ModelForm):
    class Meta:
        model = Indisponibilite
        fields = ["debut", "fin", "motif"]
        widgets = {"debut": forms.DateInput(attrs={"type": "date"}),
                   "fin": forms.DateInput(attrs={"type": "date"})}

    def clean(self):
        data = super().clean()
        if data.get("debut") and data.get("fin") and data["fin"] < data["debut"]:
            raise forms.ValidationError("La date de fin doit être après la date de début.")
        return data


class AvisForm(forms.ModelForm):
    class Meta:
        model = Avis
        fields = ["note", "commentaire"]
