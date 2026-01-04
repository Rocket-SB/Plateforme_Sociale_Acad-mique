from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            cache.set(f'last_seen_{request.user.id}', timezone.now(), 300) # 5 minutes timeout
        response = self.get_response(request)
        return response
