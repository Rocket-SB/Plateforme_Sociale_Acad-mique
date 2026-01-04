from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from apps.notifications.models import Notification
from .models import Post

@receiver(post_save, sender=Post)
def post_created_notification(sender, instance, created, **kwargs):
    """
    Crée des notifications pour les followers de l'auteur
    lorsqu'un nouveau post est créé.
    """
    if created:
        author = instance.author
        followers = author.followers.all()
        
        # URL du post
        post_url = reverse('posts:detail', kwargs={'pk': instance.pk})
        
        # Message de la notification
        notification_title = f"Nouveau post de {author.full_name}"
        notification_message = f'"{instance.content[:50]}..." a été publié.'
        
        # Créer une notification pour chaque follower
        for follower in followers:
            # Ne pas notifier l'auteur du post lui-même
            if follower != author:
                Notification.objects.create(
                    recipient=follower,
                    sender=author,
                    title=notification_title,
                    message=notification_message,
                    notification_type='new_post',
                    action_url=post_url,
                    related_object=instance
                )
