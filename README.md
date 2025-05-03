
# MLrecap_api — API de prédiction


Ce dépôt contient le module **MLrecap_api**, qui expose le modèle de machine learning via une API REST construite avec **FastAPI**.

---

## ➤ Description

Ce module permet :  
- De charger le modèle entraîné (`catboostmodel.pkl`)  
- De recevoir des requêtes HTTP POST contenant des données de films  
- De retourner les prédictions attendues (nombre d’entrées estimées)  
- De gérer les vérifications de formats via **Pydantic**  
- De protéger certaines routes par authentification (via un compte administrateur)

Cette API est consommée par l’application Django du module **MLrecap_django**.

---

## ➤ Comment exécuter

### Avec Docker

```
docker build -t mlrecap_api .
docker run -d -p 8086:8086 mlrecap_api
```

### Sans Docker (en local)

1️⃣ Créez l’environnement virtuel :  
```
python -m venv venv
source venv/bin/activate  # sous Windows : venv\Scripts\activate
```

2️⃣ Installez les dépendances :  
```
pip install -r requirements.txt
```

3️⃣ Assurez-vous d’être dans le dossier racine (là où se trouve `app/`) :  
```
uvicorn app.main:app --host=0.0.0.0 --port=8086
```

API disponible ensuite sur : [http://localhost:8086/docs](http://localhost:8086/docs)

---

## ➤ Initialisation de l’administrateur

Avant de tester les routes protégées, créez un compte administrateur :  

1️⃣ Créez un fichier `.env` à la racine du projet, contenant :  
```
API_USER = <username>
API_EMAIL = <email@example.com>
API_PASSWORD = <my_password>
```

2️⃣ Exécutez :  
```
python create_admin.py
```

✅ Le compte sera ajouté à la base et prêt à être utilisé.

---

## ➤ Structure des fichiers

- `app/main.py` → Script principal FastAPI  
- `app/models/` → Chargement du modèle ML  
- `app/schemas.py` → Schémas Pydantic pour validation  
- `app/endpoints/` → Routes organisées par fonctionnalité  
- `create_admin.py` → Script pour initialiser un compte admin  

---

## ➤ Auteur(e)s

* **Hacene Zerrouk**: [GitHub](https://github.com/haceneZERROUK)
* **Malek Boumedine**: [GitHub](https://github.com/Malek-Boumedine)
* **Khadija Abdelmalek**: [GitHub](https://github.com/khadmalek)
* **Khadija Aassi**: [GitHub](https://github.com/Khadaassi)

Pour plus de détails sur le projet: [ML_recap](https://github.com/Khadaassi/Simplon_ML-Recap)

Pour toute question ou amélioration, merci d’ouvrir une issue sur ce dépôt.
