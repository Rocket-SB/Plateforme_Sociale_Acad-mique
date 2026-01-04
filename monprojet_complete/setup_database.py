#!/usr/bin/env python
"""
Script Python pour configurer automatiquement la connexion MySQL
"""
import os
from getpass import getpass

print("=" * 60)
print("Configuration de la connexion MySQL pour Django")
print("=" * 60)
print()

# Demander les informations de connexion
db_name = input("Nom de la base de données [research_platform]: ").strip() or "research_platform"
db_user = input("Nom d'utilisateur MySQL [root]: ").strip() or "root"
db_password = getpass("Mot de passe MySQL: ")
db_host = input("Hôte MySQL [localhost]: ").strip() or "localhost"
db_port = input("Port MySQL [3306]: ").strip() or "3306"
secret_key = input("Secret Key Django (ou laissez vide pour générer): ").strip()

if not secret_key:
    import secrets
    secret_key = secrets.token_urlsafe(50)

# Contenu du fichier .env
env_content = f"""# Django Settings
SECRET_KEY={secret_key}
DEBUG=True

# MySQL Database Configuration
DB_NAME={db_name}
DB_USER={db_user}
DB_PASSWORD={db_password}
DB_HOST={db_host}
DB_PORT={db_port}
"""

# Écrire le fichier .env
with open('.env', 'w', encoding='utf-8') as f:
    f.write(env_content)

print()
print("✓ Fichier .env créé avec succès!")
print()

# Tester la connexion
print("Test de la connexion MySQL...")
try:
    import pymysql
    pymysql.install_as_MySQLdb()
    
    connection = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        port=int(db_port),
        charset='utf8mb4'
    )
    
    with connection.cursor() as cursor:
        # Vérifier si la base de données existe
        cursor.execute("SHOW DATABASES LIKE %s", (db_name,))
        result = cursor.fetchone()
        
        if result:
            print(f"✓ La base de données '{db_name}' existe déjà.")
        else:
            print(f"✗ La base de données '{db_name}' n'existe pas.")
            create = input(f"\nVoulez-vous créer la base de données '{db_name}' maintenant? (o/n): ").strip().lower()
            
            if create == 'o' or create == 'oui' or create == 'y' or create == 'yes':
                cursor.execute(f"CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                print(f"✓ Base de données '{db_name}' créée avec succès!")
    
    connection.close()
    print()
    print("=" * 60)
    print("CONFIGURATION TERMINÉE!")
    print("=" * 60)
    print()
    print("Prochaines étapes:")
    print("1. python manage.py migrate")
    print("2. python manage.py createsuperuser")
    print("3. python manage.py runserver")
    print()
    
except ImportError:
    print("⚠ PyMySQL n'est pas installé. Installation...")
    os.system("pip install pymysql")
    print("Veuillez réexécuter ce script.")
except Exception as e:
    print(f"✗ Erreur de connexion: {e}")
    print()
    print("Vérifiez:")
    print("- Que MySQL est démarré")
    print("- Vos identifiants MySQL sont corrects")
    print("- Le port MySQL est correct")
    print()
    print("Le fichier .env a été créé, vous pouvez le modifier manuellement.")

