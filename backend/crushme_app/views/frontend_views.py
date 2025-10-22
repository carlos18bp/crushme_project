"""
Frontend views for serving the Vue.js SPA
Handles all frontend routes and serves the index.html template
"""
from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator


@method_decorator(never_cache, name='dispatch')
class FrontendView(TemplateView):
    """
    Serves the Vue.js frontend application
    All frontend routes are handled by Vue Router
    """
    template_name = 'index.html'
