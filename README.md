# TP 1 — De la page statique à la première API

Projet correspondant aux étapes 1 à 5 du TP. Le pays choisi pour le bonus est le **Cameroun** (`CMR`). Les quatre prix initiaux de `prix.csv` sont des **données fictives de démonstration**, à remplacer par de vrais relevés.

## 1. Installer et préparer

Python, VS Code et Git sont nécessaires. Dans ce dossier, sous PowerShell :

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Le dépôt Git local se crée avec `git init`, puis `git add .` et `git commit -m "TP 1 : formulaire et API Django"`. Pour le publier, créez un dépôt vide sur votre compte GitHub, puis ajoutez son URL avec `git remote add origin URL_DU_DEPOT` et poussez avec `git push -u origin main` (après avoir nommé la branche `main` si nécessaire). Ne publiez pas `.venv` ; il est exclu par `.gitignore`.

## 2–3. HTML et CSS

Ouvrez `releve.html` directement dans un navigateur pour voir le formulaire et son style mobile. Dans ce mode, les relevés saisis sont conservés dans le stockage local du navigateur. Testez les largeurs mobile et ordinateur avec le mode « appareil » des outils de développement. Le chargement de la population nécessite le serveur Django.

## 4–5. Django et API

```powershell
.\.venv\Scripts\python.exe app.py runserver
```

Ouvrez ensuite :

- `http://127.0.0.1:8000/` : formulaire ; avec le serveur, les envois sont ajoutés à `prix.csv`.
- `http://127.0.0.1:8000/bonjour/Douala` : salutation de la ville.
- `http://127.0.0.1:8000/api/prix` : JSON des relevés du CSV.
- `http://127.0.0.1:8000/api/prix?affichage=texte` : même JSON affiché en texte, utile pour une capture si le navigateur télécharge les réponses `application/json`.
- `http://127.0.0.1:8000/apercu/prix` : page de présentation de la réponse de `/api/prix` pour les navigateurs qui bloquent l’ouverture directe du JSON.
- `http://127.0.0.1:8000/api/population/CMR` : dernière population non vide du Cameroun via la Banque mondiale, avec son année et l’URL source.

L’API Banque mondiale doit être accessible depuis le réseau pour afficher la population. La route répond avec une erreur explicite si elle est indisponible. Documentation officielle : https://datahelpdesk.worldbank.org/knowledgebase/articles/898581-api-basic-call-structures

## Éléments à rendre

1. Le lien de votre dépôt GitHub après publication.
2. Une capture du navigateur sur `/api/prix`, ou de son aperçu `/apercu/prix` si le navigateur bloque le JSON brut (fichier `capture_api_prix.png` si disponible).
3. Les cinq lignes ci-dessous sur l’usage de l’IA.

## Usage de l’IA — cinq lignes

Une IA a aidé à structurer les fichiers et les routes Django de ce rendu.  
Elle a proposé le formulaire HTML, le style CSS et les contrôles des données saisies.  
Elle a aidé à relier le CSV à l’API JSON et à l’API de la Banque mondiale.  
Les exemples de prix sont fictifs et doivent être remplacés par des relevés réels.  
Le code et les résultats doivent être relus et testés par l’étudiant avant remise.
