from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from simple_history.models import HistoricalRecords


class Publication(models.Model):
    """
    Modèle pour les publications de recherche
    """
    TYPE_CHOICES = [
        ('article', _('Article')),
        ('book', _('Livre')),
        ('conference', _('Conférence')),
        ('thesis', _('Thèse')),
        ('preprint', _('Prépublication')),
        ('other', _('Autre')),
    ]
    
    STATUS_CHOICES = [
        ('draft', _('Brouillon')),
        ('published', _('Publié')),
        ('under_review', _('En révision')),
    ]
    
    title = models.CharField(_('titre'), max_length=500)
    abstract = models.TextField(_('résumé'), blank=True, null=True)
    authors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='publications',
        verbose_name=_('auteurs')
    )
    main_author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='authored_publications',
        verbose_name=_('auteur principal')
    )
    publication_type = models.CharField(_('type'), max_length=20, choices=TYPE_CHOICES, default='article')
    status = models.CharField(_('statut'), max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Informations de publication
    journal = models.CharField(_('revue/journal'), max_length=255, blank=True, null=True)
    publisher = models.CharField(_('éditeur'), max_length=255, blank=True, null=True)
    publication_date = models.DateField(_('date de publication'), blank=True, null=True)
    doi = models.CharField(_('DOI'), max_length=255, blank=True, null=True)
    isbn = models.CharField(_('ISBN'), max_length=20, blank=True, null=True)

    citation_count = models.PositiveIntegerField(_('nombre de citations'), default=0)
    
    # Fichiers
    document = models.FileField(_('document'), upload_to='publications/', blank=True, null=True)
    cover_image = models.ImageField(_('image de couverture'), upload_to='publications/covers/', blank=True, null=True)
    
    # Métadonnées
    keywords = models.TextField(_('mots-clés'), blank=True, null=True)
    citation_count = models.PositiveIntegerField(_('nombre de citations'), default=0)
    view_count = models.PositiveIntegerField(_('nombre de vues'), default=0)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)

    history = HistoricalRecords()
    mongo_id = models.CharField(max_length=24, null=True, blank=True, unique=True)


class Citation(models.Model):
    """Modèle pour les citations entre publications"""
    citing_publication = models.ForeignKey(
        Publication,
        on_delete=models.CASCADE,
        related_name='citations_made',
        verbose_name=_('publication citante')
    )
    cited_publication = models.ForeignKey(
        Publication,
        on_delete=models.CASCADE,
        related_name='citations_received',
        verbose_name=_('publication citée')
    )
    citation_text = models.TextField(_('texte de citation'), blank=True, null=True)
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('citation')
        verbose_name_plural = _('citations')
        unique_together = ['citing_publication', 'cited_publication']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.citing_publication.title} → {self.cited_publication.title}"


class PublicationImage(models.Model):
    """Images for publications"""
    publication = models.ForeignKey(
        Publication,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('publication')
    )
    image = models.ImageField(
        _('image'),
        upload_to='publications/images/'
    )
    caption = models.CharField(
        _('légende'),
        max_length=255,
        blank=True,
        null=True
    )
    order = models.PositiveIntegerField(_('ordre'), default=0)
    uploaded_at = models.DateTimeField(_('téléchargé le'), auto_now_add=True)
    
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('image de publication')
        verbose_name_plural = _('images de publication')
        ordering = ['order', '-uploaded_at']
    
    def __str__(self):
        return f"Image for {self.publication.title}"


mongo_id = models.CharField(max_length=24, null=True, blank=True, unique=True)