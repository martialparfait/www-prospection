# WWW Prospection

Scripts de gestion du Google Sheet de prospection (catégories, pays, régions, établissements).

**Sheet** : https://docs.google.com/spreadsheets/d/15Du4fIou9cOOMA5CjTz6aAtP3teTtewWd_YMU7I8Xm0

## Installation

```bash
pip install gspread google-auth
```

## Authentification

Place le fichier JSON de la Service Account Google dans :

```
.secrets/service_account.json
```

Le script le détecte automatiquement (pas besoin de `GOOGLE_APPLICATION_CREDENTIALS`).

⚠️ Le Sheet doit être partagé en édition avec l'email de la Service Account
(`xxx@xxx.iam.gserviceaccount.com`, visible dans le JSON sous `client_email`).

## Utilisation

```bash
python3 setup_sheet.py
```

Reconstruit les onglets `Catégories`, `Pays`, `Régions`, `Établissements`.
