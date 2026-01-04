from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils.crypto import get_random_string
from simple_history.models import HistoricalRecords


class Groupe(models.Model):
    """Modèle pour les groupes académiques"""
    VISIBILITY_CHOICES = [
        ('public', _('Public')),
        ('private', _('Privé')),
        ('invite_only', _('Sur invitation uniquement')),
    ]

    name = models.CharField(_('nom'), max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_groups',
        verbose_name=_('créateur')
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='member_groups',
        through='GroupMembership',
        verbose_name=_('membres')
    )
    admins = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='admin_groups',
        verbose_name=_('administrateurs')
    )
    visibility = models.CharField(
        _('visibilité'),
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default='public'
    )
    cover_image = models.ImageField(_('image de couverture'), upload_to='groups/covers/', blank=True, null=True)
    icon = models.ImageField(_('icône'), upload_to='groups/icons/', blank=True, null=True)
    member_count = models.PositiveIntegerField(_('nombre de membres'), default=0)
    post_count = models.PositiveIntegerField(_('nombre de posts'), default=0)
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    history = HistoricalRecords()
    mongo_id = models.CharField(max_length=24, null=True, blank=True, unique=True)

    class Meta:
        verbose_name = _('groupe')
        verbose_name_plural = _('groupes')
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class GroupMembership(models.Model):
    """Modèle pour l'adhésion aux groupes"""
    ROLE_CHOICES = [
        ('member', _('Membre')),
        ('moderator', _('Modérateur')),
        ('admin', _('Administrateur')),
    ]

    group = models.ForeignKey(Groupe, on_delete=models.CASCADE, verbose_name=_('groupe'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('utilisateur'))
    role = models.CharField(_('rôle'), max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(_('rejoint le'), auto_now_add=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _('adhésion au groupe')
        verbose_name_plural = _('adhésions aux groupes')
        unique_together = ['group', 'user']
        ordering = ['-joined_at']

    def __str__(self):
        return f"{self.user.username} - {self.group.name}"


def generate_invitation_code():
    """Generate a random invitation code"""
    return get_random_string(length=32)


class GroupInvitation(models.Model):
    """Modèle pour les invitations aux groupes"""
    STATUS_CHOICES = [
        ('pending', _('En attente')),
        ('accepted', _('Acceptée')),
        ('declined', _('Refusée')),
    ]

    group = models.ForeignKey(Groupe, on_delete=models.CASCADE, related_name='invitations', verbose_name=_('groupe'))
    
    # User invitation (for authenticated users requesting access)
    invitee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='group_invitations',
        blank=True,
        null=True,
        verbose_name=_('invité')
    )
    
    # Email invitation (for external users)
    email = models.EmailField(_('email'), blank=True, null=True)
    
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='group_invites_sent',
        verbose_name=_('invité par')
    )
    
    status = models.CharField(
        _('statut'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # FIX: Use the function without parentheses, or use a lambda with length parameter
    code = models.CharField(
        _('code'),
        max_length=32,
        unique=True,
        default=generate_invitation_code  # Use the function without calling it
    )
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    responded_at = models.DateTimeField(_('répondu le'), blank=True, null=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _('invitation au groupe')
        verbose_name_plural = _('invitations aux groupes')
        ordering = ['-created_at']

    def __str__(self):
        invitee_str = self.invitee.username if self.invitee else self.email
        return f"{self.group.name} - {invitee_str} ({self.status})"


class GroupMessage(models.Model):
    """Modèle pour les messages de groupe"""
    group = models.ForeignKey(
        Groupe,
        on_delete=models.CASCADE,
        related_name='chat_messages',
        verbose_name=_('groupe')
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('expéditeur')
    )
    content = models.TextField(_('contenu'))
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _('message de groupe')
        verbose_name_plural = _('messages de groupe')
        ordering = ['created_at']

    def __str__(self):
        return f"Message in {self.group.name} by {self.sender.username}"


mongo_id = models.CharField(max_length=24, null=True, blank=True, unique=True)