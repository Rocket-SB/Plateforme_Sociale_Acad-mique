from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Conversation, Message
from apps.users.models import Utilisateur

@login_required
def chat_interface(request, conversation_id=None):
    """
    Affiche l'interface de chat principale avec la liste des conversations
    et la conversation sélectionnée.
    """
    # Logic from inbox view
    conversations = Conversation.objects.filter(participants=request.user).order_by('-updated_at')
    conversations_data = []
    for conv in conversations:
        other_participant = conv.participants.exclude(id=request.user.id).first()
        last_message = conv.messages.first()
        unread_count = conv.messages.filter(is_read=False, recipient=request.user).count()
        conversations_data.append({
            'conversation': conv,
            'other_participant': other_participant,
            'last_message': last_message,
            'unread_count': unread_count,
        })

    context = {
        'conversations_data': conversations_data,
        'conversation': None,
        'active_conversation_id': conversation_id,
    }

    if conversation_id:
        # Logic from conversation_detail view
        conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
        message_list = conversation.messages.all().order_by('created_at')
        
        # Mark messages as read
        unread_messages = message_list.filter(is_read=False, recipient=request.user)
        for msg in unread_messages:
            msg.is_read = True
            msg.save()
        
        other_participant = conversation.participants.exclude(id=request.user.id).first()
        
        context['conversation'] = conversation
        context['messages'] = message_list
        context['other_participant'] = other_participant

    return render(request, 'messages/chat_interface.html', context)


# @login_required
# def inbox(request):
#     """Liste des conversations"""
#     conversations = Conversation.objects.filter(participants=request.user).order_by('-updated_at')
    
#     # Préparer les données pour chaque conversation
#     conversations_data = []
#     for conv in conversations:
#         other_participant = conv.participants.exclude(id=request.user.id).first()
#         last_message = conv.messages.first()
#         unread_count = conv.messages.filter(is_read=False, recipient=request.user).count()
        
#         conversations_data.append({
#             'conversation': conv,
#             'other_participant': other_participant,
#             'last_message': last_message,
#             'unread_count': unread_count,
#         })
    
#     context = {
#         'conversations_data': conversations_data,
#     }
#     return render(request, 'messages/inbox.html', context)


# @login_required
# def conversation_detail(request, conversation_id):
#     """Détails d'une conversation"""
#     conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
#     message_list = conversation.messages.all().order_by('created_at')
    
#     # Marquer les messages comme lus
#     unread_messages = message_list.filter(is_read=False, recipient=request.user)
#     for msg in unread_messages:
#         msg.is_read = True
#         msg.save()
    
#     # Obtenir l'autre participant
#     other_participant = conversation.participants.exclude(id=request.user.id).first()
    
#     context = {
#         'conversation': conversation,
#         'messages': message_list,
#         'other_participant': other_participant,
#     }
#     return render(request, 'messages/conversation.html', context)


@login_required
def new_conversation(request, user_id):
    """Créer une nouvelle conversation avec un utilisateur"""
    recipient = get_object_or_404(Utilisateur, id=user_id)
    
    # Check if trying to message yourself
    if request.user == recipient:
        messages.error(request, 'Vous ne pouvez pas vous envoyer de message à vous-même.')
        return redirect('users:home')
    
    # Check if users follow each other (mutual follow)
    user_follows_recipient = recipient.followers.filter(id=request.user.id).exists()
    recipient_follows_user = request.user.followers.filter(id=recipient.id).exists()
    
    if not (user_follows_recipient and recipient_follows_user):
        messages.error(request, f'Vous devez vous suivre mutuellement avec {recipient.username} pour envoyer des messages.')
        return redirect('users:profile', pk=recipient.pk)
    
    # Chercher une conversation existante
    conversation = Conversation.objects.filter(participants=request.user).filter(participants=recipient).first()
    
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, recipient)
    
    return redirect('messaging:chat_detail', conversation_id=conversation.id)


@login_required
def user_list(request):
    """Liste des utilisateurs avec qui vous pouvez envoyer des messages (mutual follow)"""
    # Get users who follow you
    followers_ids = request.user.followers.values_list('id', flat=True)
    
    # Get users you follow
    following_ids = request.user.following.values_list('id', flat=True)
    
    # Find mutual follows (intersection)
    mutual_follow_ids = set(followers_ids) & set(following_ids)
    
    # Get user objects for mutual follows
    users = Utilisateur.objects.filter(id__in=mutual_follow_ids).order_by('username')
    
    context = {
        'users': users,
    }
    return render(request, 'messages/user_list.html', context)
