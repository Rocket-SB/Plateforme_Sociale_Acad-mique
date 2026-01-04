from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from simple_history.models import HistoricalRecords


class Post(models.Model):
    """
    Modèle pour les posts partagés sur la plateforme
    """
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name=_('auteur')
    )
    group = models.ForeignKey(
        'groups.Groupe',
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name=_('groupe')
    )
    content = models.TextField(_('contenu'))
    image = models.ImageField(_('image'), upload_to='posts/', blank=True, null=True)
    file = models.FileField(_('fichier'), upload_to='posts/files/', blank=True, null=True)
    
    # Engagement
    like_count = models.PositiveIntegerField(_('nombre de likes'), default=0)
    comment_count = models.PositiveIntegerField(_('nombre de commentaires'), default=0)
    share_count = models.PositiveIntegerField(_('nombre de partages'), default=0)
    
    # Relations
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_posts',
        blank=True,
        verbose_name=_('aimé par')
    )
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = _('post')
        verbose_name_plural = _('posts')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Post by {self.author.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

