"""
Authentication backend allowing login with either email or username (case-insensitive).
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Authenticates against settings.AUTH_USER_MODEL using either email or username.
    Also supports 'admin' as an alias for 'admin@homebuddy.local'.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if not username or not password:
            return None

        identifier = str(username).strip()

        # 1. Check exact/case-insensitive email or username
        user = UserModel.objects.filter(
            Q(email__iexact=identifier) | Q(username__iexact=identifier)
        ).first()

        # 2. Friendly fallback: 'admin' alias maps to 'admin@homebuddy.local'
        if user is None and identifier.lower() == 'admin':
            user = UserModel.objects.filter(email='admin@homebuddy.local').first()

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
