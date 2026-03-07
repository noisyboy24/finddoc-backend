from django.contrib import admin
from .models import (
    Klinika, Shifokor, Navbat, Foydalanuvchi, ShaxsTasdigi, AdminProfil, KlinikaTekshiruvi, WorkSchedule, DamOlishKuni, AnalizNavbat, AnalizWorkSchedule, AnalizDamOlishKuni
)
from django.utils.html import format_html 

# ===============================================
# INLINE KLASSINI ANIQLASH
# ===============================================

class KlinikaTekshiruviInline(admin.TabularInline):
    model = KlinikaTekshiruvi
    extra = 1
    fields = ('nom', 'narx', 'xona_raqami', 'qavat_raqami', 'ish_vaqti')


# ===============================================
# 1. SHIFOKOR ADMIN
# ===============================================
@admin.register(Shifokor)
class ShifokorAdmin(admin.ModelAdmin):
    # 'user' maydonini ham list_display ga qo'shdik
    list_display = (
        'id', 'user', 'ism', 'familiya', 'mutaxassislik', 'klinika', 'qabul_narxi', 'rasm_preview'
    )
    search_fields = ('familiya', 'ism', 'mutaxassislik')
    list_filter = ('klinika', 'mutaxassislik', 'jinsi')
    # Tahrirlash oynasida user tanlash imkonini beramiz
    raw_id_fields = ('user',) 
    
    def rasm_preview(self, obj):
        if obj.rasm:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />', obj.rasm.url)
        return "Rasm yo'q"
    rasm_preview.short_description = 'Rasm'


# ===============================================
# 2. KLINIKA ADMIN 
# ===============================================
@admin.register(Klinika)
class KlinikaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'manzil', 'telefon', 'logo_preview')
    search_fields = ('nom', 'manzil')
    inlines = [KlinikaTekshiruviInline]
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />', obj.logo.url)
        return "Logo yo'q"
    logo_preview.short_description = 'Logo'


# ===============================================
# 3. KLINIKA TEKSHIRUVI ADMIN
# ===============================================
@admin.register(KlinikaTekshiruvi)
class KlinikaTekshiruviAdmin(admin.ModelAdmin):
    list_display = ('klinika', 'nom', 'narx', 'xona_raqami', 'qavat_raqami')
    list_filter = ('klinika',)
    search_fields = ('nom',)


# ===============================================
# 4. NAVBAT ADMIN (Shifokorlar filtri bilan)
# ===============================================
@admin.register(Navbat)
class NavbatAdmin(admin.ModelAdmin):
    list_display = ('id', 'foydalanuvchi', 'shifokor', 'vaqt', 'status')
    list_filter = ('status', 'vaqt')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Superadmin hamma narsani ko'radi
        if request.user.is_superuser:
            return qs
        # Shifokor faqat o'z navbatlarini ko'radi
        if hasattr(request.user, 'shifokor_profil'):
            return qs.filter(shifokor=request.user.shifokor_profil)
        return qs.none()


# ===============================================
# 5. ISH GRAFIGI ADMIN
# ===============================================
@admin.register(WorkSchedule)
class WorkScheduleAdmin(admin.ModelAdmin):
    list_display = ('shifokor', 'kun_boshlanishi', 'kun_tugashi', 'ish_boshlanishi', 'ish_yakuni')
    list_filter = ('shifokor', 'kun_boshlanishi', 'kun_tugashi')


# ===============================================
# 6. BOSHQA MODELLARNI RO'YXATDAN O'TKAZISH
# ===============================================
@admin.register(Foydalanuvchi)
class FoydalanuvchiAdmin(admin.ModelAdmin):
    list_display = ('ism', 'get_email', 'tel_raqam')

    def get_email(self, obj):
        return obj.user.email if obj.user else None

    get_email.short_description = 'Email'

admin.site.register(ShaxsTasdigi)
admin.site.register(AdminProfil)

@admin.register(DamOlishKuni) # 2. Modelni admin panelga ulang
class DamOlishKuniAdmin(admin.ModelAdmin):
    list_display = ('shifokor', 'sana', 'sabab')
    list_filter = ('shifokor', 'sana')

@admin.register(AnalizNavbat)
class AnalizNavbatAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'foydalanuvchi',
        'analiz',
        'sana',
        'vaqt',
        'status',
    )
    list_filter = ('status', 'sana')
    search_fields = ('foydalanuvchi__ism', 'analiz__nom')

@admin.register(AnalizWorkSchedule)
class AnalizWorkScheduleAdmin(admin.ModelAdmin):
    list_display = (
        'analiz',
        'kun_boshlanishi',
        'kun_tugashi',
        'ish_boshlanishi',
        'ish_yakuni',
        'qabul_davomiyligi',
    )
    list_filter = ('analiz',)

@admin.register(AnalizDamOlishKuni)
class AnalizDamOlishKuniAdmin(admin.ModelAdmin):
    list_display = ('analiz', 'sana', 'sabab')
    list_filter = ('analiz', 'sana')
    search_fields = ('analiz__nom',)


