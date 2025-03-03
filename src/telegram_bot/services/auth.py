from asgiref.sync import sync_to_async
from users.models import User


@sync_to_async
def login_user(email: str, password: str) -> bool:
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return False

    if user.check_password(password):
        return True
    return False
