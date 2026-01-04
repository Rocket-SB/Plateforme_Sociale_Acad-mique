from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from .models import Commentaire


@login_required
def comment_create(request):
    """Créer un commentaire"""
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        content_type_id = request.POST.get('content_type_id')
        object_id = request.POST.get('object_id')
        parent_id = request.POST.get('parent_id') or None
        
        if not content:
            messages.error(request, 'Le contenu du commentaire est requis.')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        try:
            content_type = ContentType.objects.get_for_id(int(content_type_id))
            model_class = content_type.model_class()
            content_object = model_class.objects.get(pk=int(object_id))
        except (ContentType.DoesNotExist, ValueError, TypeError, AttributeError) as e:
            messages.error(request, 'Objet introuvable.')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        comment = Commentaire.objects.create(
            author=request.user,
            content_type=content_type,
            object_id=object_id,
            content=content,
            parent_id=parent_id
        )
        
        # Créer des notifications
        from apps.notifications.utils import notify_post_commented, notify_comment_replied
        
        if parent_id:
            # Réponse à un commentaire
            parent_comment = get_object_or_404(Commentaire, pk=parent_id)
            notify_comment_replied(parent_comment, request.user, comment)
        else:
            # Commentaire sur un post
            if content_type.model == 'post':
                from apps.posts.models import Post
                post = get_object_or_404(Post, pk=object_id)
                notify_post_commented(post, request.user, comment)
        
        messages.success(request, 'Commentaire ajouté avec succès!')
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    return redirect('/')
