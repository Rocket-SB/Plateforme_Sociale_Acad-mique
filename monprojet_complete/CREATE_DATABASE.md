# Instructions pour créer la base de données MySQL

## Option 1: Via MySQL Command Line

1. Connectez-vous à MySQL :
   ```bash
   mysql -u root -p
   ```

2. Exécutez la commande SQL :
   ```sql
   CREATE DATABASE research_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. Quittez MySQL :
   ```sql
   EXIT;
   ```

## Option 2: Via MySQL Workbench ou phpMyAdmin

1. Ouvrez MySQL Workbench ou phpMyAdmin
2. Connectez-vous avec vos identifiants
3. Créez une nouvelle base de données :
   - Nom : `research_platform`
   - Charset : `utf8mb4`
   - Collation : `utf8mb4_unicode_ci`

## Option 3: Via PowerShell (si MySQL est dans le PATH)

```powershell
mysql -u root -p -e "CREATE DATABASE research_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

## Après la création de la base de données

1. Vérifiez que le fichier `.env` contient les bonnes informations :
   ```
   DB_NAME=research_platform
   DB_USER=root
   DB_PASSWORD=votre_mot_de_passe
   DB_HOST=localhost
   DB_PORT=3306
   ```

2. Appliquez les migrations :
   ```bash
   python manage.py migrate
   ```

3. Créez un superutilisateur :
   ```bash
   python manage.py createsuperuser
   ```

