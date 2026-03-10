from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')), 
    path('', include('apps.core.urls')),
    path('', lambda request: redirect('games:list')),  # Redirect ke halaman games
    path('games/', include('apps.games.urls')),
    path('users/', include('apps.users.urls')),
    path('orders/', include('apps.orders.urls')),
     path('users/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)