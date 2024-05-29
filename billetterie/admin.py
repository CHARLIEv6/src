from django.contrib import admin
from .models import Offre, Achat, Utilisateur

class OffreAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prix', 'nb_achats', 'montant_genere')
    search_fields = ('nom',)
    list_filter = ('prix',)
    ordering = ('nom',)
    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        from django.utils.encoding import smart_str

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=offres.csv'
        writer = csv.writer(response, csv.excel)
        response.write(u'\ufeff'.encode('utf8'))
        writer.writerow([
            smart_str(u"Nom"),
            smart_str(u"Prix"),
            smart_str(u"Nombre d'achats"),
            smart_str(u"Montant généré"),
        ])

        total_general = 0
        for obj in queryset:
            montant_genere = obj.montant_genere()
            total_general += montant_genere
            writer.writerow([
                smart_str(obj.nom),
                smart_str(obj.prix),
                smart_str(obj.nb_achats()),
                smart_str(montant_genere),
            ])

        writer.writerow([
            smart_str(u"Total général"),
            "",
            "",
            smart_str(total_general),
        ])

        return response

    export_as_csv.short_description = "Exporter la sélection en CSV"

class AchatAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'offre', 'clef_achat')
    search_fields = ('utilisateur__username', 'offre__nom')
    list_filter = ('offre',)

class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('username', 'nom', 'prenom', 'email', 'clef_unique')
    search_fields = ('username', 'nom', 'prenom', 'email')
    ordering = ('username',)

admin.site.register(Offre, OffreAdmin)
admin.site.register(Achat, AchatAdmin)
admin.site.register(Utilisateur, UtilisateurAdmin)