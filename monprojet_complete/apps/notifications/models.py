from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from simple_history.models import HistoricalRecords


class Notification(models.Model):
    """
    Modèle pour les notifications des utilisateurs
    """
    TYPE_CHOICES = [
        ('like_post', _('Like sur un post')),
        ('comment_post', _('Commentaire sur un post')),
        ('like_comment', _('Like sur un commentaire')),
        ('follow', _('Nouveau follower')),
        ('message', _('Nouveau message')),
        ('group_invite', _('Invitation à un groupe')),
        ('group_post', _('Nouveau post dans un groupe')),
        ('mention', _('Mention')),
        ('publication_shared', _('Publication partagée')),
        ('comment_reply', _('Réponse à un commentaire')),
        ('publication', _('Nouvelle publication')),
        ('new_post', _('Nouveau post')),
    ]
    
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('destinataire')
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        blank=True,
        null=True,
        verbose_name=_('expéditeur')
    )
    notification_type = models.CharField(_('type'), max_length=50, choices=TYPE_CHOICES)
    
    # Generic relation pour lier la notification à différents types de contenu
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    object_id = models.PositiveIntegerField(blank=True, null=True)
    related_object = GenericForeignKey('content_type', 'object_id')
    
    title = models.CharField(_('titre'), max_length=255)
    message = models.TextField(_('message'))
    action_url = models.URLField(_("URL d'action"), blank=True, null=True)
    is_read = models.BooleanField(_('lu'), default=False)
    read_at = models.DateTimeField(_('lu le'), blank=True, null=True)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', '-created_at']),
        ]
    
    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"
