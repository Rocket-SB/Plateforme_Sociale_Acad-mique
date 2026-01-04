# Guide de Configuration Rapide

## 1. Installation des dépendances

```bash
pip install -r requirements.txt
```

**Note importante pour Windows:** Si `mysqlclient` pose problème, utilisez `pymysql` comme alternative:
```bash
pip install pymysql
```

Puis ajoutez dans `config/__init__.py`:
```python
import pymysql
pymysql.install_as_MySQLdb()
```

## 2. Configuration MySQL

### Option A: Via MySQL Workbench ou ligne de commande
```sql
CREATE DATABASE research_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Option B: Utiliser le script fourni
```bash
mysql -u root -p < setup_database.sql
```

## 3. Configuration des variables d'environnement

Créez un fichier `.env` à la racine du projet:

```env
SECRET_KEY=django-insecure-change-this-in-production-xyz123
DEBUG=True

DB_NAME=research_platform
DB_USER=root
DB_PASSWORD=votre_mot_de_passe_mysql
DB_HOST=localhost
DB_PORT=3306
```

## 4. Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## 5. Créer un superutilisateur

```bash
python manage.py createsuperuser
```

## 6. Lancer le serveur

```bash
python manage.py runserver
```

Accédez à:
- Site: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

## Modèles Créés

✅ **Utilisateur** - Profil de chercheur avec followers
✅ **Publication** - Articles, livres, conférences
✅ **Groupe** - Groupes publics/privés avec membres
✅ **Post** - Posts avec likes et commentaires
✅ **Message** - Messages privés avec conversations
✅ **Commentaire** - Commentaires sur posts/publications
✅ **Notification** - Système de notifications

## Prochaines Étapes

1. Développer les vues et templates pour chaque fonctionnalité
2. Ajouter l'authentification et les permissions
3. Implémenter les API REST (optionnel avec Django REST Framework)
4. Ajouter les fonctionnalités de recherche
5. Développer le frontend avec des templates Django

