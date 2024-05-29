from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string


class Utilisateur(AbstractUser):
    nom = models.CharField(max_length=50, blank=False)
    prenom = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True)
    clef_unique = models.CharField(max_length=16, unique=True, default=get_random_string(16))

    def save(self, *args, **kwargs):
        self.nom = self.nom.lower()
        self.prenom = self.prenom.lower()
        self.username = f"{self.nom}_{self.prenom}".replace(" ", "_")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

class Offre(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField()
    prix = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.nom

    def nb_achats(self):
        return Achat.objects.filter(offre=self).count()
    
    def montant_genere(self):
        total_achats = Achat.objects.filter(offre=self).aggregate(total=models.Sum('offre__prix'))
        return total_achats['total'] if total_achats['total'] is not None else 0

class Achat(models.Model):
    utilisateur = models.ForeignKey(
        'billetterie.Utilisateur',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    offre = models.ForeignKey(
        'billetterie.Offre',
        on_delete=models.CASCADE,
    )
    clef_achat = models.CharField(max_length=16, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.clef_achat:
            while True:
                clef = get_random_string(16)
                if not Achat.objects.filter(clef_achat=clef).exists():
                    self.clef_achat = clef
                    break
        super().save(*args, **kwargs)