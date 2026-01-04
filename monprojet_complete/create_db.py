#!/usr/bin/env python
"""
Script pour créer automatiquement la base de données MySQL et vérifier son état.
"""
import os
import sys
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

def main():
    print("=" * 60)
    print("Creation et verification de la base de donnees MySQL")
    print("=" * 60)
    print()

    db_name = os.getenv('DB_NAME', 'research_platform')
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', '')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = int(os.getenv('DB_PORT', '3306'))
    connection = None
    db_conn = None

    try:
        # --- 1. Connect to MySQL server ---
        print(f"Connexion a MySQL ({db_host}:{db_port})...")
        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            port=db_port
        )
        print("[OK] Connecte a MySQL!")
        cursor = connection.cursor()

        # --- 2. Drop the database ---
        print(f"Tentative de suppression de la base de donnees '{db_name}' si elle existe...")
        cursor.execute(f"DROP DATABASE IF EXISTS `{db_name}`")
        print(f"[OK] Base de donnees '{db_name}' supprimee (si elle existait).")

        # --- 3. Create the database ---
        print(f"Creation de la base de donnees '{db_name}'...")
        cursor.execute(
            f"CREATE DATABASE `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        print(f"[OK] Base de donnees '{db_name}' creee avec succes!")
        cursor.close()
        connection.close()

        # --- 4. Verify that the new database is empty ---
        print()
        print("--- Verification Post-Creation ---")
        print(f"Reconnexion a la base de donnees specifique '{db_name}'...")
        db_conn = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            port=db_port,
            database=db_name
        )
        print(f"[OK] Connecte a '{db_name}'.")
        db_cursor = db_conn.cursor()
        
        print("Verification des tables existantes avec 'SHOW TABLES'...")
        db_cursor.execute("SHOW TABLES")
        tables = db_cursor.fetchall()
        
        if tables:
            print("\n[ATTENTION] ERREUR INATTENDUE: La base de données qui vient d'être créée n'est pas vide !")
            print("Tables trouvées :")
            for table in tables:
                print(f"  - {table[0]}")
            sys.exit(1)
        else:
            print("[OK] La base de données est vide, comme attendu.")

        print("\n" + "=" * 60)
        print("SUCCES! La base de donnees est prete et verifiee comme etant vide.")
        print("=" * 60)
        print("\nVous pouvez maintenant exécuter en toute confiance:")
        print("  python manage.py migrate")

    except mysql.connector.Error as err:
        print(f"\n[ERREUR] Une erreur MySQL est survenue: {err}")
        print("\nVérifiez:")
        print("1. Que le service MySQL est demarre.")
        print("2. Que les identifiants dans le fichier .env sont corrects.")
        print(f"3. Que l'utilisateur '{db_user}' a les droits suffisants (CREATE, DROP DATABASE).")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n[ERREUR] Une erreur inattendue est survenue: {e}")
        sys.exit(1)

    finally:
        if connection and connection.is_connected():
            connection.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()

if __name__ == "__main__":
    main()
