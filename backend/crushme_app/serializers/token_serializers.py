"""JWT serializers with database-backed refresh rotation."""

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.utils import datetime_from_epoch


class SerializedTokenRefreshSerializer(TokenRefreshSerializer):
    """Allow exactly one rotation for a refresh token at a time."""

    def validate(self, attrs):
        refresh = self.token_class(attrs['refresh'])

        # Tokens issued before the blacklist app was enabled have no row yet.
        jti = refresh[api_settings.JTI_CLAIM]
        user_id = refresh.payload.get(api_settings.USER_ID_CLAIM)
        user = get_user_model().objects.filter(
            **{api_settings.USER_ID_FIELD: user_id}
        ).first()
        OutstandingToken.objects.get_or_create(
            jti=jti,
            defaults={
                'user': user,
                'created_at': refresh.current_time,
                'token': str(refresh),
                'expires_at': datetime_from_epoch(refresh['exp']),
            },
        )

        with transaction.atomic():
            OutstandingToken.objects.select_for_update().get(jti=jti)
            return super().validate(attrs)
