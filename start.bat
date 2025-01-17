@echo off
:: Vérifie si pip est installé
python -m ensurepip --default-pip >nul 2>&1

:: Installe les dépendances si elles ne sont pas présentes
pip install -r requirements.txt || (
    echo Une erreur s'est produite lors de l'installation des dépendances.
    pause
    exit /b
)

:: Lance le script main.py
python main.py
