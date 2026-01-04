from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Groupe, GroupMembership, GroupInvitation, GroupMessage
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from apps.posts.models import Post
from django.conf import settings

User = get_user_model()


def group_list(request):
    """Liste de tous les groupes - accessible à tous"""
    groups = Groupe.objects.all().select_related('creator').order_by('-created_at')
    
    # User groups only if authenticated
    user_groups = Groupe.objects.filter(members=request.user) if request.user.is_authenticated else Groupe.objects.none()

    context = {
        'groups': groups,
        'user_groups': user_groups,
    }
    return render(request, 'groups/list.html', context)


def group_detail(request, group_id):
    """Détails d'un groupe - accessible à tous"""
    group = get_object_or_404(Groupe, id=group_id)
    
    is_member = request.user.is_authenticated and group.members.filter(id=request.user.id).exists()
    is_admin = request.user.is_authenticated and group.admins.filter(id=request.user.id).exists()
    
    # Check if user has pending invitation request
    invitation_sent = False
    if request.user.is_authenticated:
        invitation_sent = GroupInvitation.objects.filter(
            group=group,
            invitee=request.user,
            status='pending'
        ).exists()
    
    membership = GroupMembership.objects.filter(group=group, user=request.user).first() if request.user.is_authenticated else None
    group_posts = group.posts.all().order_by('-created_at')[:10] if is_member else []
    members = group.members.all()

    context = {
        'group': group,
        'is_member': is_member,
        'is_admin': is_admin,
        'membership': membership,
        'posts': group_posts,
        'invitation_sent': invitation_sent,
        'members': members,
    }
    return render(request, 'groups/detail.html', context)


@login_required
def group_create(request):
    """Créer un nouveau groupe"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        visibility = request.POST.get('visibility', 'public')

        if not name:
            messages.error(request, 'Le nom du groupe est requis.')
            return render(request, 'groups/create.html')

        group = Groupe.objects.create(
            name=name,
            description=description,
            creator=request.user,
            visibility=visibility,
        )

        if 'cover_image' in request.FILES:
            group.cover_image = request.FILES['cover_image']
        if 'icon' in request.FILES:
            group.icon = request.FILES['icon']

        group.save()
        group.admins.add(request.user)
        GroupMembership.objects.create(group=group, user=request.user, role='admin')

        messages.success(request, f'Groupe "{group.name}" créé avec succès!')
        return redirect('groups:detail', group_id=group.id)

    return render(request, 'groups/create.html')


@login_required
def group_join(request, group_id):
    """Rejoindre un groupe public"""
    group = get_object_or_404(Groupe, id=group_id)

    if group.members.filter(id=request.user.id).exists():
        messages.info(request, 'Vous êtes déjà membre de ce groupe.')
        return redirect('groups:detail', group_id=group.id)

    if group.visibility != 'public':
        messages.error(request, 'Vous ne pouvez rejoindre que les groupes publics directement.')
        return redirect('groups:detail', group_id=group.id)

    GroupMembership.objects.create(group=group, user=request.user, role='member')
    group.member_count = group.members.count()
    group.save()

    messages.success(request, f'Vous avez rejoint le groupe "{group.name}"!')
    return redirect('groups:detail', group_id=group.id)


@login_required
def request_group_invite(request, group_id):
    """Demander une invitation à un groupe privé"""
    group = get_object_or_404(Groupe, id=group_id)

    if group.members.filter(id=request.user.id).exists():
        messages.info(request, 'Vous êtes déjà membre de ce groupe.')
        return redirect('groups:detail', group_id=group.id)

    if group.visibility != 'private':
        messages.error(request, 'Ce groupe n\'accepte pas les demandes d\'invitation.')
        return redirect('groups:detail', group_id=group.id)

    if GroupInvitation.objects.filter(group=group, invitee=request.user, status='pending').exists():
        messages.info(request, 'Vous avez déjà une demande en attente pour ce groupe.')
        return redirect('groups:detail', group_id=group.id)

    invitation = GroupInvitation.objects.create(
        group=group,
        invitee=request.user,
        invited_by=None,
        status='pending'
    )

    messages.success(request, 'Votre demande d\'invitation a été envoyée aux administrateurs du groupe!')
    return redirect('groups:detail', group_id=group.id)


@login_required
def group_leave(request, group_id):
    """Quitter un groupe"""
    group = get_object_or_404(Groupe, id=group_id)
    membership = GroupMembership.objects.filter(group=group, user=request.user).first()

    if membership:
        membership.delete()
        group.member_count = group.members.count()
        group.save()
        messages.success(request, f'Vous avez quitté le groupe "{group.name}".')

    return redirect('groups:list')


@login_required
def group_admin(request, group_id):
    """Page d'administration du groupe"""
    group = get_object_or_404(Groupe, id=group_id)

    if not group.admins.filter(id=request.user.id).exists():
        messages.error(request, "Vous n'avez pas la permission d'accéder à la page d'administration.")
        return redirect('groups:detail', group_id=group.id)

    memberships = GroupMembership.objects.filter(group=group).select_related('user')
    pending_invites = GroupInvitation.objects.filter(group=group, status='pending')
    posts = group.posts.all().order_by('-created_at')

    context = {
        'group': group,
        'memberships': memberships,
        'pending_invites': pending_invites,
        'posts': posts,
    }
    return render(request, 'groups/admin.html', context)


@login_required
def accept_invite_request(request, invitation_id):
    """Admin accepte une demande d'invitation"""
    invitation = get_object_or_404(GroupInvitation, id=invitation_id)
    group = invitation.group

    if not group.admins.filter(id=request.user.id).exists():
        messages.error(request, "Permission refusée.")
        return redirect('groups:admin', group_id=group.id)

    if request.method == 'POST':
        if not group.members.filter(id=invitation.invitee.id).exists():
            GroupMembership.objects.create(
                group=group,
                user=invitation.invitee,
                role='member'
            )
            group.member_count = group.members.count()
            group.save()

        invitation.status = 'accepted'
        invitation.save()

        messages.success(request, f'Invitation acceptée pour {invitation.invitee.username}.')
        return redirect('groups:admin', group_id=group.id)

    return render(request, 'groups/invitation_confirm.html', {
        'invitation': invitation,
        'group': group,
        'action': 'accept'
    })


@login_required
def decline_invite_request(request, invitation_id):
    """Admin refuse une demande d'invitation"""
    invitation = get_object_or_404(GroupInvitation, id=invitation_id)
    group = invitation.group

    if not group.admins.filter(id=request.user.id).exists():
        messages.error(request, "Permission refusée.")
        return redirect('groups:admin', group_id=group.id)

    if request.method == 'POST':
        invitation.status = 'declined'
        invitation.save()

        messages.success(request, f'Invitation refusée pour {invitation.invitee.username}.')
        return redirect('groups:admin', group_id=group.id)

    return render(request, 'groups/invitation_confirm.html', {
        'invitation': invitation,
        'group': group,
        'action': 'decline'
    })


@login_required
def remove_member(request, group_id, user_id):
    """Retirer un membre du groupe"""
    group = get_object_or_404(Groupe, id=group_id)
    user_to_remove = get_object_or_404(User, id=user_id)

    if not group.admins.filter(id=request.user.id).exists():
        messages.error(request, "Permission refusée.")
        return redirect('groups:admin', group_id=group.id)

    membership = GroupMembership.objects.filter(group=group, user=user_to_remove).first()
    if membership:
        membership.delete()
        group.member_count = group.members.count()
        group.save()
        messages.success(request, f'Membre {user_to_remove.username} retiré.')

    return redirect('groups:admin', group_id=group.id)


@login_required
@require_POST
def post_delete(request, post_id):
    """Supprimer un post du groupe"""
    post = get_object_or_404(Post, id=post_id)
    group = post.group

    if not group.admins.filter(id=request.user.id).exists():
        messages.error(request, "Vous n'avez pas la permission de supprimer ce post.")
        return redirect('groups:detail', group_id=group.id)

    post.delete()
    messages.success(request, "Post supprimé avec succès.")
    return redirect('groups:detail', group_id=group.id)


@login_required
def group_chat(request, group_id):
    """Chat du groupe"""
    from django.db import connection
    
    group = get_object_or_404(Groupe, id=group_id)
    
    if not group.members.filter(id=request.user.id).exists():
        messages.error(request, "Vous devez être membre pour accéder au chat.")
        return redirect('groups:detail', group_id=group.id)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            try:
                GroupMessage.objects.create(group=group, sender=request.user, content=content)
            except Exception as e:
                messages.error(request, "Erreur lors de l'envoi du message. Veuillez réessayer.")
        return redirect('groups:chat', group_id=group.id)

    try:
        chat_messages = group.chat_messages.all().order_by('created_at')
    except Exception as e:
        # Reconnect if connection lost
        connection.close()
        chat_messages = group.chat_messages.all().order_by('created_at')

    return render(request, 'groups/chat.html', {
        'group': group,
        'chat_messages': chat_messages
    })

@login_required
def send_group_invite(request, group_id):
    """Admin sends invitation to a user for invite-only group"""
    group = get_object_or_404(Groupe, id=group_id)
    
    if not group.admins.filter(id=request.user.id).exists():
        messages.error(request, "Permission refusée.")
        return redirect('groups:detail', group_id=group.id)
    
    if group.visibility != 'invite_only':
        messages.error(request, "Ce groupe n'accepte pas les invitations.")
        return redirect('groups:detail', group_id=group.id)
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        
        if not user_id:
            messages.error(request, 'Veuillez sélectionner un utilisateur.')
            return redirect('groups:send_invite', group_id=group.id)
        
        try:
            user_to_invite = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, 'Utilisateur non trouvé.')
            return redirect('groups:send_invite', group_id=group.id)
        
        if group.members.filter(id=user_to_invite.id).exists():
            messages.error(request, f'{user_to_invite.username} est déjà membre.')
            return redirect('groups:send_invite', group_id=group.id)
        
        if GroupInvitation.objects.filter(
            group=group,
            invitee=user_to_invite,
            status__in=['pending', 'accepted']
        ).exists():
            messages.error(request, f'Une invitation a déjà été envoyée.')
            return redirect('groups:send_invite', group_id=group.id)
        
        invitation = GroupInvitation.objects.create(
            group=group,
            invitee=user_to_invite,
            email=user_to_invite.email,
            invited_by=request.user,
            status='pending'
        )
        
        # ✨ Send notification to invited user
        send_group_invitation_notification(
            user_to_invite,
            group,
            request.user,
            invitation.code
        )
        
        messages.success(request, f'Invitation envoyée à {user_to_invite.username}!')
        return redirect('groups:admin', group_id=group.id)
    
    all_users = User.objects.exclude(id__in=group.members.all())
    
    context = {
        'group': group,
        'available_users': all_users,
    }
    return render(request, 'groups/invite_user.html', context)


def send_group_invitation_notification(user, group, invited_by, code):
    """Send notification about group invitation"""
    from apps.notifications.models import Notification
    
    invitation_link = f"/groups/accept-invite/{code}/"
    
    try:
        group_content_type = ContentType.objects.get_for_model(group)
        Notification.objects.create(
            recipient=user,
            notification_type='group_invite',
            title=f'Invitation au groupe "{group.name}"',
            message=f'{invited_by.get_full_name() or invited_by.username} vous a invité à rejoindre "{group.name}"',
            content_type=group_content_type,
            object_id=group.id,
            action_url=invitation_link,
            is_read=False
        )
    except Exception as e:
        print(f"Erreur lors de la création de la notification: {e}")



@login_required
def accept_group_invite(request, code):
    """User accepts group invitation via link/code"""
    try:
        invitation = GroupInvitation.objects.get(code=code, status='pending')
    except GroupInvitation.DoesNotExist:
        messages.error(request, 'Invitation invalide ou expirée.')
        return redirect('groups:list')
    
    # Check if the logged-in user matches the invitee
    if invitation.invitee.id != request.user.id:
        messages.error(request, "Cette invitation ne vous est pas destinée.")
        return redirect('groups:list')
    
    group = invitation.group
    
    # Check if already member
    if group.members.filter(id=request.user.id).exists():
        messages.info(request, 'Vous êtes déjà membre de ce groupe.')
        return redirect('groups:detail', group_id=group.id)
    
    if request.method == 'POST':
        # Add user to group
        GroupMembership.objects.create(
            group=group,
            user=request.user,
            role='member'
        )
        group.member_count = group.members.count()
        group.save()
        
        # Update invitation status
        invitation.status = 'accepted'
        invitation.save()
        
        messages.success(request, f'Vous avez rejoint le groupe "{group.name}"!')
        return redirect('groups:detail', group_id=group.id)
    
    context = {
        'invitation': invitation,
        'group': group,
    }
    return render(request, 'groups/invitation_accept.html', context)