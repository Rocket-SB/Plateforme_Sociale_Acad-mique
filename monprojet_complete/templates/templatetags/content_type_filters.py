from django import template
from django.contrib.contenttypes.models import ContentType

register = template.Library()


@register.filter
def content_type_id(obj):
    """Retourne l'ID du ContentType d'un objet"""
    return ContentType.objects.get_for_model(obj).id

