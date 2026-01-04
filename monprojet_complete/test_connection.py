#!/usr/bin/env python
"""
Script pour tester la connexion MySQL
"""
import os
from dotenv import load_dotenv

load_dotenv()

try:
    import pymysql
    pymysql.install_as_MySQLdb()
    
    print("Test de connexion MySQL...")
    print("-" * 50)
    
    connection = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        port=int(os.getenv('DB_PORT', '3306')),
        charset='utf8mb4'
    )
    
    print("[OK] Connexion a MySQL reussie!")
    
    db_name = os.getenv('DB_NAME', 'research_platform')
    
    with connection.cursor() as cursor:
        cursor.execute("SHOW DATABASES LIKE %s", (db_name,))
        result = cursor.fetchone()
        
        if result:
            print(f"[OK] La base de donnees '{db_name}' existe.")
            
            # Se connecter à la base de données
            connection.select_db(db_name)
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if tables:
                print(f"[OK] {len(tables)} table(s) trouvee(s).")
            else:
                print("[INFO] Aucune table dans la base de donnees (normal avant migrate).")
        else:
            print(f"[ERREUR] La base de donnees '{db_name}' n'existe pas.")
            print(f"  Créez-la avec: CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    
    connection.close()
    print("-" * 50)
    print("Test terminé!")
    
except ImportError:
    print("[ERREUR] PyMySQL n'est pas installe. Installez-le avec: pip install pymysql")
except Exception as e:
    print(f"[ERREUR] Erreur: {e}")
    print("\nVérifiez:")
    print("1. Que MySQL est démarré")
    print("2. Que le fichier .env contient les bonnes informations")
    print("3. Que vos identifiants MySQL sont corrects")

