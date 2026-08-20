"""JWT endpoints with project security policies attached."""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from ..serializers.token_serializers import SerializedTokenRefreshSerializer
from ..throttles import TokenRefreshRateThrottle


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([TokenRefreshRateThrottle])
def refresh_token(request):
    serializer = SerializedTokenRefreshSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
    except TokenError as exc:
        raise InvalidToken(exc.args[0]) from exc
    return Response(serializer.validated_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([TokenRefreshRateThrottle])
def logout(request):
    """Revoke the presented refresh token without leaking token state."""
    refresh_value = request.data.get('refresh')
    if not isinstance(refresh_value, str) or not refresh_value:
        return Response(
            {'refresh': ['This field is required.']},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        RefreshToken(refresh_value).blacklist()
    except TokenError:
        pass

    return Response(status=status.HTTP_204_NO_CONTENT)
