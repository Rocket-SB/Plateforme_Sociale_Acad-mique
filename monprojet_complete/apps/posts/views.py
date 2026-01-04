from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post
from apps.groups.models import Groupe


def post_list(request):
    """Liste de tous les posts - accessible à tous"""
    posts = Post.objects.all().order_by('-created_at')
    
    # User posts only if authenticated
    user_posts = Post.objects.filter(author=request.user).order_by('-created_at') if request.user.is_authenticated else Post.objects.none()
    
    context = {
        'posts': posts,
        'user_posts': user_posts,
    }
    return render(request, 'posts/list.html', context)


def post_detail(request, pk):
    """Détails d'un post - accessible à tous"""
    post = get_object_or_404(Post, pk=pk)
    is_author = request.user.is_authenticated and post.author == request.user
    is_liked = post.liked_by.filter(id=request.user.id).exists() if request.user.is_authenticated else False
    
    # Récupérer les commentaires
    from apps.comments.models import Commentaire
    from django.contrib.contenttypes.models import ContentType
    
    content_type = ContentType.objects.get_for_model(Post)
    comments = Commentaire.objects.filter(
        content_type=content_type,
        object_id=post.id
    ).order_by('-created_at')
    
    # Get other posts from the same author
    author_other_posts = Post.objects.filter(author=post.author).exclude(pk=post.pk).order_by('-created_at')[:3]
    
    context = {
        'post': post,
        'is_author': is_author,
        'is_liked': is_liked,
        'comments': comments,
        'author_other_posts': author_other_posts,
    }
    return render(request, 'posts/detail.html', context)


@login_required
def post_create(request):
    """Créer un nouveau post"""
    groups = Groupe.objects.filter(members=request.user)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        group_id = request.POST.get('group', '') or None
        
        if not content:
            messages.error(request, 'Le contenu est requis.')
            context = {'groups': groups}
            return render(request, 'posts/create.html', context)
        
        post = Post.objects.create(
            author=request.user,
            content=content,
            group_id=group_id if group_id else None,
        )
        
        if 'image' in request.FILES:
            post.image = request.FILES['image']
        if 'file' in request.FILES:
            post.file = request.FILES['file']
        
        post.save()
        
        # Notifier les membres du groupe si le post est dans un groupe
        if post.group:
            from apps.notifications.utils import notify_group_post
            notify_group_post(post.group, post, request.user)
        
        messages.success(request, 'Post créé avec succès!')
        return redirect('posts:detail', pk=post.pk)
    
    context = {
        'groups': groups,
    }
    return render(request, 'posts/create.html', context)


@login_required
def post_like(request, pk):
    """Aimer/Ne plus aimer un post"""
    post = get_object_or_404(Post, pk=pk)
    
    if post.liked_by.filter(id=request.user.id).exists():
        post.liked_by.remove(request.user)
        post.like_count = max(0, post.like_count - 1)
        messages.info(request, 'Vous n\'aimez plus ce post.')
    else:
        post.liked_by.add(request.user)
        post.like_count += 1
        messages.success(request, 'Vous aimez ce post!')
        
        # Créer une notification pour l'auteur du post
        if post.author != request.user:
            from apps.notifications.utils import notify_post_liked
            notify_post_liked(post, request.user)
    
    post.save(update_fields=['like_count'])
    
    # Redirect back to the previous page or post detail
    return redirect(request.META.get('HTTP_REFERER', 'posts:detail'), pk=post.pk) if 'HTTP_REFERER' in request.META else redirect('posts:detail', pk=post.pk)


@login_required
def post_delete(request, pk):
    """Supprimer un post"""
    post = get_object_or_404(Post, pk=pk)
    
    if post.author != request.user:
        messages.error(request, 'Vous ne pouvez supprimer que vos propres posts.')
        return redirect('posts:detail', pk=post.pk)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post supprimé avec succès!')
        return redirect('posts:list')
    
    context = {
        'post': post,
    }
    return render(request, 'posts/delete.html', context)
