# D:\BMI\core\serializers.py - TO'G'RILANGAN YAKUNIY KOD
import time
from django.db.models import Q
from django.db import transaction
from django.utils.dateparse import parse_time


from rest_framework import serializers
from django.utils import timezone
from .models import (
    AnalizDamOlishKuni, AnalizWorkSchedule, Foydalanuvchi, Klinika, Shifokor, Navbat, ShaxsTasdigi, 
    KlinikaTekshiruvi, WorkSchedule, DamOlishKuni, AnalizNavbat,
)
from django.contrib.auth.models import User
import uuid

# =========================================================================
# 1. AUTENTIFIKATSIYA SERIALIZERLARI
# =========================================================================
# ... importlar ...

class RegisterSerializer(serializers.Serializer):
    ism = serializers.CharField(max_length=100)
    familiya = serializers.CharField(max_length=100)

    email = serializers.EmailField(
        required=False,
        allow_blank=True
    )

    tel_raqam = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        tel = data.get('tel_raqam')
        email = data.get('email')

        # 🔴 Telefon majburiy va unikal
        if Foydalanuvchi.objects.filter(tel_raqam=tel).exists():
            raise serializers.ValidationError({
                "tel_raqam": "Bu telefon raqam band"
            })

        # 🔵 Email ixtiyoriy, lekin agar kiritilgan bo‘lsa — unikal
        if email:
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError({
                    "email": "Bu email band"
                })

        return data

    def create(self, validated_data):
        email = validated_data.get('email')
        if email == "":
            email = None   # 🔥 MUHIM

        user = User.objects.create_user(
            username=validated_data['tel_raqam'],
            email=email,
            password=validated_data['password'],
            first_name=validated_data['ism'],
            last_name=validated_data['familiya'],
        )

        foydalanuvchi = Foydalanuvchi.objects.create(
            user=user,
            ism=validated_data['ism'],
            tel_raqam=validated_data['tel_raqam'],
        )

        return foydalanuvchi



# YANGI: Parolni tiklash uchun Serializer
class ResetPasswordRequestSerializer(serializers.Serializer):
    contact = serializers.CharField(help_text="Telefon raqam yoki Email kiriting")

class ResetPasswordConfirmSerializer(serializers.Serializer):
    contact = serializers.CharField()
    code = serializers.CharField(max_length=6, help_text="SMS yoki Emailga kelgan kod")
    new_password = serializers.CharField(min_length=6)

class ShaxsTasdigiSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShaxsTasdigi
        fields = ('passport_seriya_raqam', 'jshshir')
        
    def validate(self, data):
        passport = data.get('passport_seriya_raqam')
        jshshir = data.get('jshshir')

        if not passport and not jshshir:
            raise serializers.ValidationError("Passport seriya raqami yoki JSHSHIR kiritilishi shart.")

        if passport and ShaxsTasdigi.objects.filter(passport_seriya_raqam=passport).exists():
            raise serializers.ValidationError({"passport_seriya_raqam": "Bu Passport seriya raqami band."})

        if jshshir and ShaxsTasdigi.objects.filter(jshshir=jshshir).exists():
            raise serializers.ValidationError({"jshshir": "Bu JSHSHIR band."})
        
        return data

# =========================================================================
# 2. KLINIKA VA SHIFOKOR SERIALIZERLARI
# =========================================================================

class KlinikaTekshiruviSerializer(serializers.ModelSerializer):
    class Meta:
        model = KlinikaTekshiruvi
        fields = ('id', 'klinika', 'nom', 'narx', 'xona_raqami', 'qavat_raqami', 'ish_vaqti')
        read_only_fields = ('klinika',)

class KlinikaSerializer(serializers.ModelSerializer):
    tekshiruv_narxlari = KlinikaTekshiruviSerializer(
        source='tekshiruvlar',  # 👈 ENG MUHIM JOY
        many=True,
        read_only=True
    )

    class Meta:
        model = Klinika
        fields = (
            'id',
            'nom',
            'manzil',
            'telefon',
            'ish_vaqti',
            'logo',
            'lat',
            'lon',
            'tekshiruv_narxlari'
        )   

class ShifokorSerializer(serializers.ModelSerializer):
    klinika_nomi = serializers.CharField(source='klinika.nom', read_only=True)
    jinsi_nomi = serializers.CharField(source='get_jinsi_display', read_only=True)
    to_liq_ism = serializers.SerializerMethodField() 

    class Meta:
        model = Shifokor
        fields = (
            'id', 'familiya', 'ism', 'sharif', 'to_liq_ism', 'mutaxassislik', 
            'klinika', 'klinika_nomi', 'qabul_narxi', 'ish_staji', 
            'jinsi', 'jinsi_nomi', 'ish_vaqti', 'ish_kuni', 'rasm', 'qavat', 'xona_raqami'
        )
        read_only_fields = ('klinika', 'to_liq_ism')
        
    def get_to_liq_ism(self, obj):
        sharif = obj.sharif if obj.sharif else ""
        return f"{obj.familiya} {obj.ism} {sharif}".strip()

# =========================================================================
# 3. NAVBAT SERIALIZERLARI
# =========================================================================
class NavbatSerializer(serializers.ModelSerializer):
    bemor = serializers.SerializerMethodField()
    shifokor = serializers.PrimaryKeyRelatedField(
        queryset=Shifokor.objects.all(),
        write_only=True)

    class Meta:
        model = Navbat
        fields = (
            'id',
            'bemor',
            'vaqt',
            'status',
            'shifokor',
        )
        validators = []  # UniqueTogetherValidator o‘chadi

    def get_bemor(self, obj):
        if not obj.foydalanuvchi:
            return None

        ism = obj.foydalanuvchi.ism
        familiya = obj.foydalanuvchi.user.last_name or ""
        return f"{ism} {familiya}".strip()

    def validate_vaqt(self, value):
        if value < timezone.now():
            raise serializers.ValidationError(
                "Navbat vaqti o'tmishda bo'lishi mumkin emas."
            )
        if value.minute not in [0, 30]:
            raise serializers.ValidationError(
                "Navbat vaqti har yarim soatga to'g'ri kelishi kerak (10:00, 10:30)."
            )
        return value

    def validate(self, data):
        shifokor = data.get('shifokor')
        vaqt = data.get('vaqt')
        instance = self.instance

        mahalliy_vaqt = timezone.localtime(vaqt)
        hafta_kuni = mahalliy_vaqt.weekday()
        tanlangan_soat = mahalliy_vaqt.time()
        tanlangan_sana = mahalliy_vaqt.date()

        # 1️⃣ Dam olish kuni
        if DamOlishKuni.objects.filter(
            shifokor=shifokor,
            sana=tanlangan_sana
        ).exists():
            raise serializers.ValidationError({
                "vaqt": "Bu kunda shifokor dam oladi."
            })

        # 2️⃣ Ish grafigi
        grafik = WorkSchedule.objects.filter(
            shifokor=shifokor,
            kun_boshlanishi__lte=hafta_kuni,
            kun_tugashi__gte=hafta_kuni
        ).first()

        if not grafik:
            raise serializers.ValidationError({
                "vaqt": "Shifokor bu kuni ishlamaydi."
            })

        # 3️⃣ Tushlik
        if grafik.tushlik_boshlanishi and grafik.tushlik_tugashi:
            if grafik.tushlik_boshlanishi <= tanlangan_soat < grafik.tushlik_tugashi:
                raise serializers.ValidationError({
                    "vaqt": "Bu vaqtda shifokor tushlikda."
                })

        # 4️⃣ Ish soati
        if not (grafik.ish_boshlanishi <= tanlangan_soat < grafik.ish_yakuni):
            raise serializers.ValidationError({
                "vaqt": "Bu vaqt ish soatiga to‘g‘ri kelmaydi."
            })

        # 5️⃣ Bandlik
        qs = Navbat.objects.filter(
            shifokor=shifokor,
            vaqt=vaqt,
            status='tasdiqlandi'
        )
        if instance:
            qs = qs.exclude(pk=instance.pk)

        if qs.exists():
            raise serializers.ValidationError({
                "vaqt": "Bu vaqtda navbat band."
            })

        return data

    
class NavbatStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Navbat
        fields = ['status']

class WorkScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkSchedule
        fields = ['id', 'shifokor', 'kun_boshlanishi', 'kun_tugashi', 'ish_boshlanishi', 'ish_yakuni', 'qabul_davomiyligi']

class AnalizNavbatSerializer(serializers.ModelSerializer):
    analiz_nomi = serializers.CharField(source='analiz.nom', read_only=True)

    class Meta:
        model = AnalizNavbat
        fields = ('id', 'analiz', 'analiz_nomi', 'sana', 'vaqt', 'status')
        read_only_fields = ('status',)

    def validate(self, data):
        analiz = data.get('analiz')
        sana = data.get('sana')
        vaqt = data.get('vaqt')

        qs = AnalizNavbat.objects.filter(
            analiz=analiz,
            sana=sana,
            vaqt=vaqt,
            status='tasdiqlandi'
        )

        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError({"vaqt": "Bu vaqtda analiz navbati band."})

        return data


class AnalizNavbatStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalizNavbat
        fields = ['status']

class ProfileSerializer(serializers.ModelSerializer):
    familiya = serializers.CharField(
        source='user.last_name',
        required=False,
        allow_blank=True
    )
    email = serializers.EmailField(
        source='user.email',
        required=False,
        allow_blank=True,
        allow_null=True
    )

    tel_raqam = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    passport_seriya_raqam = serializers.CharField(
        source='shaxsiy_tasdiq.passport_seriya_raqam',
        required=False,
        allow_blank=True,
        allow_null=True
    )
    jshshir = serializers.CharField(
        source='shaxsiy_tasdiq.jshshir',
        required=False,
        allow_blank=True,
        allow_null=True
    )

    yangi_parol = serializers.CharField(
        write_only=True,
        required=False,
        min_length=6
    )

    class Meta:
        model = Foydalanuvchi
        fields = (
            'ism',
            'familiya',
            'email',
            'tel_raqam',
            'passport_seriya_raqam',
            'jshshir',
            'yangi_parol',
        )

    def update(self, instance, validated_data):
        user = instance.user

        # 🔹 USER DATA (MUHIM FIX)
        user_data = validated_data.pop('user', {})

        if 'last_name' in user_data:
            user.last_name = user_data['last_name']

        # ✅ EMAIL NI MAJBURAN YOZAMIZ
        if 'email' in user_data:
            user.email = user_data['email'] or None

        # 🔐 PAROL
        yangi_parol = validated_data.pop('yangi_parol', None)
        if yangi_parol:
            user.set_password(yangi_parol)

        user.save()

        # 🔹 FOYDALANUVCHI
        if 'ism' in validated_data:
            instance.ism = validated_data['ism']

        if 'tel_raqam' in validated_data:
             new_tel = validated_data['tel_raqam']
             instance.tel_raqam = new_tel
             instance.user.username = new_tel

        instance.user.save()
        instance.save()

        # 🔹 SHAXS TASDIGI
        shaxs_data = validated_data.get('shaxsiy_tasdiq')
        if shaxs_data:
            shaxs, _ = ShaxsTasdigi.objects.get_or_create(
                foydalanuvchi=instance
            )
            for k, v in shaxs_data.items():
                setattr(shaxs, k, v)
            shaxs.save()

        return instance


class AdminKlinikaSerializer(serializers.ModelSerializer):
    lat = serializers.FloatField(required=False, allow_null=True)
    lon = serializers.FloatField(required=False, allow_null=True)
    manzil = serializers.CharField(required=False, allow_blank=True)
    telefon = serializers.CharField(required=False, allow_blank=True)
    ish_vaqti = serializers.CharField(required=False, allow_blank=True)
    nom = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Klinika
        fields = (
            'id',
            'nom',
            'manzil',
            'telefon',
            'ish_vaqti',
            'logo',
            'lat',
            'lon',
        )

class AdminShifokorSerializer(serializers.ModelSerializer):
    # login ixtiyoriy
    login = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Mavjud foydalanuvchi telefoni yoki emaili"
    )
    current_login = serializers.SerializerMethodField()

    # ⚠️ MUHIM: update'da rasm majburiy bo'lmasin
    rasm = serializers.ImageField(required=False, allow_null=True)

    # CREATE paytida schedule majburiy (login’dan boshqa)
    kun_boshlanishi = serializers.IntegerField(write_only=True, required=True)
    kun_tugashi = serializers.IntegerField(write_only=True, required=True)

    ish_boshlanishi = serializers.TimeField(write_only=True, required=True)
    ish_yakuni = serializers.TimeField(write_only=True, required=True)

    tushlik_boshlanishi = serializers.TimeField(write_only=True, required=True)
    tushlik_tugashi = serializers.TimeField(write_only=True, required=True)

    qabul_davomiyligi = serializers.IntegerField(write_only=True, required=False, default=30)

    # read-only schedule qaytarish
    kun_boshlanishi_ro = serializers.SerializerMethodField()
    kun_tugashi_ro = serializers.SerializerMethodField()
    ish_boshlanishi_ro = serializers.SerializerMethodField()
    ish_yakuni_ro = serializers.SerializerMethodField()
    tushlik_boshlanishi_ro = serializers.SerializerMethodField()
    tushlik_tugashi_ro = serializers.SerializerMethodField()
    qabul_davomiyligi_ro = serializers.SerializerMethodField()

    class Meta:
        model = Shifokor
        fields = (
            'id',
            'familiya', 'ism', 'sharif',
            'mutaxassislik',
            'jinsi',
            'ish_staji',
            'qabul_narxi',
            'ish_vaqti',
            'ish_kuni',
            'rasm',
            'qavat',
            'xona_raqami',

            'login',
            'current_login',

            # write-only schedule (create/update payload uchun)
            'kun_boshlanishi',
            'kun_tugashi',
            'ish_boshlanishi',
            'ish_yakuni',
            'tushlik_boshlanishi',
            'tushlik_tugashi',
            'qabul_davomiyligi',

            # read-only schedule (UI ko‘rsatish uchun)
            'kun_boshlanishi_ro',
            'kun_tugashi_ro',
            'ish_boshlanishi_ro',
            'ish_yakuni_ro',
            'tushlik_boshlanishi_ro',
            'tushlik_tugashi_ro',
            'qabul_davomiyligi_ro',
        )

    def validate(self, attrs):
        # ✅ CREATE paytida rasm majburiy bo‘lsin
        if self.instance is None:
            if not attrs.get("rasm"):
                raise serializers.ValidationError({"rasm": ["Rasm majburiy"]})

        # ✅ vaqtlar mantiqiy bo‘lsin (create/update'da ham tekshiramiz, bor bo‘lsa)
        def _get(name):
            if name in attrs:
                return attrs.get(name)
            if self.instance:
                # update paytida schedule fieldlar serializer orqali kelsa tekshiradi,
                # lekin schedule alohida modelda — shuning uchun bu joy faqat payload bo‘lsa ishlaydi
                return None
            return None

        ish_b = _get("ish_boshlanishi")
        ish_y = _get("ish_yakuni")
        tb = _get("tushlik_boshlanishi")
        tt = _get("tushlik_tugashi")

        # faqat payloadda bo‘lsa tekshiramiz
        if ish_b and ish_y and ish_b >= ish_y:
            raise serializers.ValidationError({"ish_yakuni": ["Ish tugashi ish boshlanishidan keyin bo‘lishi kerak"]})

        if tb and tt and tb >= tt:
            raise serializers.ValidationError({"tushlik_tugashi": ["Tushlik tugashi tushlik boshlanishidan keyin bo‘lishi kerak"]})

        # tushlik ish orasida bo‘lsin (payload to‘liq bo‘lsa)
        if ish_b and ish_y and tb and tt:
            if not (ish_b <= tb < tt <= ish_y):
                raise serializers.ValidationError({
                    "tushlik_boshlanishi": ["Tushlik ish vaqt oralig‘ida bo‘lishi kerak"],
                    "tushlik_tugashi": ["Tushlik ish vaqt oralig‘ida bo‘lishi kerak"],
                })

        return attrs

    def get_current_login(self, obj):
        if obj.user:
            return obj.user.username or obj.user.email
        return None

    def _schedule(self, obj):
        return WorkSchedule.objects.filter(shifokor=obj).first()

    def _fmt(self, t):
        if not t:
            return ""
        try:
            return t.strftime("%H:%M")
        except Exception:
            return str(t)

    def get_kun_boshlanishi_ro(self, obj):
        s = self._schedule(obj)
        return getattr(s, "kun_boshlanishi", None) if s else None

    def get_kun_tugashi_ro(self, obj):
        s = self._schedule(obj)
        return getattr(s, "kun_tugashi", None) if s else None

    def get_ish_boshlanishi_ro(self, obj):
        s = self._schedule(obj)
        return self._fmt(getattr(s, "ish_boshlanishi", None)) if s else ""

    def get_ish_yakuni_ro(self, obj):
        s = self._schedule(obj)
        return self._fmt(getattr(s, "ish_yakuni", None)) if s else ""

    def get_tushlik_boshlanishi_ro(self, obj):
        s = self._schedule(obj)
        return self._fmt(getattr(s, "tushlik_boshlanishi", None)) if s else ""

    def get_tushlik_tugashi_ro(self, obj):
        s = self._schedule(obj)
        return self._fmt(getattr(s, "tushlik_tugashi", None)) if s else ""

    def get_qabul_davomiyligi_ro(self, obj):
        s = self._schedule(obj)
        return getattr(s, "qabul_davomiyligi", None) if s else None

    def _attach_login(self, instance, login):
        if not login:
            return

        try:
            user = User.objects.get(Q(username=login) | Q(email=login))
        except User.DoesNotExist:
            raise serializers.ValidationError({"login": "Bu login bilan foydalanuvchi topilmadi"})

        if hasattr(user, 'shifokor_profil') and user.shifokor_profil != instance:
            raise serializers.ValidationError({"login": "Bu login boshqa shifokorga biriktirilgan"})

        if hasattr(user, 'admin_profil'):
            raise serializers.ValidationError({"login": "Admin loginini shifokorga biriktirib bo‘lmaydi"})

        instance.user = user

    @transaction.atomic
    def create(self, validated_data):
        login = validated_data.pop('login', None)
        if login is not None:
            login = str(login).strip() or None

        # schedule required
        kun_boshlanishi = validated_data.pop('kun_boshlanishi')
        kun_tugashi = validated_data.pop('kun_tugashi')
        ish_boshlanishi = validated_data.pop('ish_boshlanishi')
        ish_yakuni = validated_data.pop('ish_yakuni')
        tushlik_boshlanishi = validated_data.pop('tushlik_boshlanishi')
        tushlik_tugashi = validated_data.pop('tushlik_tugashi')
        qabul_davomiyligi = validated_data.pop('qabul_davomiyligi', 30) or 30

        shifokor = Shifokor.objects.create(**validated_data)

        if login:
            self._attach_login(shifokor, login)
            shifokor.save()

        # ✅ eng muhim FIX: create paytida WorkSchedule ham to‘liq yaratiladi
        WorkSchedule.objects.create(
            shifokor=shifokor,
            kun_boshlanishi=kun_boshlanishi,
            kun_tugashi=kun_tugashi,
            ish_boshlanishi=ish_boshlanishi,
            ish_yakuni=ish_yakuni,
            tushlik_boshlanishi=tushlik_boshlanishi,
            tushlik_tugashi=tushlik_tugashi,
            qabul_davomiyligi=qabul_davomiyligi
        )

        return shifokor

    @transaction.atomic
    def update(self, instance, validated_data):
        login = validated_data.pop('login', None)
        if login is not None:
            login = str(login).strip() or None
            if login:
                self._attach_login(instance, login)

        # schedule fieldlar kelgan bo‘lsa — WorkSchedule'ga yozamiz
        schedule_payload = {}
        for f in [
            'kun_boshlanishi', 'kun_tugashi',
            'ish_boshlanishi', 'ish_yakuni',
            'tushlik_boshlanishi', 'tushlik_tugashi',
            'qabul_davomiyligi'
        ]:
            if f in validated_data:
                schedule_payload[f] = validated_data.pop(f)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if schedule_payload:
            schedule, _ = WorkSchedule.objects.get_or_create(
                shifokor=instance,
                defaults={
                    "kun_boshlanishi": schedule_payload.get("kun_boshlanishi", 0),
                    "kun_tugashi": schedule_payload.get("kun_tugashi", 4),
                    "ish_boshlanishi": schedule_payload.get("ish_boshlanishi"),
                    "ish_yakuni": schedule_payload.get("ish_yakuni"),
                    "tushlik_boshlanishi": schedule_payload.get("tushlik_boshlanishi"),
                    "tushlik_tugashi": schedule_payload.get("tushlik_tugashi"),
                    "qabul_davomiyligi": schedule_payload.get("qabul_davomiyligi", 30) or 30,
                }
            )
            for k, v in schedule_payload.items():
                setattr(schedule, k, v)
            if not schedule.qabul_davomiyligi:
                schedule.qabul_davomiyligi = 30
            schedule.save()

        return instance

class AdminAnalizSerializer(serializers.ModelSerializer):
    # 🔥 Grafik maydonlari
    kun_boshlanishi = serializers.IntegerField(write_only=True, required=False)
    kun_tugashi = serializers.IntegerField(write_only=True, required=False)

    ish_boshlanishi = serializers.TimeField(write_only=True, required=False)
    ish_yakuni = serializers.TimeField(write_only=True, required=False)

    tushlik_boshlanishi = serializers.TimeField(write_only=True, required=False)
    tushlik_tugashi = serializers.TimeField(write_only=True, required=False)

    qabul_davomiyligi = serializers.IntegerField(write_only=True, required=False)

    # 🔵 O‘qish uchun
    grafik = serializers.SerializerMethodField()

    class Meta:
        model = KlinikaTekshiruvi
        fields = (
            'id',
            'nom',
            'narx',
            'xona_raqami',
            'qavat_raqami',
            'ish_vaqti',

            # grafik write
            'kun_boshlanishi',
            'kun_tugashi',
            'ish_boshlanishi',
            'ish_yakuni',
            'tushlik_boshlanishi',
            'tushlik_tugashi',
            'qabul_davomiyligi',

            # grafik read
            'grafik',
        )

    def get_grafik(self, obj):
        grafik = obj.ish_grafiklari.first()
        if not grafik:
            return None

        return {
            "kun_boshlanishi": grafik.kun_boshlanishi,
            "kun_tugashi": grafik.kun_tugashi,
            "ish_boshlanishi": grafik.ish_boshlanishi,
            "ish_yakuni": grafik.ish_yakuni,
            "tushlik_boshlanishi": grafik.tushlik_boshlanishi,
            "tushlik_tugashi": grafik.tushlik_tugashi,
            "qabul_davomiyligi": grafik.qabul_davomiyligi,
        }

    def create(self, validated_data):
        grafik_data = {
            "kun_boshlanishi": validated_data.pop("kun_boshlanishi", 0),
            "kun_tugashi": validated_data.pop("kun_tugashi", 4),
            "ish_boshlanishi": validated_data.pop("ish_boshlanishi", "09:00"),
            "ish_yakuni": validated_data.pop("ish_yakuni", "17:00"),
            "tushlik_boshlanishi": validated_data.pop("tushlik_boshlanishi", None),
            "tushlik_tugashi": validated_data.pop("tushlik_tugashi", None),
            "qabul_davomiyligi": validated_data.pop("qabul_davomiyligi", 30),
        }

        analiz = KlinikaTekshiruvi.objects.create(**validated_data)

        AnalizWorkSchedule.objects.create(
            analiz=analiz,
            **grafik_data
        )

        return analiz

    def update(self, instance, validated_data):
        grafik = instance.ish_grafiklari.first()

        grafik_fields = [
            "kun_boshlanishi",
            "kun_tugashi",
            "ish_boshlanishi",
            "ish_yakuni",
            "tushlik_boshlanishi",
            "tushlik_tugashi",
            "qabul_davomiyligi",
        ]

        grafik_data = {}

        for field in grafik_fields:
            if field in validated_data:
                grafik_data[field] = validated_data.pop(field)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if grafik:
            for attr, value in grafik_data.items():
                setattr(grafik, attr, value)
            grafik.save()

        return instance



class AdminNavbatSerializer(serializers.ModelSerializer):
    foydalanuvchi_ism = serializers.CharField(
        source='foydalanuvchi.ism', read_only=True
    )
    foydalanuvchi_tel = serializers.CharField(
        source='foydalanuvchi.tel_raqam', read_only=True
    )

    class Meta:
        model = Navbat
        fields = (
            'id',
            'foydalanuvchi_ism',
            'foydalanuvchi_tel',
            'vaqt',
            'status',
        )


class ShifokorProfileSerializer(serializers.ModelSerializer):
    klinika_nomi = serializers.CharField(source='klinika.nom', read_only=True)
    login = serializers.SerializerMethodField()

    class Meta:
        model = Shifokor
        fields = (
            'id',
            'ism',
            'familiya',
            'sharif',
            'mutaxassislik',
            'ish_staji',
            'qabul_narxi',
            'ish_vaqti',
            'ish_kuni',
            'qavat',
            'xona_raqami',
            'rasm',
            'klinika_nomi',
            'login',
        )

    def get_login(self, obj):
        if obj.user:
            return obj.user.username or obj.user.email
        return None
    
class AdminDamOlishSerializer(serializers.ModelSerializer):
    class Meta:
        model = DamOlishKuni
        fields = ('id', 'sana', 'sabab')

class AdminAnalizWorkScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalizWorkSchedule
        fields = (
            'id',
            'analiz',
            'kun_boshlanishi',
            'kun_tugashi',
            'ish_boshlanishi',
            'ish_yakuni',
            'tushlik_boshlanishi',
            'tushlik_tugashi',
            'qabul_davomiyligi',
        )

class AdminAnalizDamOlishSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalizDamOlishKuni
        fields = ('id', 'sana', 'sabab')

class AdminAnalizNavbatSerializer(serializers.ModelSerializer):
    foydalanuvchi_ism = serializers.CharField(source='foydalanuvchi.ism', read_only=True)
    foydalanuvchi_tel = serializers.CharField(source='foydalanuvchi.tel_raqam', read_only=True)

    # MUHIM: AnalizNavbat’da sana = DateField, vaqt = TimeField
    sana = serializers.DateField()
    vaqt = serializers.TimeField(format="%H:%M")

    class Meta:
        model = AnalizNavbat
        fields = (
            'id',
            'foydalanuvchi_ism',
            'foydalanuvchi_tel',
            'sana',
            'vaqt',
            'status',
        )