from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Publication
from config.mongodb import publications_coll
from bson.objectid import ObjectId

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Publication
from config.mongodb import publications_coll
from bson.objectid import ObjectId
from apps.recommendations.neo4j_queries import RecommendationEngine

@receiver(post_save, sender=Publication)
def sync_publication_to_mongo_and_neo4j(sender, instance, created, **kwargs):
    """
    Synchronize Publication instance with MongoDB and Neo4j on save.
    """
    publication_collection = publications_coll()
    
    # Prepare the document for MongoDB
    mongo_doc = {
        'mysql_id': instance.id,
        'title': instance.title,
        'abstract': instance.abstract or '',
        'status': instance.status,
        'publication_type': instance.publication_type,
        
        # EMBED: Métadonnées
        'metadata': {
            'journal': instance.journal or '',
            'publisher': instance.publisher or '',
            'publication_date': instance.publication_date.isoformat() if instance.publication_date else None,
            'doi': instance.doi or '',
            'isbn': instance.isbn or '',
            'keywords': [k.strip() for k in instance.keywords.split(',') if k.strip()] if instance.keywords else []
        },
        
        # LINK: Auteur principal
        'main_author_id': str(instance.main_author.id),
        
        # EMBED: Co-auteurs
        'authors': [
            {
                'user_id': str(author.id),
                'username': author.username,
                'full_name': author.get_full_name() or author.username,
                'role': 'main_author' if author.id == instance.main_author.id else 'co_author'
            }
            for author in instance.authors.all()
        ],
        
        # EMBED: Images
        'images': [
            {
                'url': img.image.url if img.image else '',
                'caption': img.caption or '',
                'order': img.order
            }
            for img in instance.images.all()
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
            for cit in instance.citations_made.all()
        ],
        
        # LINK: Cité par (IDs uniquement)
        'cited_by_ids': [
            str(cit.citing_publication.id)
            for cit in instance.citations_received.all()
        ],
        
        # Statistiques
        'stats': {
            'view_count': instance.view_count,
            'citation_count': instance.citation_count,
            'download_count': 0 # This needs to be implemented
        },
        
        'created_at': instance.created_at.isoformat(),
        'updated_at': instance.updated_at.isoformat()
    }

    # Use find_one_and_update with upsert=True to handle both insert and update
    result = publication_collection.find_one_and_update(
        {'mysql_id': instance.id},
        {'$set': mongo_doc},
        upsert=True,
        return_document=True  # Return the new or updated document
    )

    # If the mongo_id in the instance is not set, update it
    if not instance.mongo_id and result:
        # Update the instance without triggering post_save again
        Publication.objects.filter(pk=instance.pk).update(mongo_id=str(result['_id']))

    # Neo4j Sync
    if instance.status == 'published':
        try:
            engine = RecommendationEngine()
            topics = [k.strip() for k in instance.keywords.split(',') if k.strip()] if instance.keywords else []
            engine.sync_publication_to_neo4j(instance.id, instance.title, topics)
        except Exception as e:
            print(f"Failed to sync publication to Neo4j: {e}")

@receiver(post_delete, sender=Publication)
def delete_publication_from_mongo(sender, instance, **kwargs):
    """
    Delete Publication instance from MongoDB on delete.
    """
    if instance.mongo_id:
        publication_collection = publications_coll()
        publication_collection.delete_one({'_id': ObjectId(instance.mongo_id)})


@receiver(post_delete, sender=Publication)
def delete_publication_from_mongo(sender, instance, **kwargs):
    """
    Delete Publication instance from MongoDB on delete.
    """
    if instance.mongo_id:
        publication_collection = publications_coll()
        publication_collection.delete_one({'_id': ObjectId(instance.mongo_id)})
