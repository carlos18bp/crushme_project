"""JWT endpoints with the project security policies attached."""

from rest_framework_simplejwt.views import TokenRefreshView

from ..throttles import TokenRefreshRateThrottle


class ThrottledTokenRefreshView(TokenRefreshView):
    throttle_classes = [TokenRefreshRateThrottle]
