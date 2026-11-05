"""
URL configuration for sociosolve_core project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('challenges.urls')),
    path('accounts/', include('accounts.urls')),
    path('solutions/', include('solutions.urls')),
    path('collaboration/', include('collaboration.urls')),
    path('partnerships/', include('partnerships.urls')),
    path('impact/', include('impact.urls')),
    path('ai/', include('ai_services.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler400 = 'challenges.error_views.custom_bad_request_view'
handler403 = 'challenges.error_views.custom_permission_denied_view'
handler404 = 'challenges.error_views.custom_page_not_found_view'
handler500 = 'challenges.error_views.custom_server_error_view'
