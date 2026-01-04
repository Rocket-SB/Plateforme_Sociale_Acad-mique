from config.mongodb import publications_collection, users_collection
from bson import ObjectId

def get_publication_from_mongo(mysql_id):
    """Récupérer une publication depuis MongoDB"""
    return publications_collection().find_one({'mysql_id': mysql_id})

def search_publications_mongo(keywords):
    """Rechercher par mots-clés"""
    return publications_collection().find({
        'metadata.keywords': {'$in': keywords},
        'status': 'published'
    }).sort('stats.citation_count', -1).limit(20)

def get_user_publications_mongo(user_id):
    """Publications d'un utilisateur"""
    return publications_collection().find({
        'main_author_id': str(user_id)
    }).sort('created_at', -1)
