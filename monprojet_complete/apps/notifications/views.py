from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Notification


@login_required
def notification_list(request):
    """
    Affiche la liste complète des notifications pour l'utilisateur connecté.
    Le contexte pour le dropdown (unread_count, notifications récentes) est géré
    par le context processor.
    """
    all_notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    
    context = {
        'all_notifications': all_notifications,
    }
    return render(request, 'notifications/list.html', context)


@login_required
def notification_mark_read(request, notification_id):
    """Marquer une notification comme lue"""
    from django.shortcuts import redirect, get_object_or_404
    from django.utils import timezone
    
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
    
    return redirect('notifications:list')


@login_required
def notification_mark_all_read(request):
    """Marquer toutes les notifications comme lues"""
    from django.shortcuts import redirect
    from django.utils import timezone
    from django.contrib import messages
    
    updated = Notification.objects.filter(recipient=request.user, is_read=False).update(
        is_read=True,
        read_at=timezone.now()
    )
    
    if updated > 0:
        messages.success(request, f'{updated} notification(s) marquée(s) comme lue(s).')
    else:
        messages.info(request, 'Aucune notification non lue.')
    
    return redirect('notifications:list')
