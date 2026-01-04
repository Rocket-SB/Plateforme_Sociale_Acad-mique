# Configuration de la connexion MySQL

## Étape 1: Créer le fichier .env

Créez un fichier `.env` à la racine du projet avec ce contenu :

```env
# Django Settings
SECRET_KEY=django-insecure-change-this-in-production-xyz123
DEBUG=True

# MySQL Database Configuration
DB_NAME=research_platform
DB_USER=root
DB_PASSWORD=votre_mot_de_passe_mysql
DB_HOST=localhost
DB_PORT=3306
```

**⚠️ IMPORTANT** : Remplacez `votre_mot_de_passe_mysql` par votre vrai mot de passe MySQL !

## Étape 2: Créer la base de données MySQL

Si la base de données n'existe pas encore, créez-la :

### Option A: Via MySQL Workbench ou phpMyAdmin
Exécutez cette commande SQL :
```sql
CREATE DATABASE research_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Option B: Via ligne de commande
```powershell
mysql -u root -p -e "CREATE DATABASE research_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### Option C: Via le script SQL
```powershell
mysql -u root -p < setup_database.sql
```

## Étape 3: Tester la connexion

Utilisez le script de test :
```powershell
python quick_setup.py
```

Ou testez directement avec Django :
```powershell
python manage.py check --database default
```

## Étape 4: Appliquer les migrations

Une fois la connexion fonctionnelle :
```powershell
python manage.py migrate
```

## Vérification rapide

Pour vérifier que tout fonctionne :
```powershell
python test_connection.py
```

## Dépannage

### Erreur: "Unknown database"
→ La base de données n'existe pas. Créez-la avec les options ci-dessus.

### Erreur: "Access denied"
→ Vérifiez vos identifiants MySQL dans le fichier `.env`.

### Erreur: "Can't connect to MySQL server"
→ Vérifiez que MySQL est démarré et que le port est correct.

