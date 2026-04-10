# D:\BMI\core\urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    AdminAnalizDamOlishListCreateAPIView,
    AdminAnalizDetailAPIView,
    AdminAnalizNavbatListAPIView,
    AdminShifokorDetailAPIView,
    AdminShifokorListAPIView,
    AdminShifokorNavbatListAPIView,
    RegisterAPIView, 
    LoginAPIView, 
    ShaxsTasdigiCreateAPIView,
    KlinikaListAPIView, 
    KlinikaDetailAPIView,
    ShifokorListAPIView, 
    ShifokorDetailAPIView,
    ShifokorCreateAPIView,
    NavbatCreateAPIView, 
    NavbatlarimListAPIView, 
    NavbatDetailAPIView,
    KlinikaTekshiruviCreateAPIView,
    NavbatKlinikaAdminListAPIView,
    NavbatStatusUpdateAPIView,
    WorkScheduleListCreateAPIView,
    WorkScheduleListAPIView,
    AvailableSlotsAPIView,
    ShifokorNavbatlariAPIView,
    NavbatCancelAPIView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    analiz_available_slots,
    analiz_navbat_yaratish,
    shifokor_day_available,
    analiz_day_available,
    AnalizNavbatlarimListAPIView,
    AnalizNavbatCancelAPIView,
    ProfileAPIView,
    AdminClinicAPIView,
    AdminAnalizListAPIView,
    ShifokorProfileAPIView,
    AdminShifokorCreateAPIView,
    AdminAnalizCreateAPIView,
    AdminDamOlishListCreateAPIView,
    AdminDamOlishDeleteAPIView,
    AdminAnalizWorkScheduleAPIView,
    AssignClinicAdminAPIView,
    AdminShifokorWorkScheduleAPIView,
    AdminAnalizDamOlishDeleteAPIView,
    MutaxassisliklarAPIView,
    AiChatAPIView,
    create_super_admin,
     # <<< BU IMPORT ETISHLAB QOLGAN EDI
)

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Autentifikatsiya
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('shaxs_tasdigi/', ShaxsTasdigiCreateAPIView.as_view(), name='shaxs_tasdigi'),

    # Klinikalar
    path('klinikalar/', KlinikaListAPIView.as_view(), name='klinikalar_list'),
    path('klinikalar/<int:pk>/', KlinikaDetailAPIView.as_view(), name='klinikalar_detail'),

    # Shifokorlar
    path('shifokorlar/', ShifokorListAPIView.as_view(), name='shifokorlar_list'),
    path('shifokorlar/<int:pk>/', ShifokorDetailAPIView.as_view(), name='shifokorlar_detail'),
    path('shifokorlar/create/', ShifokorCreateAPIView.as_view(), name='shifokor-create'),
    path('shifokorlar/ish-grafigi/', WorkScheduleListAPIView.as_view(), name='public-work-schedule'),

    # Navbatlar
    path('navbat_yaratish/', NavbatCreateAPIView.as_view(), name='navbat_yaratish'),
    path('navbatlarim/', NavbatlarimListAPIView.as_view(), name='navbatlarim_list'),
    path('navbatlarim/<int:pk>/', NavbatDetailAPIView.as_view(), name='navbat_detail'),

    # Klinika Admin bo'limi
    path('navbatlar/admin/list/', NavbatKlinikaAdminListAPIView.as_view(), name='navbat-admin-list'),
    path('navbatlar/admin/<int:pk>/update/', NavbatStatusUpdateAPIView.as_view(), name='navbat-admin-update'),
    path('work-schedules/', WorkScheduleListCreateAPIView.as_view(), name='work-schedule-list'),

    # Tekshiruvlar
    path('tekshiruv_narxlari/create/', KlinikaTekshiruviCreateAPIView.as_view(), name='tekshiruv-create'),
    path('available-slots/', AvailableSlotsAPIView.as_view(), name='available-slots'),
    
    # Ma'lum bir navbatni yangilash uchun (PATCH)
    path('navbatlar/bekor-qilish/<int:pk>/', NavbatCancelAPIView.as_view(), name='navbat-cancel'),
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('analiz/available-slots/',analiz_available_slots,name='analiz-available-slots'),
    path('analiz/navbat_yaratish/',analiz_navbat_yaratish,name='analiz-navbat-yaratish'),
    path('shifokor/day-available/',shifokor_day_available,name='shifokor-day-available'),
    path('analiz/day-available/', analiz_day_available,name='analiz-day-available'),
    path('analiz/navbatlarim/',AnalizNavbatlarimListAPIView.as_view(),name='analiz-navbatlarim'),
    path('analiz/navbat-bekor/<int:pk>/',AnalizNavbatCancelAPIView.as_view(),name='analiz-navbat-bekor'),
    path('profile/', ProfileAPIView.as_view(), name='profile'),
    path('admin/clinic/', AdminClinicAPIView.as_view()),
    path('admin/analizlar/', AdminAnalizListAPIView.as_view()),
     # SHIFOKOR
    path('admin/shifokorlar/', AdminShifokorListAPIView.as_view()),
    path('admin/shifokor/<int:pk>/', AdminShifokorDetailAPIView.as_view()),
    path('admin/shifokor/<int:pk>/navbatlar/', AdminShifokorNavbatListAPIView.as_view()),

    # ANALIZ
    path('admin/analizlar/', AdminAnalizListAPIView.as_view()),
    path('admin/analiz/<int:pk>/', AdminAnalizDetailAPIView.as_view()),
    path('admin/analiz/<int:pk>/navbatlar/', AdminAnalizNavbatListAPIView.as_view()),
    path('shifokor/profile/', ShifokorProfileAPIView.as_view()),
    path('shifokor/navbatlar/', ShifokorNavbatlariAPIView.as_view()),
    path('admin/shifokor/create/', AdminShifokorCreateAPIView.as_view()),
    path('admin/analiz/create/', AdminAnalizCreateAPIView.as_view()),
    path('admin/shifokor/<int:pk>/dam-olish/', AdminDamOlishListCreateAPIView.as_view()),
    path('admin/dam-olish/<int:pk>/', AdminDamOlishDeleteAPIView.as_view()),
    path('admin/analiz/<int:pk>/work-schedule/',AdminAnalizWorkScheduleAPIView.as_view()),
    path('admin/analiz/<int:pk>/dam-olish/', AdminAnalizDamOlishListCreateAPIView.as_view()),
    path('super/assign-admin/', AssignClinicAdminAPIView.as_view()),
    path('admin/shifokor/<int:pk>/work-schedule/', AdminShifokorWorkScheduleAPIView.as_view()),
    path('admin/analiz/dam-olish/<int:pk>/', AdminAnalizDamOlishDeleteAPIView.as_view()),
    path('mutaxassisliklar/', MutaxassisliklarAPIView.as_view(), name='mutaxassisliklar'),
    path('ai/chat/', AiChatAPIView.as_view()),
    path("create-admin/", create_super_admin),
    path('api/', include('core.urls')),
    ]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)