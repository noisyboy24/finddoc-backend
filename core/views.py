from django.shortcuts import get_object_or_404
from rest_framework import status, generics, filters, permissions, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
import django_filters.rest_framework
import os
import requests
from django.conf import settings

from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter
from rest_framework.exceptions import PermissionDenied
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User

from .models import (
    AnalizWorkSchedule, DamOlishKuni, Klinika, Shifokor, Navbat, Foydalanuvchi, 
    KlinikaTekshiruvi, WorkSchedule, ShaxsTasdigi, AnalizNavbat, AnalizDamOlishKuni,AdminProfil, Klinika
)
from .serializers import (
    AdminAnalizDamOlishSerializer, AdminAnalizWorkScheduleSerializer, RegisterSerializer, KlinikaSerializer, ShifokorSerializer, 
    NavbatSerializer, ShaxsTasdigiSerializer, KlinikaTekshiruviSerializer, 
    NavbatStatusSerializer, WorkScheduleSerializer, ResetPasswordRequestSerializer, ResetPasswordConfirmSerializer, AnalizNavbatSerializer, AnalizNavbatStatusSerializer, ProfileSerializer, AdminKlinikaSerializer, 
    AdminShifokorSerializer, AdminAnalizSerializer, AdminNavbatSerializer, ShifokorProfileSerializer, AdminDamOlishSerializer,AdminAnalizNavbatSerializer

)
from .permissions import IsAdminKlinika, IsShifokor, IsSuperAdmin
from datetime import datetime, timedelta, time
from django.utils import timezone

# --- Permissions ---
class IsPersonalVerified(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated: return False
        return ShaxsTasdigi.objects.filter(foydalanuvchi__user=request.user).exists()

class LoginInputSerializer(serializers.Serializer): 
    username = serializers.CharField()
    password = serializers.CharField()

# --- Auth ---
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            foydalanuvchi = serializer.save()
            token, _ = Token.objects.get_or_create(user=foydalanuvchi.user)

            return Response({
                "token": token.key,
                "next_step": "shaxs_tasdigi"
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginInputSerializer

    @extend_schema(request=LoginInputSerializer)
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if not user:
            return Response(
                {"error": "Login yoki parol xato"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        token, _ = Token.objects.get_or_create(user=user)

        # ================= ROLE ANIQLASH =================
        role = "user"
        klinika_id = None
        klinika_nomi = None
        shifokor_id = None

        # 🔹 ADMIN
        if hasattr(user, 'admin_profil'):
            role = "admin"
            if user.admin_profil.klinika:
                klinika_id = user.admin_profil.klinika.id
                klinika_nomi = user.admin_profil.klinika.nom

        # 🔹 SHIFOKOR
        elif hasattr(user, 'shifokor_profil'):
            role = "shifokor"
            shifokor_id = user.shifokor_profil.id
            if user.shifokor_profil.klinika:
                klinika_id = user.shifokor_profil.klinika.id
                klinika_nomi = user.shifokor_profil.klinika.nom

        # 🔹 ODDIY USER (default)
        else:
            role = "user"

        return Response({
            "token": token.key,
            "role": role,                 # 👈 ENG MUHIM
            "klinika_id": klinika_id,
            "klinika_nomi": klinika_nomi,
            "shifokor_id": shifokor_id,
        })


    
class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordRequestSerializer
    
    @extend_schema(request=ResetPasswordRequestSerializer)
    def post(self, request):
        contact = request.data.get('contact')
        
        # Foydalanuvchini Telefon yoki Email orqali qidiramiz
        try:
            foydalanuvchi = Foydalanuvchi.objects.get(
                Q(tel_raqam=contact) | Q(email=contact)
            )
        except Foydalanuvchi.DoesNotExist:
            # Xavfsizlik uchun: "Topilmadi" demasdan, "Kod yuborildi" deymiz (agar u mavjud bo'lmasa ham)
            return Response({"message": "Agar bunday foydalanuvchi mavjud bo'lsa, tasdiqlash kodi yuborildi."}, status=200)

        # BU YERDA SMS YOKI EMAIL YUBORISH KODI BO'LISHI KERAK
        # Hozircha konsolga chiqaramiz (Simulyatsiya)
        fake_code = "123456" 
        print(f"DIQQAT: {contact} uchun tiklash kodi: {fake_code}")
        
        # Kodni vaqtinchalik xotirada saqlash kerak (Redis yoki Database)
        # Hozircha oddiylik uchun sessiyada yoki keshda saqlashni tasavvur qilamiz.
        
        return Response({"message": "Tasdiqlash kodi yuborildi. (Test uchun kod: 123456)"}, status=200)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordConfirmSerializer

    @extend_schema(request=ResetPasswordConfirmSerializer)
    def post(self, request):
        contact = request.data.get('contact')
        code = request.data.get('code')
        new_password = request.data.get('new_password')
        
        # KODNI TEKSHIRISH (Simulyatsiya)
        if code != "123456":
            return Response({"error": "Kod noto'g'ri"}, status=400)
            
        try:
            foydalanuvchi = Foydalanuvchi.objects.get(
                Q(tel_raqam=contact) | Q(email=contact)
            )
            user = foydalanuvchi.user
            user.set_password(new_password) # Yangi parolni o'rnatish
            user.save()
            return Response({"message": "Parol muvaffaqiyatli o'zgartirildi. Endi yangi parol bilan kirishingiz mumkin."}, status=200)
            
        except Foydalanuvchi.DoesNotExist:
            return Response({"error": "Foydalanuvchi topilmadi"}, status=404)

class ShaxsTasdigiCreateAPIView(CreateAPIView):
    serializer_class = ShaxsTasdigiSerializer
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):
        serializer.save(foydalanuvchi=self.request.user.foydalanuvchi)

# --- Klinika & Shifokor ---
class KlinikaListAPIView(ListAPIView):
    queryset = Klinika.objects.all()
    serializer_class = KlinikaSerializer
    permission_classes = [AllowAny]

class KlinikaDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Klinika.objects.all()
    serializer_class = KlinikaSerializer
    permission_classes = [AllowAny]

class ShifokorListAPIView(ListAPIView):
    serializer_class = ShifokorSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Shifokor.objects.all()

        # 1️⃣ Frontend uchun: ?klinika=ID
        klinika_param = self.request.query_params.get('klinika')

        # 2️⃣ Agar admin bo‘lsa — faqat o‘z klinikasi (HAR DOIM ustun)
        user = self.request.user
        if user.is_authenticated and hasattr(user, "admin_profil") and user.admin_profil.klinika_id:
         return queryset.filter(klinika_id=user.admin_profil.klinika_id)


        # 3️⃣ Oddiy user / guest uchun — tanlangan klinika
        if klinika_param:
            return queryset.filter(klinika_id=klinika_param)

        # 4️⃣ Agar hech narsa berilmasa — hammasi (masalan umumiy ro‘yxat)
        return queryset
    
    def get_queryset(self):
        queryset = Shifokor.objects.all()

        klinika_param = self.request.query_params.get('klinika')
        q = (self.request.query_params.get('q') or "").strip()

        user = self.request.user
        if user.is_authenticated and hasattr(user, "admin_profil") and user.admin_profil.klinika_id:
            queryset = queryset.filter(klinika_id=user.admin_profil.klinika_id)
        elif klinika_param:
            queryset = queryset.filter(klinika_id=klinika_param)

        # ✅ YANGI: mutaxassislik bo‘yicha qidiruv (icontains)
        if q:
            queryset = queryset.filter(mutaxassislik__icontains=q)

        return queryset


class ShifokorCreateAPIView(CreateAPIView):
    serializer_class = ShifokorSerializer
    permission_classes = [IsAdminKlinika]
    def perform_create(self, serializer):
        serializer.save(klinika=self.request.user.admin_profil.klinika)

class ShifokorDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Shifokor.objects.all()
    serializer_class = ShifokorSerializer
    permission_classes = [AllowAny]

# --- Navbat ---
class NavbatCreateAPIView(CreateAPIView):
    serializer_class = NavbatSerializer
    permission_classes = [IsAuthenticated, IsPersonalVerified]
    def perform_create(self, serializer):
        serializer.save(foydalanuvchi=self.request.user.foydalanuvchi,status='tasdiqlandi')

class NavbatlarimListAPIView(ListAPIView):
    serializer_class = NavbatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Swagger (drf-spectacular) uchun himoya
        if getattr(self, "swagger_fake_view", False):
            return Navbat.objects.none()
        
        # User login qilgan bo'lsa va uning foydalanuvchi profili bo'lsa
        user = self.request.user
        if hasattr(user, 'foydalanuvchi'):
            return Navbat.objects.filter(foydalanuvchi=user.foydalanuvchi)
        return Navbat.objects.none()

class NavbatKlinikaAdminListAPIView(ListAPIView):
    serializer_class = NavbatSerializer
    permission_classes = [IsAdminKlinika]

    def get_queryset(self):
        # Swagger uchun himoya
        if getattr(self, "swagger_fake_view", False):
            return Navbat.objects.none()

        user = self.request.user
        if hasattr(user, 'admin_profil'):
            return Navbat.objects.filter(shifokor__klinika_id=user.admin_profil.klinika_id)
        return Navbat.objects.none()

class NavbatDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = NavbatSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Navbat.objects.filter(foydalanuvchi=self.request.user.foydalanuvchi)

class NavbatStatusUpdateAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = NavbatStatusSerializer
    permission_classes = [IsAdminKlinika]
    def get_queryset(self):
        return Navbat.objects.filter(shifokor__klinika_id=self.request.user.admin_profil.klinika_id)
    
class NavbatCancelAPIView(UpdateAPIView):
    """Bemor o'z navbatini bekor qilishi uchun"""
    serializer_class = NavbatStatusSerializer # Faqat statusni o'zgartirish uchun
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Faqat foydalanuvchining o'ziga tegishli va hali bekor qilinmagan navbatlar
        return Navbat.objects.filter(foydalanuvchi=self.request.user.foydalanuvchi)

    def perform_update(self, serializer):
        # Statusni avtomatik 'bekor_qilindi'ga o'tkazamiz
        serializer.save(status='bekor_qilindi')

# --- Ish Grafigi ---
class WorkScheduleListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = WorkScheduleSerializer
    permission_classes = [IsAdminKlinika]
    def get_queryset(self):
        return WorkSchedule.objects.filter(shifokor__klinika_id=self.request.user.admin_profil.klinika_id)

class WorkScheduleListAPIView(generics.ListAPIView):
    queryset = WorkSchedule.objects.all()
    serializer_class = WorkScheduleSerializer
    permission_classes = [AllowAny]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['shifokor']

# --- Tekshiruvlar ---
class KlinikaTekshiruviCreateAPIView(CreateAPIView):
    serializer_class = KlinikaTekshiruviSerializer
    permission_classes = [IsAdminKlinika]
    def perform_create(self, serializer):
        serializer.save(klinika=self.request.user.admin_profil.klinika)

class AvailableSlotsAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter("shifokor", OpenApiTypes.INT, description="Shifokor ID si"),
            OpenApiParameter("sana", OpenApiTypes.STR, description="Sana (YYYY-MM-DD formatida)"),
        ],
        responses={
            200: inline_serializer(
                name='SlotsResponse',
                fields={
                    'shifokor': serializers.CharField(),
                    'sana': serializers.CharField(),
                    'available_slots': serializers.ListField(child=serializers.CharField())
                }
            )
        }
    )
    def get(self, request):
        shifokor_id = request.query_params.get('shifokor')
        sana_str = request.query_params.get('sana')

        if not shifokor_id or not sana_str:
            return Response({"error": "shifokor va sana parametrlarini yuboring"}, status=400)

        try:
            sana = datetime.strptime(sana_str, '%Y-%m-%d').date()
            shifokor = Shifokor.objects.get(id=shifokor_id)
            hafta_kuni = sana.weekday()  # 0-Dushanba ... 6-Yakshanba

            # ✅ 0) Dam olish kuni bo‘lsa — umuman slot bermaymiz
            if DamOlishKuni.objects.filter(shifokor=shifokor, sana=sana).exists():
                return Response({
                    "shifokor": shifokor.ism,
                    "sana": sana_str,
                    "available_slots": []
                }, status=200)

            # 1) Ish grafigini topish
            grafik = WorkSchedule.objects.filter(
                shifokor=shifokor,
                kun_boshlanishi__lte=hafta_kuni,
                kun_tugashi__gte=hafta_kuni
            ).first()

            if not grafik:
                return Response({
                    "shifokor": shifokor.ism,
                    "sana": sana_str,
                    "available_slots": []
                }, status=200)

            # 2) Barcha slotlarni yaratish
            slots = []
            current_dt = datetime.combine(sana, grafik.ish_boshlanishi)
            end_dt = datetime.combine(sana, grafik.ish_yakuni)

            step = timedelta(minutes=grafik.qabul_davomiyligi or 30)

            while current_dt < end_dt:
                slots.append(current_dt)
                current_dt += step

            # 3) Band navbatlarni olish (faqat tasdiqlanganlar)
            band_navbatlar = Navbat.objects.filter(
                shifokor=shifokor,
                vaqt__date=sana,
                status='tasdiqlandi'
            ).values_list('vaqt', flat=True)

            band_soatlar = set()
            for nb in band_navbatlar:
                local_v = timezone.localtime(nb)
                band_soatlar.add(local_v.strftime('%H:%M'))

            # 4) Bo‘sh slotlarni filtrlash (tushlik + o‘tmish + band)
            available_slots = []
            now = timezone.localtime(timezone.now())

            for slot in slots:
                slot_time = slot.time()
                slot_str = slot.strftime('%H:%M')

                # 🥪 Tushlik
                if grafik.tushlik_boshlanishi and grafik.tushlik_tugashi:
                    if grafik.tushlik_boshlanishi <= slot_time < grafik.tushlik_tugashi:
                        continue

                # ❌ Band
                if slot_str in band_soatlar:
                    continue

                # ❌ O‘tmish (bugun bo‘lsa — hozirdan oldingi slotlar yashiriladi)
                if sana == now.date() and slot_time <= now.time():
                    continue

                # ✅ Kelajak kunlar
                if sana > now.date() or sana == now.date():
                    available_slots.append(slot_str)

            return Response({
                "shifokor": shifokor.ism,
                "sana": sana_str,
                "available_slots": available_slots
            }, status=200)

        except Shifokor.DoesNotExist:
            return Response({"error": "Shifokor topilmadi"}, status=404)
        except Exception as e:
            return Response({"error": f"Xato yuz berdi: {str(e)}"}, status=400)
    
class IsShifokor(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and hasattr(request.user, 'shifokor_profil'))

class ShifokorNavbatlariAPIView(APIView):
    permission_classes = [IsAuthenticated, IsShifokor]

    def get(self, request):
        shifokor = request.user.shifokor_profil
        now = timezone.now()

        navbatlar = Navbat.objects.filter(
            shifokor=shifokor,
            status='tasdiqlandi',
            vaqt__gte=timezone.now() 
        ).order_by('vaqt')

        serializer = NavbatSerializer(navbatlar, many=True)
        return Response(serializer.data)

        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    user = request.user
    
    # DIQQAT: Bu yerda User modelingizdagi maydon nomlari bo'lishi kerak.
    # Agar siz AbstractUser ishlatgan bo'lsangiz va 'ism', 'familiya' qo'shgan bo'lsangiz:
    return Response({
        "ism": getattr(user, 'ism', user.first_name), # Agar 'ism' bo'lmasa, 'first_name' ni oladi
        "familiya": getattr(user, 'familiya', user.last_name),
        "tel_raqam": getattr(user, 'tel_raqam', user.username), # Telefon login o'rnida bo'lsa
        "email": user.email
    })

# Tahrirlash (Update) funksiyasi
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    data = request.data
    
    # Ma'lumotlarni yangilash
    if 'ism' in data: user.ism = data['ism']
    if 'familiya' in data: user.familiya = data['familiya']
    if 'email' in data: user.email = data['email']
    # Telefonni o'zgartirish sal murakkabroq (unikal bo'lishi kerak), hozircha shart emas
    
    user.save()
    return Response({"success": True, "message": "Profil yangilandi"})


@api_view(['GET'])
def analiz_available_slots(request):
    analiz_id = request.GET.get('analiz_id')
    date_str = request.GET.get('date')

    if not analiz_id or not date_str:
        return Response([])

    analiz = KlinikaTekshiruvi.objects.get(id=analiz_id)
    sana = datetime.strptime(date_str, '%Y-%m-%d').date()
    hafta_kuni = sana.weekday()

    grafik = AnalizWorkSchedule.objects.filter(
        analiz=analiz,
        kun_boshlanishi__lte=hafta_kuni,
        kun_tugashi__gte=hafta_kuni
    ).first()

    # ❌ Ish grafigi yo‘q
    if not grafik:
        return Response([])

    # ❌ Dam olish kuni
    if AnalizDamOlishKuni.objects.filter(
        analiz=analiz,
        sana=sana
    ).exists():
        return Response([])

    start = datetime.combine(sana, grafik.ish_boshlanishi)
    end = datetime.combine(sana, grafik.ish_yakuni)
    step = timedelta(minutes=grafik.qabul_davomiyligi)

    band_vaqtlar = AnalizNavbat.objects.filter(
    analiz=analiz,
    sana=sana,
    status='tasdiqlandi'   # 👈 MUHIM QATOR
).values_list('vaqt', flat=True)

    slots = []
    now = timezone.localtime()

    current = start
    while current + step <= end:
        vaqt = current.time()

        # 🥪 Tushlikni chiqarib tashlash
        if grafik.tushlik_boshlanishi and grafik.tushlik_tugashi:
            if grafik.tushlik_boshlanishi <= vaqt < grafik.tushlik_tugashi:
                current += step
                continue

        # ❌ Band vaqt
        if vaqt in band_vaqtlar:
            current += step
            continue

        # ❌ O‘tmish vaqt
        if sana == now.date() and vaqt <= now.time():
            current += step
            continue

        slots.append(vaqt.strftime('%H:%M'))
        current += step

    return Response(slots)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analiz_navbat_yaratish(request):
    serializer = AnalizNavbatSerializer(
        data=request.data,
        context={'request': request}
    )

    if serializer.is_valid():
        serializer.save(foydalanuvchi=request.user.foydalanuvchi,status='tasdiqlandi')
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def shifokor_day_available(request):
    shifokor_id = request.GET.get('shifokor')
    date_str = request.GET.get('date')

    if not shifokor_id or not date_str:
        return Response({"available": False})

    try:
        shifokor = Shifokor.objects.get(id=shifokor_id)
        sana = datetime.strptime(date_str, '%Y-%m-%d').date()
        hafta_kuni = sana.weekday()
        now = timezone.localtime()

        # ❌ O‘tmish kun
        if sana < now.date():
            return Response({"available": False})

        # ❌ Shifokor dam olish kuni
        if DamOlishKuni.objects.filter(
            shifokor=shifokor,
            sana=sana
        ).exists():
            return Response({"available": False})

        # ❌ Ish grafigi yo‘q
        grafik = WorkSchedule.objects.filter(
            shifokor=shifokor,
            kun_boshlanishi__lte=hafta_kuni,
            kun_tugashi__gte=hafta_kuni
        ).first()

        if not grafik:
            return Response({"available": False})

        # ❌ Bugun va ish vaqti tugagan
        if sana == now.date() and now.time() >= grafik.ish_yakuni:
            return Response({"available": False})

        return Response({"available": True})

    except Shifokor.DoesNotExist:
        return Response({"available": False})


@api_view(['GET'])
def analiz_day_available(request):
    analiz_id = request.GET.get('analiz')
    date_str = request.GET.get('date')

    if not analiz_id or not date_str:
        return Response({"available": False})

    try:
        analiz = KlinikaTekshiruvi.objects.get(id=analiz_id)
        sana = datetime.strptime(date_str, '%Y-%m-%d').date()
        hafta_kuni = sana.weekday()
        now = timezone.localtime()

        # ❌ O‘tmish sana
        if sana < now.date():
            return Response({"available": False})

        # ❌ FAQAT SHU ANALIZ UCHUN dam olish kuni
        if AnalizDamOlishKuni.objects.filter(
            analiz=analiz,
            sana=sana
        ).exists():
            return Response({"available": False})

        # ❌ Ish grafigi yo‘q
        grafik = AnalizWorkSchedule.objects.filter(
            analiz=analiz,
            kun_boshlanishi__lte=hafta_kuni,
            kun_tugashi__gte=hafta_kuni
        ).first()

        if not grafik:
            return Response({"available": False})

        # ❌ Bugun va ish vaqti tugagan
        if sana == now.date() and now.time() >= grafik.ish_yakuni:
            return Response({"available": False})

        # ✅ HAMMASI JOYIDA
        return Response({"available": True})

    except KlinikaTekshiruvi.DoesNotExist:
        return Response({"available": False})
    
    # --- ANALIZ NAVBATNI BEKOR QILISH ---
class AnalizNavbatCancelAPIView(UpdateAPIView):
    serializer_class = AnalizNavbatStatusSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # faqat foydalanuvchining o‘z analiz navbatlari
        return AnalizNavbat.objects.filter(
            foydalanuvchi=self.request.user.foydalanuvchi
        )

    def perform_update(self, serializer):
        serializer.save(status='bekor_qilindi')

# --- ANALIZ NAVBATLARIM ---
class AnalizNavbatlarimListAPIView(ListAPIView):
    serializer_class = AnalizNavbatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Swagger uchun himoya
        if getattr(self, "swagger_fake_view", False):
            return AnalizNavbat.objects.none()

        user = self.request.user

        if hasattr(user, 'foydalanuvchi'):
            return AnalizNavbat.objects.filter(
                foydalanuvchi=user.foydalanuvchi
            ).order_by('-created_at')

        return AnalizNavbat.objects.none()
    
class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        foydalanuvchi = request.user.foydalanuvchi
        serializer = ProfileSerializer(foydalanuvchi)
        return Response(serializer.data)

    def put(self, request):
        foydalanuvchi = request.user.foydalanuvchi
        user = request.user

        # eski qiymatlar
        old_email = user.email
        old_tel = foydalanuvchi.tel_raqam

        serializer = ProfileSerializer(
            foydalanuvchi,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # 🔎 KIRISH MA'LUMOTLARI O‘ZGARDIMI?
        force_logout = False

        if request.data.get('yangi_parol'):
            force_logout = True

        if request.data.get('email') != old_email:
            force_logout = True

        if request.data.get('tel_raqam') != old_tel:
            force_logout = True

        # 🔥 TOKENLARNI O‘CHIRAMIZ
        if force_logout:
            Token.objects.filter(user=user).delete()

        return Response({
            "success": True,
            "force_logout": force_logout
        })

class AdminClinicAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminKlinika]

    def get(self, request):
        klinika = request.user.admin_profil.klinika
        serializer = AdminKlinikaSerializer(klinika)
        return Response(serializer.data)

    def put(self, request):
        klinika = request.user.admin_profil.klinika
        serializer = AdminKlinikaSerializer(
            klinika,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
class AdminAnalizListAPIView(ListAPIView):
    serializer_class = KlinikaTekshiruviSerializer
    permission_classes = [IsAdminKlinika]

    def get_queryset(self):
        return KlinikaTekshiruvi.objects.filter(
            klinika=self.request.user.admin_profil.klinika
        )

class AdminShifokorListAPIView(ListAPIView):
    serializer_class = AdminShifokorSerializer
    permission_classes = [IsAuthenticated, IsAdminKlinika]

    def get_queryset(self):
        return Shifokor.objects.filter(
            klinika=self.request.user.admin_profil.klinika
        )

class AdminShifokorDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminKlinika]

    def get_object(self, pk):
        return get_object_or_404(
            Shifokor,
            pk=pk,
            klinika=self.request.user.admin_profil.klinika
        )

    def get(self, request, pk):
        shifokor = self.get_object(pk)
        serializer = AdminShifokorSerializer(shifokor)
        return Response(serializer.data)

    def put(self, request, pk):
        shifokor = self.get_object(pk)
        serializer = AdminShifokorSerializer(
            shifokor,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        shifokor = self.get_object(pk)
        shifokor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminAnalizListAPIView(ListAPIView):
    serializer_class = AdminAnalizSerializer
    permission_classes = [IsAuthenticated, IsAdminKlinika]

    def get_queryset(self):
        return KlinikaTekshiruvi.objects.filter(
            klinika=self.request.user.admin_profil.klinika
        )
class AdminAnalizDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminKlinika]

    def get_object(self, pk):
        return get_object_or_404(
            KlinikaTekshiruvi,
            pk=pk,
            klinika=self.request.user.admin_profil.klinika
        )

    def get(self, request, pk):
        analiz = self.get_object(pk)
        serializer = AdminAnalizSerializer(analiz)
        return Response(serializer.data)

    def put(self, request, pk):
        analiz = self.get_object(pk)
        serializer = AdminAnalizSerializer(
            analiz,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        analiz = self.get_object(pk)
        analiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminShifokorNavbatListAPIView(ListAPIView):
    serializer_class = AdminNavbatSerializer
    permission_classes = [IsAuthenticated, IsAdminKlinika]

    def get_queryset(self):
        return Navbat.objects.filter(
            shifokor_id=self.kwargs['pk'],
            shifokor__klinika=self.request.user.admin_profil.klinika
        ).order_by('-vaqt')

class AdminAnalizNavbatListAPIView(ListAPIView):
    serializer_class = AdminAnalizNavbatSerializer
    permission_classes = [IsAuthenticated, IsAdminKlinika]

    def get_queryset(self):
        return AnalizNavbat.objects.filter(
            analiz_id=self.kwargs['pk'],
            analiz__klinika=self.request.user.admin_profil.klinika
        ).order_by('-sana', '-vaqt')

class AdminShifokorWorkScheduleAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminKlinika]

    def get(self, request, pk):
        schedule = WorkSchedule.objects.filter(
            shifokor_id=pk,
            shifokor__klinika=request.user.admin_profil.klinika
        ).first()

        if not schedule:
            return Response({})

        return Response({
            "kun_boshlanishi": schedule.kun_boshlanishi,
            "kun_tugashi": schedule.kun_tugashi,
            "ish_boshlanishi": schedule.ish_boshlanishi,
            "ish_yakuni": schedule.ish_yakuni,
            "tushlik_boshlanishi": schedule.tushlik_boshlanishi,
            "tushlik_tugashi": schedule.tushlik_tugashi,
            "qabul_davomiyligi": schedule.qabul_davomiyligi,
        })

class ShifokorProfileAPIView(APIView):
    permission_classes = [IsAuthenticated, IsShifokor]

    def get(self, request):
        shifokor = request.user.shifokor_profil
        serializer = ShifokorProfileSerializer(shifokor)
        return Response(serializer.data)

class AdminShifokorCreateAPIView(CreateAPIView):
    serializer_class = AdminShifokorSerializer
    permission_classes = [IsAuthenticated, IsAdminKlinika]

    def perform_create(self, serializer):
        serializer.save(
            klinika=self.request.user.admin_profil.klinika
        )
class AdminAnalizCreateAPIView(CreateAPIView):
    serializer_class = AdminAnalizSerializer
    permission_classes = [IsAuthenticated, IsAdminKlinika]

    def perform_create(self, serializer):
        serializer.save(
            klinika=self.request.user.admin_profil.klinika
        )
class AdminShifokorFullSerializer(serializers.ModelSerializer):
    login = serializers.SerializerMethodField()
    tushlik_boshlanishi = serializers.SerializerMethodField()
    tushlik_tugashi = serializers.SerializerMethodField()

    class Meta:
        model = Shifokor
        fields = '__all__'

    def get_login(self, obj):
        if obj.user:
            return obj.user.username or obj.user.email
        return ""

    def get_tushlik_boshlanishi(self, obj):
        grafik = obj.ish_grafiklari.first()
        return grafik.tushlik_boshlanishi if grafik else None

    def get_tushlik_tugashi(self, obj):
        grafik = obj.ish_grafiklari.first()
        return grafik.tushlik_tugashi if grafik else None

class AdminDamOlishListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminKlinika]

    def get(self, request, pk):
        shifokor = get_object_or_404(
            Shifokor,
            pk=pk,
            klinika=request.user.admin_profil.klinika
        )

        dam_kunlar = DamOlishKuni.objects.filter(shifokor=shifokor).order_by('-sana')
        serializer = AdminDamOlishSerializer(dam_kunlar, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        shifokor = get_object_or_404(
            Shifokor,
            pk=pk,
            klinika=request.user.admin_profil.klinika
        )

        serializer = AdminDamOlishSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(shifokor=shifokor)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AdminDamOlishDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminKlinika]

    def delete(self, request, pk):
        dam_kuni = get_object_or_404(
            DamOlishKuni,
            pk=pk,
            shifokor__klinika=request.user.admin_profil.klinika
        )

        dam_kuni.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class AdminAnalizWorkScheduleAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminKlinika]

    def get(self, request, pk):
        grafik = AnalizWorkSchedule.objects.filter(
            analiz_id=pk,
            analiz__klinika=request.user.admin_profil.klinika
        ).first()

        if not grafik:
            return Response({})

        return Response({
            "kun_boshlanishi": grafik.kun_boshlanishi,
            "kun_tugashi": grafik.kun_tugashi,
            "ish_boshlanishi": grafik.ish_boshlanishi,
            "ish_yakuni": grafik.ish_yakuni,
            "tushlik_boshlanishi": grafik.tushlik_boshlanishi,
            "tushlik_tugashi": grafik.tushlik_tugashi,
            "qabul_davomiyligi": grafik.qabul_davomiyligi,
        })

    def put(self, request, pk):
        analiz = get_object_or_404(
            KlinikaTekshiruvi,
            pk=pk,
            klinika=request.user.admin_profil.klinika
        )

        grafik, _ = AnalizWorkSchedule.objects.get_or_create(
            analiz=analiz
        )

        grafik.kun_boshlanishi = request.data.get("kun_boshlanishi")
        grafik.kun_tugashi = request.data.get("kun_tugashi")
        grafik.ish_boshlanishi = request.data.get("ish_boshlanishi")
        grafik.ish_yakuni = request.data.get("ish_yakuni")
        grafik.tushlik_boshlanishi = request.data.get("tushlik_boshlanishi")
        grafik.tushlik_tugashi = request.data.get("tushlik_tugashi")
        grafik.qabul_davomiyligi = request.data.get("qabul_davomiyligi", 30)

        grafik.save()

        return Response({"success": True})

class AdminAnalizWorkScheduleAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminKlinika]

    def get(self, request, pk):
        schedule = AnalizWorkSchedule.objects.filter(
            analiz_id=pk,
            analiz__klinika=request.user.admin_profil.klinika
        ).first()

        if not schedule:
            return Response({})

        serializer = AdminAnalizWorkScheduleSerializer(schedule)
        return Response(serializer.data)

    def post(self, request, pk):
        analiz = get_object_or_404(
            KlinikaTekshiruvi,
            pk=pk,
            klinika=request.user.admin_profil.klinika
        )

        serializer = AdminAnalizWorkScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(analiz=analiz)

        return Response(serializer.data, status=201)

    def put(self, request, pk):
        schedule = get_object_or_404(
            AnalizWorkSchedule,
            analiz_id=pk,
            analiz__klinika=request.user.admin_profil.klinika
        )

        serializer = AdminAnalizWorkScheduleSerializer(
            schedule,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class AdminAnalizDamOlishListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminKlinika]

    def get(self, request, pk):
        analiz = get_object_or_404(
            KlinikaTekshiruvi,
            pk=pk,
            klinika=request.user.admin_profil.klinika
        )

        dam_kunlar = AnalizDamOlishKuni.objects.filter(
            analiz=analiz
        ).order_by('-sana')

        serializer = AdminAnalizDamOlishSerializer(dam_kunlar, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        analiz = get_object_or_404(
            KlinikaTekshiruvi,
            pk=pk,
            klinika=request.user.admin_profil.klinika
        )

        serializer = AdminAnalizDamOlishSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(analiz=analiz)

        return Response(serializer.data, status=201)


class AssignClinicAdminAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def post(self, request):
        user_id = request.data.get("user_id")
        klinika_id = request.data.get("klinika_id")

        user = get_object_or_404(User, pk=user_id)
        klinika = get_object_or_404(Klinika, pk=klinika_id)

        profil, _ = AdminProfil.objects.get_or_create(user=user)
        profil.klinika = klinika
        profil.rol = "klinika_admin"
        profil.save()

        return Response({"success": True})
    
class AdminShifokorWorkScheduleAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminKlinika]

    def get(self, request, pk):
        schedule = WorkSchedule.objects.filter(
            shifokor_id=pk,
            shifokor__klinika=request.user.admin_profil.klinika
        ).first()

        if not schedule:
            return Response({})

        return Response({
            "kun_boshlanishi": schedule.kun_boshlanishi,
            "kun_tugashi": schedule.kun_tugashi,
            "ish_boshlanishi": schedule.ish_boshlanishi,
            "ish_yakuni": schedule.ish_yakuni,
            "tushlik_boshlanishi": schedule.tushlik_boshlanishi,
            "tushlik_tugashi": schedule.tushlik_tugashi,
            "qabul_davomiyligi": schedule.qabul_davomiyligi,
        })

    def put(self, request, pk):
        shifokor = get_object_or_404(
            Shifokor,
            pk=pk,
            klinika=request.user.admin_profil.klinika
        )

        schedule, _ = WorkSchedule.objects.get_or_create(shifokor=shifokor)

        for field in ["kun_boshlanishi", "kun_tugashi", "qabul_davomiyligi"]:
            if field in request.data and request.data[field] is not None:
                setattr(schedule, field, request.data[field])

        for field in ["ish_boshlanishi", "ish_yakuni", "tushlik_boshlanishi", "tushlik_tugashi"]:
            if field in request.data:
                val = request.data[field]
                if val in [None, ""]:
                    setattr(schedule, field, None)
                else:
                    # "HH:MM" format
                    h, m = map(int, val.split(":"))
                    setattr(schedule, field, time(hour=h, minute=m))

        schedule.save()
        return Response({"success": True})
    

class AdminAnalizDamOlishDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminKlinika]

    def delete(self, request, pk):
        dam = get_object_or_404(
            AnalizDamOlishKuni,
            pk=pk,
            analiz__klinika=request.user.admin_profil.klinika
        )
        dam.delete()
        return Response(status=204)
    
class MutaxassisliklarAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        items = (
            Shifokor.objects
            .exclude(mutaxassislik__isnull=True)
            .exclude(mutaxassislik__exact="")
            .values_list("mutaxassislik", flat=True)
            .distinct()
            .order_by("mutaxassislik")
        )
        return Response(list(items))
    

class AiChatAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        message = (request.data.get("message") or "").strip()
        if not message:
            return Response({"error": "message required"}, status=400)

        api_key = getattr(settings, "OPENAI_API_KEY", None)
        if not api_key:
            return Response({"error": "OPENAI_API_KEY missing"}, status=500)

        try:
            r = requests.post(
                "https://api.openai.com/v1/responses",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
  "model": "gpt-4o-mini",
  "input": [
    {
      "role": "developer",
      "content": (
        "Siz FindDoc ilovasi uchun tibbiy yo‘naltiruvchi (triage) yordamchisiz.\n"
        "Vazifa: foydalanuvchining shikoyatiga qarab qaysi mutaxassisga borishni tavsiya qiling.\n"
        "Qoidalar:\n"
        "1) Tashxis qo‘ymang, dorini buyurmang.\n"
        "2) Javob UZBEK (lotin) tilida bo‘lsin.\n"
        "3) Avval 2-4 ta aniqlashtiruvchi savol bering (zarur bo‘lsa).\n"
        "4) Keyin 1-3 ta ehtimoliy mutaxassis variantini tartib bilan bering.\n"
        "5) Agar xavfli belgi bo‘lsa (kuchli ko‘krak og‘rig‘i, hushdan ketish, falaj, nafas qisilishi, "
        "yuqori isitma+bo‘yin qotishi, to‘satdan eng kuchli bosh og‘riq, qon ketish, juda kuchli shish/allergiya) "
        "— 'Tez yordam/103' deb alohida ogohlantiring.\n"
        "Format (majburiy):\n"
        "Savollar:\n"
        "- ...\n"
        "Tavsiya:\n"
        "1) ...\n"
        "2) ...\n"
        "Ogohlantirish:\n"
        "- ... (agar kerak bo‘lsa, aks holda 'Yo‘q')"
      ),
    },
    {"role": "user", "content": message},
  ],
},
                timeout=30,
            )

            # ✅ OpenAI xatolarini status bilan qaytarish
            if r.status_code >= 400:
                try:
                    err = r.json()
                except Exception:
                    err = {"raw": r.text}

                # OpenAI ko‘p holatda {"error": {...}} qaytaradi
                payload = err.get("error") if isinstance(err, dict) else None
                code = None
                msg = None
                if isinstance(payload, dict):
                    code = payload.get("code") or payload.get("type")
                    msg = payload.get("message")
                else:
                    msg = r.text

                return Response(
                    {
                        "error": "OpenAI error",
                        "status": r.status_code,
                        "code": code,
                        "message": msg,
                    },
                    status=r.status_code,  # 401, 402, 429...
                )

            data = r.json()

            reply = (data.get("output_text") or "").strip()

            if not reply:
                parts = []
                for item in data.get("output", []):
                    for c in item.get("content", []):
                        if c.get("type") in ("output_text", "text"):
                            parts.append(c.get("text", ""))
                reply = "".join(parts).strip()

            if not reply:
                reply = "Kechirasiz, javob kelmadi. Qayta urinib ko‘ring."

            return Response({"reply": reply})

        except requests.Timeout:
            return Response({"error": "OpenAI timeout"}, status=504)
        except Exception as e:
            return Response({"error": str(e)}, status=500)