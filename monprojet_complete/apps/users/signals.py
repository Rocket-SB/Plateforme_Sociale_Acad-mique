from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Utilisateur
from config.mongodb import users_coll
from bson.objectid import ObjectId

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Utilisateur
from config.mongodb import users_coll
from bson.objectid import ObjectId
from apps.recommendations.neo4j_queries import RecommendationEngine

@receiver(post_save, sender=Utilisateur)
def sync_user_to_mongo_and_neo4j(sender, instance, created, **kwargs):
    """
    Synchronize Utilisateur instance with MongoDB and Neo4j on save.
    """
    # MongoDB Sync
    user_collection = users_coll()

    mongo_doc = {
        'mysql_id': instance.id,
        'username': instance.username,
        'email': instance.email,
        
        'profile': {
            'first_name': instance.first_name or '',
            'last_name': instance.last_name or '',
            'full_name': instance.get_full_name() or instance.username,
            'bio': instance.bio or '',
            'institution': instance.institution or '',
            'profile_picture': instance.profile_picture.url if instance.profile_picture else None
        },
        
        'publication_ids': [
            str(pub.id) for pub in instance.authored_publications.all()
        ],
        
        'group_ids': [
            str(group.id) for group in instance.member_groups.all()
        ],
        
        'stats': {
            'publication_count': instance.authored_publications.count(),
            'citation_count': sum(pub.citation_count for pub in instance.authored_publications.all())
        },
        
        'created_at': instance.date_joined.isoformat(),
        'last_login': instance.last_login.isoformat() if instance.last_login else None
    }

    # Use update_one with upsert=True to prevent DuplicateKeyError
    result = user_collection.update_one(
        {'mysql_id': instance.id},
        {'$set': mongo_doc},
        upsert=True
    )

    if result.upserted_id:
        Utilisateur.objects.filter(pk=instance.pk).update(mongo_id=str(result.upserted_id))

    # Neo4j Sync
    try:
        engine = RecommendationEngine()
        engine.sync_user_to_neo4j(instance.id, instance.username, instance.email)
    except Exception as e:
        print(f"Failed to sync user to Neo4j: {e}")

@receiver(post_delete, sender=Utilisateur)
def delete_user_from_mongo(sender, instance, **kwargs):
    """
    Delete Utilisateur instance from MongoDB on delete.
    """
    if instance.mongo_id:
        user_collection = users_coll()
        user_collection.delete_one({'_id': ObjectId(instance.mongo_id)})

@receiver(post_delete, sender=Utilisateur)
def delete_user_from_mongo(sender, instance, **kwargs):
    """
    Delete Utilisateur instance from MongoDB on delete.
    """
    if instance.mongo_id:
        user_collection = users_coll()
        user_collection.delete_one({'_id': ObjectId(instance.mongo_id)})