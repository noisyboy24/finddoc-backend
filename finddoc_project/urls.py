# D:\BMI\finddoc_project\urls.py - SPECTACULAR BILAN YAKUNIY KOD

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# drf-spectacular dan import
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


# urlpatterns ning YAGONIY E'LONI
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API yo'llari
    path('api/', include('core.urls')), 
    
    # Hujjatlashtirish yo'llari (drf-spectacular)
    
    # 1. Schema faylini yaratish (JSON/YAML)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # 2. Swagger UI
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # 3. ReDoc UI
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# DEBUG=True bo'lganda MEDIA fayllarga kirish imkoniyatini ochish
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    