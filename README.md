Plateforme Sociale Académique - Research Platform

Une plateforme web sociale pour chercheurs académiques, similaire à ResearchGate, permettant aux utilisateurs de publier des recherches, rejoindre des groupes, partager des posts, échanger des messages et interagir via des commentaires et notifications.
Structure du Projet

monprojet_complete/
├── config/              # Configuration Django (settings, URLs, WSGI/ASGI)
├── apps/                # Applications Django modulaires
│   ├── users/           # Utilisateurs
│   ├── publications/    # Publications de recherche
│   ├── groups/          # Groupes de recherche
│   ├── posts/           # Posts
│   ├── messages/        # Messages privés
│   ├── comments/        # Commentaires
│   └── notifications/   # Notifications
├── templates/           # Templates HTML globaux
├── static/              # Fichiers statiques globaux (CSS, JS, images)
├── media/               # Fichiers uploadés par les utilisateurs
├── manage.py            # Script de gestion Django
├── requirements.txt     # Dépendances Python
└── .env                 # Variables d'environnement

Installation
Prérequis

    Python 3.8+
    MySQL 5.7+ ou MariaDB 10.3+
    pip

Étapes d'installation

    Cloner le projet

cd monprojet_complete

    Créer un environnement virtuel

python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

    Installer les dépendances

pip install -r requirements.txt

    Configurer MySQL

Créez une base de données MySQL:

CREATE DATABASE research_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

    Configurer les variables d'environnement

Copiez .env.example vers .env et modifiez les valeurs:

cp .env.example .env

Éditez .env avec vos informations MySQL:

DB_NAME=research_platform
DB_USER=votre_utilisateur_mysql
DB_PASSWORD=votre_mot_de_passe_mysql
DB_HOST=localhost
DB_PORT=3306
SECRET_KEY=votre-secret-key-django

    Appliquer les migrations

python manage.py makemigrations
python manage.py migrate

    Créer un superutilisateur

python manage.py createsuperuser

    Lancer le serveur de développement

python manage.py runserver

Le site sera accessible à http://127.0.0.1:8000/
Modèles
Utilisateur

    Profil de chercheur avec informations académiques
    Système de followers/following
    ORCID ID, institution, département

Publication

    Articles, livres, conférences, thèses
    Documents PDF, images de couverture
    DOI, ISBN, métadonnées de publication

Groupe

    Groupes publics/privés/invitation uniquement
    Système de membres avec rôles (membre, modérateur, admin)

Post

    Posts avec texte, images, fichiers
    Likes, commentaires, partages
    Peut être associé à un groupe

Message

    Messages privés entre utilisateurs
    Conversations avec historique
    Fichiers joints

Commentaire

    Commentaires sur posts et publications
    Système de réponses (threading)
    Likes sur commentaires

Notification

    Notifications pour diverses actions
    Système de lecture/non-lecture
    Types: likes, comments, follows, messages, etc.

Technologies Utilisées

    Django 5.0: Framework web Python
    MySQL: Base de données relationnelle
    Pillow: Traitement d'images
    python-dotenv: Gestion des variables d'environnement

Développement
Créer une nouvelle migration

python manage.py makemigrations
python manage.py migrate

Accéder à l'administration Django

http://127.0.0.1:8000/admin/

Collecter les fichiers statiques (production)

python manage.py collectstatic

Licence

Ce projet est sous licence MIT.
