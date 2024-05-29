from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Utilisateur

class InscriptionForm(UserCreationForm):
    nom = forms.CharField(max_length=50, label="Nom", help_text="Veuillez entrer uniquement des lettres minuscules.")
    prenom = forms.CharField(max_length=50, label="Prénom", help_text="Veuillez entrer uniquement des lettres minuscules.")

    class Meta:
        model = Utilisateur
        fields = ['nom', 'prenom', 'email', 'password1', 'password2']

    def clean_nom(self):
        nom = self.cleaned_data['nom']
        if not nom.islower():
            raise forms.ValidationError("Le nom doit être en minuscules.")
        return nom

    def clean_prenom(self):
        prenom = self.cleaned_data['prenom']
        if not prenom.islower():
            raise forms.ValidationError("Le prénom doit être en minuscules.")
        return prenom

    def save(self, commit=True):
        utilisateur = super().save(commit=False)
        utilisateur.nom = self.cleaned_data['nom'].lower()
        utilisateur.prenom = self.cleaned_data['prenom'].lower()
        utilisateur.username = f"{utilisateur.nom}_{utilisateur.prenom}".replace(" ", "_")
        
        if commit:
            utilisateur.save()
        return utilisateur

class AchatForm(forms.Form):
    nombre_billets = forms.IntegerField(min_value=1, label="Nombre de billets", required=True)

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label="Nom d'utilisateur", widget=forms.TextInput(attrs={"placeholder": "ex : nom_prenom"}))
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)