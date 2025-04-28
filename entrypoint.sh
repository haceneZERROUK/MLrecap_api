#!/bin/bash
# startup.sh

# Exécuter le script de création d'admin
python create_admin.py

# Démarrer l'application principale
exec uvicorn app.main:app --host=0.0.0.0 --port=8086 --reload
