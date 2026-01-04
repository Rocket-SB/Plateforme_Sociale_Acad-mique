from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Groupe
from config.mongodb import groups_coll
from bson.objectid import ObjectId

@receiver(post_save, sender=Groupe)
def sync_group_to_mongo(sender, instance, created, **kwargs):
    """
    Synchronize Groupe instance with MongoDB on save.
    """
    group_collection = groups_coll()

    # --- SAFE HANDLING FOR DATES ---
    # Check if 'updated_at' exists, otherwise default to created_at or None
    created_at_val = instance.created_at.isoformat() if hasattr(instance, 'created_at') else None
    
    if hasattr(instance, 'updated_at'):
        updated_at_val = instance.updated_at.isoformat()
    elif hasattr(instance, 'created_at'):
        updated_at_val = instance.created_at.isoformat()
    else:
        updated_at_val = None

    mongo_doc = {
        'mysql_id': instance.id,
        'name': instance.name,
        'description': instance.description or '',
        # Use getattr with a default value to prevent errors if these fields are missing
        'visibility': getattr(instance, 'visibility', 'public'), 
        'creator_id': str(instance.creator.id) if instance.creator else None,
        
        # Depending on your ManyToMany setup, access might be direct or via a through model.
        # This generic list comprehension is safer:
        'members': [
            {
                'user_id': str(member.id),
                'username': member.username,
                'full_name': member.get_full_name() or member.username,
                # Default role since 'groupmembership_set' might not exist directly on simple ManyToMany
                'role': 'member', 
                'joined_at': None
            }
            for member in instance.members.all() 
        ] if hasattr(instance, 'members') else [],
        
        'stats': {
            'member_count': instance.members.count() if hasattr(instance, 'members') else 0,
            # Check if post_count exists, otherwise 0
            'post_count': getattr(instance, 'post_count', 0)
        },
        
        'created_at': created_at_val,
        'updated_at': updated_at_val
    }

    if instance.mongo_id:
        group_collection.update_one(
            {'_id': ObjectId(instance.mongo_id)},
            {'$set': mongo_doc}
        )
    else:
        result = group_collection.insert_one(mongo_doc)
        # Update without triggering signals again to avoid recursion loop
        Groupe.objects.filter(pk=instance.pk).update(mongo_id=str(result.inserted_id))

@receiver(post_delete, sender=Groupe)
def delete_group_from_mongo(sender, instance, **kwargs):
    """
    Delete Groupe instance from MongoDB on delete.
    """
    if instance.mongo_id:
        group_collection = groups_coll()
        group_collection.delete_one({'_id': ObjectId(instance.mongo_id)})