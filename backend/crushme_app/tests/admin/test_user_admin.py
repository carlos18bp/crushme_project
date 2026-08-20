"""Behavior tests for CrushMe user administration actions."""

from crushme_app.admin import CustomUserAdmin
from crushme_app.models import User
from django.contrib import admin
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory


def test_approve_crush_verification_updates_only_pending_requests(user_factory):
    """Fails if approval changes a non-pending request or leaves a pending request rejected."""
    pending_user = user_factory(
        crush_verification_status='pending',
        crush_rejection_reason='Prior rejection reason',
    )
    rejected_user = user_factory(
        crush_verification_status='rejected',
        crush_rejection_reason='Missing documentation',
    )
    request = RequestFactory().post('/admin/crushme_app/user/')
    SessionMiddleware(lambda _request: None).process_request(request)
    request._messages = FallbackStorage(request)
    user_admin = CustomUserAdmin(User, admin.site)

    user_admin.approve_crush_verification(
        request,
        User.objects.filter(pk__in=[pending_user.pk, rejected_user.pk]),
    )

    pending_user.refresh_from_db()
    rejected_user.refresh_from_db()
    assert (
        pending_user.is_crush,
        pending_user.crush_verification_status,
        pending_user.crush_rejection_reason,
    ) == (True, 'approved', None)
    assert (
        rejected_user.is_crush,
        rejected_user.crush_verification_status,
        rejected_user.crush_rejection_reason,
    ) == (False, 'rejected', 'Missing documentation')
