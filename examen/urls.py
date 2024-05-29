from django.contrib import admin
from django.urls import path
from billetterie.views import accueil_view, inscription_view, login_view, logout_view, achat_billet, billetterie_view

urlpatterns = [
    path('', accueil_view, name='accueil'),
    path('inscription/', inscription_view, name='inscription'),
    path('connexion/', login_view, name='login'),
    path('billetterie/', billetterie_view, name='billetterie'),
    path('achat/', achat_billet, name='achat_billet'),
    path('deconnexion/', logout_view, name='logout'),
    path('admin/', admin.site.urls),
]