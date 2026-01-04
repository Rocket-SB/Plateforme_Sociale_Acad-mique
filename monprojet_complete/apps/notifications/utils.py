"""
Utilitaires pour créer des notifications automatiquement
"""
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from .models import Notification
from apps.posts.models import Post
from apps.publications.models import Publication


def create_notification(recipient, notification_type, title, message, sender=None, content_object=None, action_url=None):
    """
    Crée une notification pour un utilisateur
    
    Args:
        recipient: L'utilisateur qui recevra la notification
        notification_type: Le type de notification (voir Notification.TYPE_CHOICES)
        title: Titre de la notification
        message: Message de la notification
        sender: L'utilisateur qui a déclenché la notification (optionnel)
        content_object: L'objet lié à la notification (Post, Commentaire, etc.)
        action_url: L'URL de l'action à effectuer (optionnel)
    """
    if recipient == sender:
        # Ne pas créer de notification si l'utilisateur se notifie lui-même
        return None
    
    notification = Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        title=title,
        message=message,
        action_url=action_url,
    )
    
    # Lier l'objet si fourni
    if content_object:
        notification.content_type = ContentType.objects.get_for_model(content_object)
        notification.object_id = content_object.pk
        notification.save()
    
    return notification


def notify_post_liked(post, liker):
    """Crée une notification lorsqu'un post est liké"""
    if post.author != liker:
        action_url = reverse('posts:detail', kwargs={'pk': post.pk})
        return create_notification(
            recipient=post.author,
            notification_type='like_post',
            title='Nouveau like sur votre post',
            message=f'{liker.full_name or liker.username} a aimé votre post.',
            sender=liker,
            content_object=post,
            action_url=action_url
        )
    return None


def notify_post_commented(post, commenter, comment):
    """Crée une notification lorsqu'un post est commenté"""
    if post.author != commenter:
        action_url = reverse('posts:detail', kwargs={'pk': post.pk}) + f'#comment-{comment.pk}'
        return create_notification(
            recipient=post.author,
            notification_type='comment_post',
            title='Nouveau commentaire sur votre post',
            message=f'{commenter.full_name or commenter.username} a commenté votre post: {comment.content[:50]}...',
            sender=commenter,
            content_object=post,
            action_url=action_url
        )
    return None


def notify_comment_replied(parent_comment, replier, reply):
    """Crée une notification lorsqu'une réponse est faite à un commentaire"""
    if parent_comment.author != replier:
        content_object = parent_comment.content_object
        action_url = None
        if isinstance(content_object, Post):
            action_url = reverse('posts:detail', kwargs={'pk': content_object.pk}) + f'#comment-{reply.pk}'
        elif isinstance(content_object, Publication):
            action_url = reverse('publications:detail', kwargs={'pk': content_object.pk}) + f'#comment-{reply.pk}'

        return create_notification(
            recipient=parent_comment.author,
            notification_type='comment_reply',
            title='Réponse à votre commentaire',
            message=f'{replier.full_name or replier.username} a répondu à votre commentaire.',
            sender=replier,
            content_object=parent_comment,
            action_url=action_url
        )
    return None


def notify_new_message(conversation, sender, recipient, message):
    """Crée une notification lorsqu'un nouveau message est envoyé"""
    action_url = reverse('messaging:chat_detail', kwargs={'conversation_id': conversation.id})
    
    # Raccourcir le message si nécessaire
    content_preview = (message.content[:75] + '...') if len(message.content) > 75 else message.content

    return create_notification(
        recipient=recipient,
        notification_type='message',
        title=f'Nouveau message de {sender.username}',
        message=content_preview,
        sender=sender,
        content_object=conversation,
        action_url=action_url,
    )


def notify_group_post(group, post, poster):
    """Crée une notification lorsqu'un post est publié dans un groupe"""
    # Notifier tous les membres du groupe sauf l'auteur
    action_url = reverse('posts:detail', kwargs={'pk': post.pk})
    notifications = []
    for member in group.members.exclude(id=poster.id):
        notification = create_notification(
            recipient=member,
            notification_type='group_post',
            title=f'Nouveau post dans {group.name}',
            message=f'{poster.full_name or poster.username} a publié dans {group.name}.',
            sender=poster,
            content_object=post,
            action_url=action_url
        )
        if notification:
            notifications.append(notification)
    return notifications


def notify_new_follower(followed_user, follower):
    """Crée une notification lorsqu'un utilisateur est suivi"""
    action_url = reverse('users:profile', kwargs={'pk': follower.pk})
    return create_notification(
        recipient=followed_user,
        notification_type='follow',
        title='Nouveau follower',
        message=f'{follower.full_name or follower.username} vous suit maintenant.',
        sender=follower,
        action_url=action_url
    )
