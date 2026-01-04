#!/usr/bin/env python
"""
Script rapide pour tester et configurer la connexion MySQL
"""
import os
import sys
from pathlib import Path

# Charger les variables d'environnement
from dotenv import load_dotenv
load_dotenv()

print("=" * 60)
print("Configuration MySQL pour Django")
print("=" * 60)
print()

# Vérifier si .env existe
if not Path('.env').exists():
    print("✗ Le fichier .env n'existe pas.")
    print("  Créez-le avec les informations MySQL suivantes:")
    print()
    print("  DB_NAME=research_platform")
    print("  DB_USER=root")
    print("  DB_PASSWORD=votre_mot_de_passe")
    print("  DB_HOST=localhost")
    print("  DB_PORT=3306")
    print()
    sys.exit(1)

# Afficher la configuration actuelle (sans le mot de passe)
print("Configuration actuelle:")
print(f"  DB_NAME: {os.getenv('DB_NAME', 'research_platform')}")
print(f"  DB_USER: {os.getenv('DB_USER', 'root')}")
print(f"  DB_PASSWORD: {'***' if os.getenv('DB_PASSWORD') else '(vide)'}")
print(f"  DB_HOST: {os.getenv('DB_HOST', 'localhost')}")
print(f"  DB_PORT: {os.getenv('DB_PORT', '3306')}")
print()

# Tester la connexion
try:
    import pymysql
    pymysql.install_as_MySQLdb()
    
    print("Test de connexion MySQL...")
    
    connection = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        port=int(os.getenv('DB_PORT', '3306')),
        charset='utf8mb4'
    )
    
    print("[OK] Connexion MySQL reussie!")
    print()
    
    db_name = os.getenv('DB_NAME', 'research_platform')
    
    with connection.cursor() as cursor:
        # Vérifier si la base existe
        cursor.execute("SHOW DATABASES LIKE %s", (db_name,))
        result = cursor.fetchone()
        
        if result:
            print(f"[OK] Base de donnees '{db_name}' existe.")
            
            # Se connecter et vérifier les tables
            connection.select_db(db_name)
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if tables:
                print(f"[OK] {len(tables)} table(s) dans la base de donnees.")
            else:
                print("[INFO] Base de donnees vide (pret pour les migrations).")
        else:
            print(f"[ERREUR] Base de donnees '{db_name}' n'existe pas.")
            print()
            create = input(f"Voulez-vous créer la base '{db_name}' maintenant? (o/n): ").strip().lower()
            
            if create in ['o', 'oui', 'y', 'yes']:
                cursor.execute(f"CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                print(f"[OK] Base de donnees '{db_name}' creee!")
            else:
                print(f"Créez-la avec: CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    
    connection.close()
    
    print()
    print("=" * 60)
    print("CONFIGURATION PRÊTE!")
    print("=" * 60)
    print()
    print("Vous pouvez maintenant exécuter:")
    print("  python manage.py migrate")
    print("  python manage.py createsuperuser")
    print("  python manage.py runserver")
    print()
    
except ImportError:
    print("[ERREUR] PyMySQL n'est pas installe.")
    print("  Installez-le avec: pip install pymysql")
    sys.exit(1)
    
except pymysql.Error as e:
    print(f"[ERREUR] Erreur MySQL: {e}")
    print()
    print("Vérifiez:")
    print("1. Que MySQL est démarré")
    print("2. Les identifiants dans .env sont corrects")
    print("3. Que le port MySQL est correct (généralement 3306)")
    sys.exit(1)
    
except Exception as e:
    print(f"[ERREUR] Erreur: {e}")
    sys.exit(1)

