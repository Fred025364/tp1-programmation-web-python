"""Petit projet Django autonome pour le TP 1.

Lancement : python app.py runserver
"""

import csv
import json
import os
import re
from datetime import date
from html import escape
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings


BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "prix.csv"
FIELDS = ("date", "ville", "produit", "unite", "prix_fcfa")

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY=os.environ.get("DJANGO_SECRET_KEY", "tp1-local-development-only"),
        ALLOWED_HOSTS=["localhost", "127.0.0.1", "testserver"],
        ROOT_URLCONF=__name__,
        MIDDLEWARE=[
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
        ],
        DEFAULT_CHARSET="utf-8",
    )

import django  # noqa: E402

django.setup()

from django.http import FileResponse, HttpResponse, JsonResponse  # noqa: E402
from django.urls import path  # noqa: E402
from django.views.decorators.csrf import ensure_csrf_cookie  # noqa: E402


@ensure_csrf_cookie
def accueil(request):
    """Affiche le formulaire et pose le cookie CSRF pour ses envois."""
    return FileResponse((BASE_DIR / "releve.html").open("rb"), content_type="text/html; charset=utf-8")


def style(request):
    return FileResponse((BASE_DIR / "style.css").open("rb"), content_type="text/css; charset=utf-8")


def script(request):
    return FileResponse((BASE_DIR / "script.js").open("rb"), content_type="text/javascript; charset=utf-8")


def bonjour(request, ville):
    return HttpResponse(f"Bonjour {ville} !", content_type="text/plain; charset=utf-8")


def lire_prix():
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as fichier:
        return list(csv.DictReader(fichier))


def valider_releve(data):
    if not isinstance(data, dict):
        raise ValueError("Le relevé doit être un objet JSON.")
    valeurs = {champ: str(data.get(champ, "")).strip() for champ in FIELDS}
    try:
        date.fromisoformat(valeurs["date"])
    except ValueError:
        raise ValueError("La date doit être au format AAAA-MM-JJ.") from None

    for champ in ("ville", "produit", "unite"):
        valeur = valeurs[champ]
        if not 1 <= len(valeur) <= 80 or not re.fullmatch(r"[\wÀ-ÿ .'-]+", valeur, re.UNICODE):
            raise ValueError(f"Le champ {champ} est invalide.")

    if not valeurs["prix_fcfa"].isdigit() or not 1 <= int(valeurs["prix_fcfa"]) <= 10_000_000:
        raise ValueError("Le prix doit être un entier positif (maximum : 10 000 000 FCFA).")
    return valeurs


def api_prix(request):
    if request.method == "GET":
        lignes = lire_prix()
        resultat = {"source": "prix.csv", "nombre": len(lignes), "prix": lignes}
        if request.GET.get("affichage") == "texte":
            return HttpResponse(
                json.dumps(resultat, ensure_ascii=False, indent=2),
                content_type="text/plain; charset=utf-8",
            )
        return JsonResponse(resultat, json_dumps_params={"ensure_ascii": False})

    if request.method == "POST":
        try:
            valeurs = valider_releve(json.loads(request.body))
        except (json.JSONDecodeError, UnicodeDecodeError, TypeError, ValueError) as erreur:
            return JsonResponse({"erreur": str(erreur)}, status=400)
        with CSV_PATH.open("a", encoding="utf-8", newline="") as fichier:
            writer = csv.DictWriter(fichier, fieldnames=FIELDS)
            writer.writerow(valeurs)
        return JsonResponse({"message": "Relevé enregistré.", "releve": valeurs}, status=201, json_dumps_params={"ensure_ascii": False})

    return JsonResponse({"erreur": "Méthode non autorisée."}, status=405)


def apercu_prix(request):
    """Affiche dans une page HTML la réponse de /api/prix pour la capture du TP."""
    lignes = lire_prix()
    resultat = {"source": "prix.csv", "nombre": len(lignes), "prix": lignes}
    contenu = escape(json.dumps(resultat, ensure_ascii=False, indent=2))
    page = (
        '<!doctype html><html lang="fr"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Réponse de /api/prix</title>'
        '<style>body{margin:0;padding:32px;background:#f3f7f8;color:#102d47;font:16px Segoe UI,Arial,sans-serif}'
        'main{max-width:900px;margin:auto}h1{font-size:1.6rem}p{color:#5c6f7e}'
        'pre{overflow:auto;background:white;border:1px solid #dce6e9;border-radius:12px;padding:24px;line-height:1.5}'
        'a{color:#2b8260}</style><main><h1>GET /api/prix</h1>'
        '<p>Réponse JSON produite à partir de prix.csv</p>'
        f'<pre>{contenu}</pre><a href="/">Retour au formulaire</a></main></html>'
    )
    return HttpResponse(page, content_type="text/html; charset=utf-8")


def api_population(request, pays="TCD"):
    if request.method != "GET":
        return JsonResponse({"erreur": "Méthode non autorisée."}, status=405)
    if not re.fullmatch(r"[A-Za-z]{3}", pays):
        return JsonResponse({"erreur": "Utilisez un code pays de trois lettres."}, status=400)

    code = pays.upper()
    source = f"https://api.worldbank.org/v2/country/{code}/indicator/SP.POP.TOTL?format=json&mrnev=1"
    try:
        requete = Request(source, headers={"User-Agent": "TP1-ISSEA/1.0"})
        with urlopen(requete, timeout=10) as reponse:
            donnees = json.load(reponse)
        if not isinstance(donnees, list) or len(donnees) < 2 or not donnees[1]:
            raise ValueError("Aucune donnée de population trouvée pour ce pays.")
        entree = donnees[1][0]
        if entree.get("value") is None:
            raise ValueError("La dernière donnée de population est vide.")
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as erreur:
        return JsonResponse({"erreur": "La Banque mondiale est momentanément indisponible.", "detail": str(erreur)}, status=502)
    except (ValueError, KeyError, IndexError, TypeError) as erreur:
        return JsonResponse({"erreur": str(erreur)}, status=404)

    return JsonResponse(
        {"pays": entree["country"]["value"], "code": code, "annee": entree["date"], "population": entree["value"], "source": source},
        json_dumps_params={"ensure_ascii": False},
    )


urlpatterns = [
    path("", accueil),
    path("style.css", style),
    path("script.js", script),
    path("bonjour/<str:ville>", bonjour),
    path("api/prix", api_prix),
    path("apercu/prix", apercu_prix),
    path("api/population", api_population),
    path("api/population/<str:pays>", api_population),
]


if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line()
