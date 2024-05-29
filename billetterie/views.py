from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.conf import settings
from .forms import InscriptionForm, AchatForm, LoginForm
from .models import Offre, Achat, Utilisateur
import qrcode
import os
from tempfile import NamedTemporaryFile  
from reportlab.pdfgen import canvas  
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from django.shortcuts import get_object_or_404


def accueil_view(request):
    return render(request, "accueil.html")

def inscription_view(request):
    form = InscriptionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        utilisateur = form.save()
        login(request, utilisateur, backend='django.contrib.auth.backends.ModelBackend')
        return redirect("accueil")
    return render(request, "inscription.html", {"form": form})

def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        utilisateur = authenticate(
            request,
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"]
        )
        if utilisateur:
            login(request, utilisateur)
            return redirect("accueil")
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    return render(request, "login.html", {"form": form})



def generate_qr_code_as_file(data):
    try:
        with NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            qr = qrcode.make(data)
            qr.save(tmp_file.name)
            return tmp_file.name
    except Exception as e:
        print("Erreur lors de la génération du QR code:", e)
        return None


def create_ticket_pdf(utilisateur, offre, clef_unique, clef_achat, nombre_billets):
    try:
        with NamedTemporaryFile(delete=False) as pdf_temp_file:
            pdf = canvas.Canvas(pdf_temp_file.name, pagesize=A4)
            largeur, hauteur = A4
            centre_x = largeur / 2

            logo_path = os.path.join(settings.STATICFILES_DIRS[0], "logojo.png")
            if os.path.exists(logo_path):
                logo_largeur = 6 * cm
                logo_hauteur = 6 * cm
                position_x = centre_x - (logo_largeur / 2)
                position_y = hauteur - (logo_hauteur + 2 * cm)
                pdf.drawImage(logo_path, position_x, position_y, width=logo_largeur, height=logo_hauteur)
            else:
                print("Logo introuvable à", logo_path)

            position_y -= 2 * cm
            pdf.setFont("Helvetica-Bold", 24)
            pdf.drawCentredString(centre_x, position_y, "Billet d'Événement")

            pdf.setFont("Helvetica-Bold", 14)
            position_y -= 2 * cm
            pdf.drawCentredString(centre_x, position_y, f"Utilisateur :")

            pdf.setFont("Helvetica", 14)
            pdf.drawCentredString(centre_x, position_y - 1 * cm, utilisateur.username)

            pdf.setFont("Helvetica-Bold", 14)
            position_y -= 3 * cm
            pdf.drawCentredString(centre_x, position_y, f"Offre :")

            pdf.setFont("Helvetica", 14)
            pdf.drawCentredString(centre_x, position_y - 1 * cm, offre.nom)

            pdf.setFont("Helvetica-Bold", 14)
            position_y -= 3 * cm
            pdf.drawCentredString(centre_x, position_y, f"Nombre de billets :")

            pdf.setFont("Helvetica", 14)
            pdf.drawCentredString(centre_x, position_y - 1 * cm, str(nombre_billets))

            qr_file = generate_qr_code_as_file(f"{clef_unique}_{clef_achat}")
            if qr_file:
                qr_largeur = 8 * cm
                position_y -= 10 * cm
                pdf.drawInlineImage(qr_file, centre_x - (qr_largeur / 2), position_y, width=qr_largeur, height=qr_largeur)
                os.remove(qr_file)
            else:
                raise Exception("Erreur lors de la génération du QR code")

            pdf.showPage()
            pdf.save()

            return pdf_temp_file.name

    except Exception as e:
        print("Erreur lors de la création du PDF:", e)
        return None

@login_required(login_url='inscription')
def achat_billet(request):
    form = AchatForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        try:
            utilisateur = request.user
            offre_nom = request.GET.get("offre")
            offre = get_object_or_404(Offre, nom=offre_nom)
            nombre_billets = form.cleaned_data["nombre_billets"]
            achats = []
            for _ in range(nombre_billets):
                achat = Achat(utilisateur=utilisateur, offre=offre)
                achat.save()
                achats.append(achat)

            pdf_path = create_ticket_pdf(
                utilisateur, offre, achats[-1].utilisateur.clef_unique, achats[-1].clef_achat, nombre_billets
            )

            if pdf_path is None:
                raise Exception("Le PDF n'a pas été généré")
            with open(pdf_path, "rb") as pdf_file:
                response = HttpResponse(pdf_file, content_type="application/pdf")
                response['Content-Disposition'] = 'attachment; filename="billet_evenement.pdf"'
                return response

        except Offre.DoesNotExist:
            return HttpResponseNotFound("Offre non trouvée")

        except Exception as e:
            messages.error(request, f"Erreur lors de l'achat: {e}")
            return redirect("billetterie")

    messages.error(request, "Formulaire invalide.")
    return render(request, "achat.html", {"form": form})

@login_required(login_url='inscription')
def billetterie_view(request):
    offres = Offre.objects.all()
    return render(request, 'billetterie.html', {"offres": offres})

def logout_view(request):
    logout(request)
    return redirect("accueil")