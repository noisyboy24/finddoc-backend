# D:\BMI\core\models.py - TO'LIQ VA YAKUNIY TUZATILGAN KOD

from django.db import models
from django.contrib.auth.models import User 
from django.core.validators import MinValueValidator
from django.conf import settings
from multiselectfield import MultiSelectField
from django.db.models import Q

# --- Global Choices ---
JINS_CHOICES = [
    ('E', 'Erkak'),
    ('A', 'Ayol'),
]

TEKSHIRUV_TURLARI = [
    ('A', 'Analiz (Tahlil)'),
    ('T', 'Tibbiy tekshiruv (UZI, MRT, KT)')
]


# =========================================================================
# 1. FOYDALANUVCHI MODELLARI
# =========================================================================

class Foydalanuvchi(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    ism = models.CharField(max_length=150)
    
    tel_raqam = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True) 
    
    class Meta:
        verbose_name = "Foydalanuvchi Profili"
        verbose_name_plural = "Foydalanuvchilar Profil"

    def __str__(self):
        return self.ism

class ShaxsTasdigi(models.Model):
    """Foydalanuvchini Passport yoki JSHSHIR orqali tasdiqlash uchun model."""
    foydalanuvchi = models.OneToOneField(Foydalanuvchi, on_delete=models.CASCADE, primary_key=True, related_name='shaxsiy_tasdiq')
    
    passport_seriya_raqam = models.CharField(max_length=15, unique=True, null=True, blank=True) 
    
    jshshir = models.CharField(max_length=14, unique=True, null=True, blank=True)

    tasdiqlangan_sana = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Shaxsni Tasdiqlash"
        verbose_name_plural = "Shaxsni Tasdiqlash"

    def __str__(self):
        return f"Tasdiq: {self.foydalanuvchi.ism}"

class KlinikaTekshiruvi(models.Model):
    """
    Har bir klinika uchun uning o'zi yaratgan, narx belgilagan 
    va xona ma'lumotlari mavjud bo'lgan analiz/tekshiruvlar modeli.
    """
    # Bog'lanishlar
    klinika = models.ForeignKey(
        'Klinika', # Klinika modeliga bog'lanish
        on_delete=models.CASCADE,
        related_name='tekshiruvlar'
    )
    
    # Asosiy ma'lumotlar (Analiz/Tekshiruv nomidan)
    nom = models.CharField(max_length=150, verbose_name="Tekshiruv nomi")
    
    # Qo'shimcha ma'lumotlar (Narxlar modelidan olingan)
    narx = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Tekshiruv narxi"
    )
    
    # Qo'shimcha ma'lumotlar (Siz so'ragan)
    xona_raqami = models.CharField(max_length=10, blank=True, null=True)
    qavat_raqami = models.SmallIntegerField(blank=True, null=True)
    ish_vaqti = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="Tekshiruv vaqti oralig'i"
    )

    def __str__(self):
        return f"{self.klinika.nom} - {self.nom} ({self.narx})"

    class Meta:
        verbose_name = "Klinika Tekshiruvi/Analizi"
        verbose_name_plural = "Klinika Tekshiruvlari/Analizlari"
        # Bir klinikada bir xil nomli tekshiruv qayta bo'lishini cheklash
        unique_together = ('klinika', 'nom')
# =========================================================================
# 2. KLINIKA MODELLARI (Kengaytirilgan)
# =========================================================================

class Klinika(models.Model):
    nom = models.CharField(max_length=255)
    manzil = models.CharField(max_length=255)
    telefon = models.CharField(max_length=20)
    
    logo = models.ImageField(upload_to='klinika_logolari/', blank=True, null=True)
    ish_vaqti = models.CharField(max_length=100, default='Du-Sha 08:00-20:00')
    
    # Google Maps yoki Yandex uchun koordinatalar
    lat = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True) # Kenglik (Latitude)
    lon = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True) # Uzunlik (Longitude)
    
    class Meta:
        verbose_name = "Klinika"
        verbose_name_plural = "Klinikalar"

    def __str__(self):
        return self.nom


# =========================================================================
# 3. SHIFOKOR VA NAVBAT MODELLARI 
# =========================================================================

class Shifokor(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='shifokor_profil',
        null=True, 
        blank=True,
        verbose_name="Foydalanuvchi (Login/Parol)"
    )
    familiya = models.CharField(max_length=100, verbose_name="Familiyasi")
    ism = models.CharField(max_length=100, verbose_name="Ismi")
    sharif = models.CharField(max_length=100, verbose_name="Sharifi", blank=True, null=True)
    mutaxassislik = models.CharField(max_length=100)
    klinika = models.ForeignKey(Klinika, on_delete=models.CASCADE)

    ish_staji = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    jinsi = models.CharField(max_length=1, choices=JINS_CHOICES, default='E')
    qabul_narxi = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    rasm = models.ImageField(upload_to='shifokor_rasmlari/', blank=True, null=True)
    ish_vaqti = models.CharField(max_length=100, default='Du-Ju 09:00-17:00') 
    ish_kuni = models.CharField(max_length=255, default='Dushanba, Seshanba, Chorshanba, Payshanba, Juma, Shanba')

    class Meta:
        verbose_name = "Shifokor"
        verbose_name_plural = "Shifokorlar"

    def __str__(self):
        return f"{self.ism} ({self.mutaxassislik})"
    qavat = models.IntegerField(
        default=1, 
        verbose_name="Qabul qavati", 
        help_text="Shifokor qabul qiladigan bino qavati"
    )
    xona_raqami = models.CharField(
        max_length=10, 
        default='101', 
        verbose_name="Xona raqami", 
        help_text="Shifokor qabul qiladigan xona raqami"
    )


class Navbat(models.Model):
    # Navbat holatlari uchun variantlar
    STATUS_CHOICES = [
        ('tasdiqlandi', 'Tasdiqlandi'),
        ('bekor_qilindi', 'Bekor qilindi'),
    ]

    shifokor = models.ForeignKey(Shifokor, on_delete=models.CASCADE)
    foydalanuvchi = models.ForeignKey(Foydalanuvchi, on_delete=models.CASCADE)
    vaqt = models.DateTimeField()
    
    # BooleanField o'rniga CharField ishlatamiz (status uchun)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='tasdiqlandi'
    )

    class Meta:
          constraints = [
            models.UniqueConstraint(
                fields=['shifokor', 'vaqt'],
                condition=Q(status='tasdiqlandi'),
                name='unique_active_doctor_slot'
            )
        ]

    def __str__(self):
        # modelda .ism maydoni borligiga qarab ism yoki foydalanuvchi.user.username ishlating
        return f"{self.foydalanuvchi} - {self.shifokor} ({self.vaqt.strftime('%Y-%m-%d %H:%M')})"
    
    
# =========================================================================
# 4. ADMIN PROFIL MODELI (MUSTAQIL QILINDI)
# =========================================================================

class AdminProfil(models.Model):
    """
    Klinika adminlari, menejerlar yoki SuperAdminlar uchun profil.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_profil')
    
    klinika = models.ForeignKey(
        Klinika, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Admin qaysi klinikaga bog'langan"
    )
    
    ROL_TANLOVLARI = [
        ('klinika_admin', 'Klinika Administratsiyasi'),
        ('super_admin', 'Super Admin'),
    ]
    rol = models.CharField(max_length=20, choices=ROL_TANLOVLARI, default='klinika_admin')
    
    def __str__(self):
        return f"Admin: {self.user.username} ({self.rol})"
    
    class Meta:
        verbose_name = "Admin Profil"
        verbose_name_plural = "Admin Profillari"

        # core/models.py

class WorkSchedule(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Dushanba'),
        (1, 'Seshanba'),
        (2, 'Chorshanba'),
        (3, 'Payshanba'),
        (4, 'Juma'),
        (5, 'Shanba'),
        (6, 'Yakshanba'),
    ]

    shifokor = models.ForeignKey('Shifokor', on_delete=models.CASCADE, related_name='ish_grafiklari')
    
    # Hafta kunlari oralig'i (Masalan: Du-Ju yoki Du-Sha)
    kun_boshlanishi = models.IntegerField(choices=DAYS_OF_WEEK, default=0, verbose_name="Boshlanish kuni")
    kun_tugashi = models.IntegerField(choices=DAYS_OF_WEEK, default=4, verbose_name="Tugash kuni")
    
    ish_boshlanishi = models.TimeField(verbose_name="Ish boshlanishi")
    ish_yakuni = models.TimeField(verbose_name="Ish yakuni")
    tushlik_boshlanishi = models.TimeField(null=True, blank=True, default="13:00")
    tushlik_tugashi = models.TimeField(null=True, blank=True, default="14:00")
    qabul_davomiyligi = models.PositiveIntegerField(
        default=30, 
        help_text="Har bir bemor uchun ajratilgan vaqt (daqiqa)"
    )

    class Meta:
        verbose_name = "Ish grafigi"
        verbose_name_plural = "Ish grafiklari"

    def __str__(self):
        return f"{self.shifokor.ism}: {self.get_kun_boshlanishi_display()}-{self.get_kun_tugashi_display()}"
    
class DamOlishKuni(models.Model):
    shifokor = models.ForeignKey('Shifokor', on_delete=models.CASCADE, related_name='maxsus_dam_olish')
    sana = models.DateField()
    sabab = models.CharField(max_length=255, blank=True, null=True, verbose_name="Sabab (masalan: Bayram yoki Kasallik)")

    class Meta:
        verbose_name = "Dam olish kuni"
        verbose_name_plural = "Dam olish kunlari"
        unique_together = ['shifokor', 'sana']

    def __str__(self):
        return f"{self.shifokor.ism} - {self.sana}"
    

class AnalizNavbat(models.Model):
    STATUS_CHOICES = [
        ('tasdiqlandi', 'Tasdiqlandi'),
        ('bekor_qilindi', 'Bekor qilindi'),
    ]

    foydalanuvchi = models.ForeignKey(
        Foydalanuvchi,
        on_delete=models.CASCADE,
        related_name='analiz_navbatlari'
    )

    analiz = models.ForeignKey(
        KlinikaTekshiruvi,
        on_delete=models.CASCADE,
        related_name='navbatlar'
    )

    sana = models.DateField()
    vaqt = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='tasdiqlandi'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['analiz', 'sana', 'vaqt'],
                condition=Q(status='tasdiqlandi'),
                name='unique_active_analiz_slot'
            )
        ]

    def __str__(self):
        return f"{self.foydalanuvchi} | {self.analiz.nom} | {self.sana} {self.vaqt}"

class AnalizWorkSchedule(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Dushanba'),
        (1, 'Seshanba'),
        (2, 'Chorshanba'),
        (3, 'Payshanba'),
        (4, 'Juma'),
        (5, 'Shanba'),
        (6, 'Yakshanba'),
    ]

    analiz = models.ForeignKey(
        KlinikaTekshiruvi,
        on_delete=models.CASCADE,
        related_name='ish_grafiklari'
    )

    kun_boshlanishi = models.IntegerField(choices=DAYS_OF_WEEK)
    kun_tugashi = models.IntegerField(choices=DAYS_OF_WEEK)

    ish_boshlanishi = models.TimeField()
    ish_yakuni = models.TimeField()

    tushlik_boshlanishi = models.TimeField(null=True, blank=True)
    tushlik_tugashi = models.TimeField(null=True, blank=True)

    qabul_davomiyligi = models.PositiveIntegerField(
        default=30,
        help_text="Har bir analiz uchun vaqt (daqiqada)"
    )

    class Meta:
        verbose_name = "Analiz ish grafigi"
        verbose_name_plural = "Analiz ish grafiklari"

    def __str__(self):
        return f"{self.analiz.nom} ({self.get_kun_boshlanishi_display()}-{self.get_kun_tugashi_display()})"
    
class AnalizDamOlishKuni(models.Model):
    analiz = models.ForeignKey(
        KlinikaTekshiruvi,
        on_delete=models.CASCADE,
        related_name='dam_olish_kunlari'
    )

    sana = models.DateField()
    sabab = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Sabab (Bayram, Texnik tanaffus va h.k.)"
    )

    class Meta:
        verbose_name = "Analiz dam olish kuni"
        verbose_name_plural = "Analiz dam olish kunlari"
        unique_together = ('analiz', 'sana')

    def __str__(self):
        return f"{self.analiz.nom} - {self.sana}"


