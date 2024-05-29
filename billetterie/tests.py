from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Offre, Achat
from .forms import AchatForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.backends import ModelBackend
from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest
from billetterie.admin import OffreAdmin
from .views import generate_qr_code_as_file, create_ticket_pdf

User = get_user_model()

class AchatBilletTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='Motdepassetest12345')
        self.client.force_login(self.user)
        self.offre = Offre.objects.create(nom="Offre_Test", prix=100.0)
        
    def test_achat_billet_form_invalid_data(self):
        form = AchatForm(data={})
        self.assertFalse(form.is_valid())

    def test_achat_billet_form_validation(self):
        form = AchatForm(data={'offre': self.offre.id, 'nombre_billets': 1})
        self.assertTrue(form.is_valid())

    def test_achat_billet_view_authenticated(self):
        response = self.client.get(reverse('achat_billet') + f'?offre={self.offre.nom}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'achat.html')

    def test_achat_billet_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse('achat_billet') + f'?offre={self.offre.nom}')
        expected_url = f"{reverse('inscription')}?next={reverse('achat_billet')}?offre={self.offre.nom}"
        self.assertRedirects(response, expected_url)

    def test_generate_qr_code_as_file(self):
        data = "Test Data"
        qr_file = generate_qr_code_as_file(data)
        self.assertIsNotNone(qr_file)

    def test_create_ticket_pdf(self):
        utilisateur = self.user
        offre = self.offre
        clef_unique = utilisateur.clef_unique
        clef_achat = "test_achat_key"
        nombre_billets = 2
        pdf_path = create_ticket_pdf(utilisateur, offre, clef_unique, clef_achat, nombre_billets)
        self.assertIsNotNone(pdf_path)

class BilletterieTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='Motdepassetest12345')
        self.client.force_login(self.user)
        
    def test_billetterie_offres_display(self):
        response = self.client.get(reverse('billetterie'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'billetterie.html')

    def test_billetterie_view_authenticated(self):
        response = self.client.get(reverse('billetterie'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'billetterie.html')

    def test_billetterie_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse('billetterie'))
        self.assertRedirects(response, f"{reverse('inscription')}?next={reverse('billetterie')}")

    def test_acces_page_protegee(self):
        self.client.logout()
        response = self.client.get(reverse('achat_billet'))
        self.assertRedirects(response, f"{reverse('inscription')}?next={reverse('achat_billet')}")

    def test_deconnexion_utilisateur(self):
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('accueil'))

class InscriptionConnexionTests(TestCase):
    
    def test_inscription_et_connexion(self):
        inscription_url = reverse('inscription')
        inscription_data = {'nom': 'test', 'prenom': 'user', 'email': 'test@example.com', 'password1': 'Motdepassetest12345', 'password2': 'Motdepassetest12345'}
        inscription_response = self.client.post(inscription_url, inscription_data, follow=True)

        self.assertRedirects(inscription_response, reverse('accueil'))

        self.assertTrue(User.objects.filter(username='test_user').exists())

        connexion_url = reverse('login')
        connexion_data = {'username': 'test_user', 'password': 'Motdepassetest12345'}
        connexion_response = self.client.post(connexion_url, connexion_data, follow=True)
        
        self.assertRedirects(connexion_response, reverse('accueil'))

        self.assertTrue(User.objects.get(username='test_user').is_authenticated)


class MockRequest(HttpRequest):
    def __init__(self, user):
        super().__init__()
        self.user = user

class OffreAdminTests(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.user = User.objects.create_superuser(username='admin', password='adminpass', email='admin@example.com')
        self.factory = RequestFactory()
        self.offre_admin = OffreAdmin(Offre, self.site)
        self.offre1 = Offre.objects.create(nom="Offre 1", prix=100.00, description="Description 1")
        self.offre2 = Offre.objects.create(nom="Offre 2", prix=200.00, description="Description 2")

    def test_export_as_csv(self):
        request = MockRequest(user=self.user)
        queryset = Offre.objects.all()
        response = self.offre_admin.export_as_csv(request, queryset)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertTrue(response['Content-Disposition'].startswith('attachment; filename=offres.csv'))

        content = response.content.decode('utf-8-sig')
        lines = content.split('\r\n')
        self.assertEqual(lines[0], "Nom,Prix,Nombre d'achats,Montant généré")
        self.assertIn("Offre 1,100.00,0,0", lines[1])
        self.assertIn("Offre 2,200.00,0,0", lines[2])

