from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .models import Utilisateur
from django.urls import reverse
from django.db.models import Q, Count

from django.db.models import Sum
from apps.publications.models import Publication



def home(request):
    """Page d'accueil"""
    return render(request, 'users/home.html')


def login_view(request):
    """Vue de connexion"""
    if request.user.is_authenticated:
        return redirect('users:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenue, {user.username}!')
            next_url = request.GET.get('next', 'users:home')
            return redirect(next_url)
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    return render(request, 'users/login.html')


def signup_view(request):
    """Vue d'inscription"""
    if request.user.is_authenticated:
        return redirect('users:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        if password1 != password2:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
            return render(request, 'users/signup.html')
        
        if Utilisateur.objects.filter(username=username).exists():
            messages.error(request, 'Ce nom d\'utilisateur est déjà pris.')
            return render(request, 'users/signup.html')
        
        if Utilisateur.objects.filter(email=email).exists():
            messages.error(request, 'Cet email est déjà utilisé.')
            return render(request, 'users/signup.html')
        
        user = Utilisateur.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )
        
        login(request, user)
        messages.success(request, 'Compte créé avec succès!')
        return redirect('users:profile', pk=user.pk)
    
    return render(request, 'users/signup.html')


@login_required
def logout_view(request):
    """Vue de déconnexion"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté.')
    return redirect('users:login')


@login_required
def profile_view(request, pk):
    """Vue du profil utilisateur"""
    profile_user = get_object_or_404(Utilisateur, pk=pk)
    is_own_profile = request.user == profile_user
    is_following = profile_user.followers.filter(id=request.user.id).exists()
    is_saved = request.user.saved_profiles.filter(id=profile_user.id).exists()
    
    # Suggestions d'utilisateurs à suivre
    # Exclure: l'utilisateur connecté, les utilisateurs déjà suivis, et l'utilisateur du profil
    excluded_ids = list(request.user.following.values_list('id', flat=True))
    excluded_ids.extend([request.user.id, profile_user.id])
    
    suggested_users = Utilisateur.objects.exclude(id__in=excluded_ids).annotate(
        followers_count=Count('followers')
    ).order_by('-followers_count', '-date_joined')[:5]
    
    # Ajouter l'information si chaque utilisateur suggéré est suivi
    for suggested_user in suggested_users:
        suggested_user.is_followed_by_current_user = suggested_user.followers.filter(id=request.user.id).exists()
    
    context = {
        'profile_user': profile_user,
        'is_own_profile': is_own_profile,
        'is_following': is_following,
        'is_saved': is_saved,
        'suggested_users': suggested_users,
    }
    return render(request, 'users/profile.html', context)


@login_required
def profile_edit(request):
    """Vue d'édition du profil"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.bio = request.POST.get('bio', '')
        user.institution = request.POST.get('institution', '')
        user.department = request.POST.get('department', '')
        user.research_interests = request.POST.get('research_interests', '')
        user.website = request.POST.get('website', '')
        user.orcid_id = request.POST.get('orcid_id', '')
        
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        
        user.save()
        messages.success(request, 'Profil mis à jour avec succès!')
        return redirect('users:profile', pk=user.pk)
    
    return render(request, 'users/profile_edit.html')


@login_required
def follow_user(request, pk):
    """Suivre un utilisateur"""
    user_to_follow = get_object_or_404(Utilisateur, pk=pk)
    
    if user_to_follow == request.user:
        messages.error(request, 'Vous ne pouvez pas vous suivre vous-même.')
        return redirect('users:profile', pk=user_to_follow.pk)
    
    if user_to_follow.followers.filter(id=request.user.id).exists():
        messages.info(request, f'Vous suivez déjà {user_to_follow.username}.')
    else:
        user_to_follow.followers.add(request.user)
        
        # Créer une notification
        from apps.notifications.utils import notify_new_follower
        notify_new_follower(user_to_follow, request.user)
        
        messages.success(request, f'Vous suivez maintenant {user_to_follow.username}!')
    
    return redirect('users:profile', pk=user_to_follow.pk)


@login_required
def unfollow_user(request, pk):
    """Ne plus suivre un utilisateur"""
    user_to_unfollow = get_object_or_404(Utilisateur, pk=pk)
    
    if user_to_unfollow.followers.filter(id=request.user.id).exists():
        user_to_unfollow.followers.remove(request.user)
        messages.success(request, f'Vous ne suivez plus {user_to_unfollow.username}.')
    else:
        messages.info(request, f'Vous ne suivez pas {user_to_unfollow.username}.')
    
    return redirect('users:profile', pk=user_to_unfollow.pk)


@login_required
def save_profile(request, pk):
    """Sauvegarder un profil"""
    user_to_save = get_object_or_404(Utilisateur, pk=pk)
    
    if user_to_save == request.user:
        messages.error(request, 'Vous ne pouvez pas sauvegarder votre propre profil.')
        return redirect('users:profile', pk=user_to_save.pk)
    
    if request.user.saved_profiles.filter(id=user_to_save.id).exists():
        messages.info(request, 'Ce profil est déjà sauvegardé.')
    else:
        request.user.saved_profiles.add(user_to_save)
        messages.success(request, f'Profil de {user_to_save.username} sauvegardé!')
    
    return redirect('users:profile', pk=user_to_save.pk)


@login_required
def unsave_profile(request, pk):
    """Retirer un profil des sauvegardes"""
    user_to_unsave = get_object_or_404(Utilisateur, pk=pk)
    
    if request.user.saved_profiles.filter(id=user_to_unsave.id).exists():
        request.user.saved_profiles.remove(user_to_unsave)
        messages.success(request, f'Profil de {user_to_unsave.username} retiré des sauvegardes.')
    else:
        messages.info(request, 'Ce profil n\'est pas dans vos sauvegardes.')
    
    return redirect('users:profile', pk=user_to_unsave.pk)


@login_required
def saved_profiles(request):
    """Liste des profils sauvegardés"""
    saved = request.user.saved_profiles.all().order_by('-date_joined')
    
    context = {
        'saved_profiles': saved,
    }
    return render(request, 'users/saved_profiles.html', context)


@login_required
def profile_view(request, pk):
    profile_user = get_object_or_404(Utilisateur, pk=pk)
    is_own_profile = request.user == profile_user
    is_following = profile_user.followers.filter(id=request.user.id).exists()
    is_saved = request.user.saved_profiles.filter(id=profile_user.id).exists()

    # Suggestions d'utilisateurs à suivre
    excluded_ids = list(request.user.following.values_list('id', flat=True))
    excluded_ids.extend([request.user.id, profile_user.id])

    suggested_users = Utilisateur.objects.exclude(id__in=excluded_ids).annotate(
        followers_count=Count('followers')
    ).order_by('-followers_count', '-date_joined')[:5]

    for suggested_user in suggested_users:
        suggested_user.is_followed_by_current_user = suggested_user.followers.filter(id=request.user.id).exists()

    # Publications authored or co-authored by user (published only)
    user_publications = Publication.objects.filter(authors=profile_user, status='published')

    # Aggregate total views and citations across these publications
    total_reads = user_publications.aggregate(total=Sum('view_count'))['total'] or 0
    total_citations = user_publications.aggregate(total=Sum('citation_count'))['total'] or 0

    context = {
        'profile_user': profile_user,
        'is_own_profile': is_own_profile,
        'is_following': is_following,
        'is_saved': is_saved,
        'suggested_users': suggested_users,
        'publications': user_publications,
        'total_reads': total_reads,
        'total_citations': total_citations,
    }
    return render(request, 'users/profile.html', context)