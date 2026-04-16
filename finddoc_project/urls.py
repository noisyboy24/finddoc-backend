from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# drf-spectacular importlari
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Asosiy API yo'llari
    path('api/', include('core.urls')),
    
    # Swagger va Redoc (hujjatlashtirish)
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# MEDIA va STATIC fayllarni production da ham serv qilish
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)