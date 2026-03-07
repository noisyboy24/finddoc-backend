# D:\BMI\core\backends.py

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Foydalanuvchi

User = get_user_model()

class EmailOrPhoneBackend(ModelBackend):
    """
    Foydalanuvchi Username o'rniga Telefon raqam yoki Email kiritganda ham ishlashini ta'minlaydi.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('username')
            
        try:
            # 1. Avval oddiy username (yoki biz saqlagan tel raqam) bo'yicha qidiramiz
            user = User.objects.get(Q(username=username) | Q(email=username))
        except User.DoesNotExist:
            # 2. Agar topilmasa, Foydalanuvchi modelidagi tel_raqam orqali qidiramiz
            try:
                profil = Foydalanuvchi.objects.get(tel_raqam=username)
                user = profil.user
            except Foydalanuvchi.DoesNotExist:
                return None

        # Parol to'g'riligini tekshiramiz
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None