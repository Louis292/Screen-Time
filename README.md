# Screen Time

## Description
L'application **Screen Time** est un outil écrit en Python qui permet d'enregistrer et d'analyser le temps passé sur différentes applications de votre ordinateur. Elle surveille en temps réel les fenêtres actives, enregistre le temps d'utilisation par application, et offre des visualisations pour mieux comprendre vos habitudes numériques.

### Fonctionnalités principales :
- Suivi du temps d'utilisation des applications en temps réel.
- Enregistrement automatique dans une base de données SQLite.
- Affichage des statistiques sous forme de graphiques.
- Interface utilisateur intuitive avec **Tkinter**.

---

## Installation et exécution

### Option 1 : Utilisation du fichier exécutable
1. Téléchargez le fichier exécutable `.exe` depuis le site ou le dépôt officiel.
2. Double-cliquez sur le fichier téléchargé pour lancer l'application.

### Option 2 : Exécution depuis le code source
1. Assurez-vous que Python est installé sur votre système (version 3.7 ou supérieure recommandée).
2. Téléchargez ou clonez le projet contenant les fichiers source.
3. Naviguez dans le répertoire du projet via un terminal.
4. Installez les dépendances en exécutant :
   ```bash
   pip install -r requirements.txt
   ```
5. Lancez l'application en exécutant :
   ```bash
   python main.py
   ```

### Option 3 : Utilisation avec `start.bat`
1. Téléchargez le projet contenant le fichier `start.bat`.
2. Double-cliquez sur `start.bat` pour :
   - Vérifier que toutes les dépendances sont installées.
   - Installer automatiquement les dépendances manquantes.
   - Lancer l'application.

---

### Configuration requise
- **Système d'exploitation** : Windows (nécessite `pywin32` pour l'interaction avec les processus Windows).
- **Python** : Version 3.7 ou supérieure.
- **Modules requis** : Voir `requirements.txt`.

---
