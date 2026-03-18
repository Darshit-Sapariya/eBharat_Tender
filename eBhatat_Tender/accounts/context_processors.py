from .models import Notification

def notifications(request):
    """
    Context processor to add notifications and unread count to all templates.
    Requires an authenticated user.
    """
    if request.user.is_authenticated:
        user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        unread_count = user_notifications.filter(is_read=False).count()
        return {
            'notifications': user_notifications,
            'unread_count': unread_count,
        }
    return {
        'notifications': [],
        'unread_count': 0,
    }
