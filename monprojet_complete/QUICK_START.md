# Guide de Démarrage Rapide

## Problème: Base de données non créée

Si vous voyez l'erreur `(1049, "Unknown database 'research_platform'")`, vous devez créer la base de données MySQL avant de continuer.

## Solutions

### Option 1: Script PowerShell Automatique (Recommandé)

```powershell
.\create_database.ps1
```

Le script vous guidera pour créer la base de données.

### Option 2: MySQL Workbench ou phpMyAdmin

1. Ouvrez MySQL Workbench ou phpMyAdmin
2. Connectez-vous avec vos identifiants MySQL
3. Créez une nouvelle base de données avec ces paramètres:
   - **Nom**: `research_platform`
   - **Charset**: `utf8mb4`
   - **Collation**: `utf8mb4_unicode_ci`

Ou exécutez cette commande SQL:
```sql
CREATE DATABASE research_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Option 3: Ligne de commande MySQL

```powershell
# Se connecter à MySQL
mysql -u root -p

# Dans MySQL, exécutez:
CREATE DATABASE research_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### Option 4: Via le fichier SQL

```powershell
mysql -u root -p < setup_database.sql
```

## Après la création de la base de données

### 1. Vérifiez le fichier .env

Créez un fichier `.env` à la racine du projet avec:

```env
SECRET_KEY=django-insecure-change-this-in-production-xyz123
DEBUG=True

DB_NAME=research_platform
DB_USER=root
DB_PASSWORD=votre_mot_de_passe_mysql
DB_HOST=localhost
DB_PORT=3306
```

**⚠️ IMPORTANT**: Remplacez `votre_mot_de_passe_mysql` par votre vrai mot de passe MySQL!

### 2. Appliquez les migrations

```powershell
python manage.py migrate
```

### 3. Créez un superutilisateur

```powershell
python manage.py createsuperuser
```

### 4. Lancez le serveur

```powershell
python manage.py runserver
```

Puis ouvrez votre navigateur à: http://127.0.0.1:8000/

## Vérification

Pour vérifier que la base de données existe:

```powershell
mysql -u root -p -e "SHOW DATABASES LIKE 'research_platform';"
```

Si vous voyez `research_platform`, la base de données a été créée avec succès!

