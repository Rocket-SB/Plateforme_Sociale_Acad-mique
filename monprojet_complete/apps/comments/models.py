from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from simple_history.models import HistoricalRecords


class Commentaire(models.Model):
    """
    Modèle pour les commentaires sur les posts et publications
    """
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('auteur')
    )
    
    # Generic relation pour permettre les commentaires sur différents types de contenu
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    content = models.TextField(_('contenu'))
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='replies',
        blank=True,
        null=True,
        verbose_name=_('commentaire parent')
    )
    
    # Engagement
    like_count = models.PositiveIntegerField(_('nombre de likes'), default=0)
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_comments',
        blank=True,
        verbose_name=_('aimé par')
    )
    
    is_edited = models.BooleanField(_('modifié'), default=False)
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)

    history = HistoricalRecords()
    
    class Meta:
        verbose_name = _('commentaire')
        verbose_name_plural = _('commentaires')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

