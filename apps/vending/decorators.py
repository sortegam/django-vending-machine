from functools import wraps
from django.http import JsonResponse
from apps.vending.models import User


def validate_username(func):
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        username = request.data.get('username')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({"error": "Bad credentials"}, status=401)

        return func(self, request, user, *args, **kwargs)

    return wrapper
