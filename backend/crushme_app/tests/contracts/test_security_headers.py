"""Security-header contract tests."""

from django.conf import settings


def test_responses_cannot_be_embedded():
    """Django must deny embedding CrushMe responses in a frame."""
    expected_policy = 'DENY'

    configured_policy = settings.X_FRAME_OPTIONS

    assert configured_policy == expected_policy
