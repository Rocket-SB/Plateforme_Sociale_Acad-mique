# ##############################################################################
#
#  DEPRECATED SCRIPT
#
#  This script is deprecated and should not be used for ongoing data
#  synchronization. Real-time synchronization is now handled by Django
#  signals in each application (`apps/*/signals.py`).
#
#  This script can be used for a one-time initial migration if the
#  MongoDB database is empty.
#
# ##############################################################################

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

# Maintenant on peut importer les modèles
from pymongo import MongoClient
from apps.publications.models import Publication, Citation
from apps.users.models import Utilisateur
from apps.groups.models import Groupe
from bson import ObjectId
from datetime import datetime

# Connexion MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['research_platform_mongo']

def migrate_publications():
    """Migrer les publications vers MongoDB"""
    pubs_collection = db['publications']
    
    print("🚀 Migration des publications...")
    count = 0
    
    for pub in Publication.objects.all():
        try:
            # Document MongoDB
            mongo_doc = {
                '_id': ObjectId(),
                'mysql_id': pub.id,
                'title': pub.title,
                'abstract': pub.abstract or '',
                'status': pub.status,
                'publication_type': pub.publication_type,
                
                # EMBED: Métadonnées
                'metadata': {
                    'journal': pub.journal or '',
                    'publisher': pub.publisher or '',
                    'publication_date': pub.publication_date.isoformat() if pub.publication_date else None,
                    'doi': pub.doi or '',
                    'isbn': pub.isbn or '',
                    'keywords': [k.strip() for k in pub.keywords.split(',') if k.strip()] if pub.keywords else []
                },
                
                # LINK: Auteur principal
                'main_author_id': str(pub.main_author.id),
                
                # EMBED: Co-auteurs
                'authors': [
                    {
                        'user_id': str(author.id),
                        'username': author.username,
                        'full_name': author.get_full_name() or author.username,
                        'role': 'main_author' if author.id == pub.main_author.id else 'co_author'
                    }
                    for author in pub.authors.all()
                ],
                
                # EMBED: Images
                'images': [
                    {
                        'url': img.image.url if img.image else '',
                        'caption': img.caption or '',
                        'order': img.order
                    }
                    for img in pub.images.all()
                ],
                
                # EMBED: Citations faites
                'citations_made': [
                    {
                        'cited_publication_id': str(cit.cited_publication.id),
                        'cited_publication_mysql_id': cit.cited_publication.id,
                        'cited_title': cit.cited_publication.title,
                        'citation_text': cit.citation_text or '',
                        'created_at': cit.created_at.isoformat()
                    }
                    for cit in pub.citations_made.all()
                ],
                
                # LINK: Cité par (IDs uniquement)
                'cited_by_ids': [
                    str(cit.citing_publication.id)
                    for cit in pub.citations_received.all()
                ],
                
                # Statistiques
                'stats': {
                    'view_count': pub.view_count,
                    'citation_count': pub.citation_count,
                    'download_count': 0
                },
                
                'created_at': pub.created_at.isoformat(),
                'updated_at': pub.updated_at.isoformat()
            }
            
            # Insérer dans MongoDB
            pubs_collection.insert_one(mongo_doc)
            count += 1
            print(f"  ✅ [{count}] {pub.title[:50]}...")
            
        except Exception as e:
            print(f"  ❌ Erreur pour publication {pub.id}: {e}")
    
    print(f"\n✅ {count} publications migrées!")
    return count


def migrate_users():
    """Migrer les utilisateurs vers MongoDB"""
    users_collection = db['users']
    
    print("\n🚀 Migration des utilisateurs...")
    count = 0
    
    for user in Utilisateur.objects.all():
        try:
            mongo_doc = {
                '_id': ObjectId(),
                'mysql_id': user.id,
                'username': user.username,
                'email': user.email,
                
                # EMBED: Profil
                'profile': {
                    'first_name': user.first_name or '',
                    'last_name': user.last_name or '',
                    'full_name': user.get_full_name() or user.username,
                    'bio': user.bio or '',
                    'institution': user.institution or '',
                    'profile_picture': user.profile_picture.url if user.profile_picture else None
                },
                
                # LINK: Publications
                'publication_ids': [
                    str(pub.id) for pub in user.authored_publications.all()
                ],
                
                # LINK: Groupes
                'group_ids': [
                    str(group.id) for group in user.member_groups.all()
                ],
                
                # Stats
                'stats': {
                    'publication_count': user.authored_publications.count(),
                    'citation_count': sum(pub.citation_count for pub in user.authored_publications.all())
                },
                
                'created_at': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
            
            users_collection.insert_one(mongo_doc)
            count += 1
            print(f"  ✅ [{count}] {user.username}")
            
        except Exception as e:
            print(f"  ❌ Erreur pour utilisateur {user.id}: {e}")
    
    print(f"\n✅ {count} utilisateurs migrés!")
    return count


def migrate_groups():
    """Migrer les groupes vers MongoDB"""
    groups_collection = db['groups']
    
    print("\n🚀 Migration des groupes...")
    count = 0
    
    for group in Groupe.objects.all():
        try:
            mongo_doc = {
                '_id': ObjectId(),
                'mysql_id': group.id,
                'name': group.name,
                'description': group.description or '',
                'visibility': group.visibility,
                'creator_id': str(group.creator.id),
                
                # EMBED: Membres
                'members': [
                    {
                        'user_id': str(membership.user.id),
                        'username': membership.user.username,
                        'full_name': membership.user.get_full_name() or membership.user.username,
                        'role': membership.role,
                        'joined_at': membership.joined_at.isoformat()
                    }
                    for membership in group.groupmembership_set.all()
                ],
                
                'stats': {
                    'member_count': group.member_count,
                    'post_count': group.post_count
                },
                
                'created_at': group.created_at.isoformat(),
                'updated_at': group.updated_at.isoformat()
            }
            
            groups_collection.insert_one(mongo_doc)
            count += 1
            print(f"  ✅ [{count}] {group.name}")
            
        except Exception as e:
            print(f"  ❌ Erreur pour groupe {group.id}: {e}")
    
    print(f"\n✅ {count} groupes migrés!")
    return count


def create_indexes():
    """Créer les index MongoDB"""
    print("\n🚀 Création des index...")
    
    # Index pour publications
    db.publications.create_index([('mysql_id', 1)], unique=True)
    db.publications.create_index([('status', 1)])
    db.publications.create_index([('main_author_id', 1)])
    db.publications.create_index([('metadata.keywords', 1)])
    db.publications.create_index([('created_at', -1)])
    
    # Index pour users
    db.users.create_index([('mysql_id', 1)], unique=True)
    db.users.create_index([('username', 1)], unique=True)
    db.users.create_index([('email', 1)])
    
    # Index pour groups
    db.groups.create_index([('mysql_id', 1)], unique=True)
    db.groups.create_index([('name', 1)])
    
    print("✅ Index créés!")


def verify_migration():
    """Vérifier la migration"""
    print("\n🔍 Vérification de la migration...")
    
    mysql_pubs = Publication.objects.count()
    mongo_pubs = db.publications.count_documents({})
    print(f"  Publications: MySQL={mysql_pubs}, MongoDB={mongo_pubs}")
    
    mysql_users = Utilisateur.objects.count()
    mongo_users = db.users.count_documents({})
    print(f"  Utilisateurs: MySQL={mysql_users}, MongoDB={mongo_users}")
    
    mysql_groups = Groupe.objects.count()
    mongo_groups = db.groups.count_documents({})
    print(f"  Groupes: MySQL={mysql_groups}, MongoDB={mongo_groups}")
    
    if mysql_pubs == mongo_pubs and mysql_users == mongo_users and mysql_groups == mongo_groups:
        print("\n✅ Migration vérifiée avec succès!")
    else:
        print("\n⚠️ Attention: Différences détectées!")


if __name__ == '__main__':
    print("=" * 60)
    print("🔄 MIGRATION MySQL → MongoDB")
    print("=" * 60)
    
    try:
        # Effacer les données existantes (optionnel)
        response = input("\n⚠️ Effacer les données MongoDB existantes? (o/n): ")
        if response.lower() == 'o':
            db.publications.delete_many({})
            db.users.delete_many({})
            db.groups.delete_many({})
            print("✅ Collections vidées")
        
        # Migration
        migrate_users()
        migrate_publications()
        migrate_groups()
        create_indexes()
        verify_migration()
        
        print("\n" + "=" * 60)
        print("✅ MIGRATION TERMINÉE!")
        print("=" * 60)
        
        # Afficher un exemple
        print("\n📄 Exemple de publication MongoDB:")
        example = db.publications.find_one()
        if example:
            print(f"  Titre: {example.get('title')}")
            print(f"  Auteurs: {len(example.get('authors', []))}")
            print(f"  Images: {len(example.get('images', []))}")
            print(f"  Citations: {len(example.get('citations_made', []))}")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la migration: {e}")
        import traceback
        traceback.print_exc()
