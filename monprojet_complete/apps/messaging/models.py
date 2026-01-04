from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from simple_history.models import HistoricalRecords


class Conversation(models.Model):
    """
    Modèle pour les conversations entre utilisateurs
    """
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='conversations',
        verbose_name=_('participants')
    )
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('conversation')
        verbose_name_plural = _('conversations')
        ordering = ['-updated_at']
    
    def __str__(self):
        participants_list = ', '.join([p.username for p in self.participants.all()[:3]])
        return f"Conversation: {participants_list}"


class Message(models.Model):
    """
    Modèle pour les messages privés entre utilisateurs
    """
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('conversation')
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name=_('expéditeur')
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name=_('destinataire')
    )
    content = models.TextField(_('contenu'))
    file = models.FileField(_('fichier'), upload_to='messages/files/', blank=True, null=True)
    is_read = models.BooleanField(_('lu'), default=False)
    read_at = models.DateTimeField(_('lu le'), blank=True, null=True)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)

    history = HistoricalRecords()
    
    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        ordering = ['-created_at']
    
    def __str__(self):
        return ""

