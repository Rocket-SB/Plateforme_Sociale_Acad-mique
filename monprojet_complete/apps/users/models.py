from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta


class Utilisateur(AbstractUser):
    """
    Modèle utilisateur personnalisé pour les chercheurs académiques
    """
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    bio = models.TextField(_('biography'), blank=True, null=True)
    profile_picture = models.ImageField(_('profile picture'), upload_to='profiles/', blank=True, null=True)
    institution = models.CharField(_('institution'), max_length=255, blank=True, null=True)
    department = models.CharField(_('department'), max_length=255, blank=True, null=True)
    research_interests = models.TextField(_('research interests'), blank=True, null=True)
    website = models.URLField(_('website'), blank=True, null=True)
    orcid_id = models.CharField(_('ORCID ID'), max_length=19, blank=True, null=True)

    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)

    # Relations sociales
    followers = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='following',
        blank=True,
        verbose_name=_('followers')
    )
    saved_profiles = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='saved_by',
        blank=True,
        verbose_name=_('profils sauvegardés')
    )

    history = HistoricalRecords()
    mongo_id = models.CharField(max_length=24, null=True, blank=True, unique=True)

    class Meta:
        verbose_name = _('utilisateur')
        verbose_name_plural = _('utilisateurs')
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.username} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    @property
    def is_online(self):
        last_seen = cache.get(f'last_seen_{self.id}')
        if last_seen and timezone.now() < last_seen + timedelta(minutes=5):
            return True
        return False


mongo_id = models.CharField(max_length=24, null=True, blank=True, unique=True)