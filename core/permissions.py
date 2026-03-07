# D:\BMI\core\permissions.py

from rest_framework import permissions

class IsKlinikaOwner(permissions.BasePermission):
    """
    Ruxsat faqat Klinika ob'ektining egasi (owner) bo'lganlarga beriladi.
    Superuser hamma narsaga ruxsat oladi.
    """
    def has_object_permission(self, request, view, obj):
        # Superuserlar har doim ruxsatga ega
        if request.user.is_superuser:
            return True
            
        # O'qish (GET, HEAD, OPTIONS) ruxsatlari har doim ruxsat etiladi (ochiq API)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Yozish (PUT, PATCH, DELETE) faqat ob'ektning egasi (owner) bo'lganlarga ruxsat etiladi.
        # obj bu yerda Klinika ob'ekti, uning owner maydoni bor.
        return obj.owner == request.user
    
    # D:\BMI\core\permissions.py

class IsAdminKlinika(permissions.BasePermission):
    message = "Bu amalni faqat Klinikaga bog'langan Adminlar bajara oladi."

    def has_permission(self, request, view):
        user = request.user
        
        # 1. Superuserlar har doim ruxsat oladi (bu mantiq to'g'ri)
        if user.is_superuser:
            return True
        
        # 2. Tizimga kirgan va Admin (is_staff) statusiga ega ekanligini tekshirish
        if not user.is_authenticated:
            return False
        
        # 3. Klinika bog'lanishini tekshirish (Admin Profil orqali)
        try:
            # Agar user.admin_profil mavjud bo'lsa
            if hasattr(user, 'admin_profil') and user.admin_profil.klinika is not None:
                return True
        except AttributeError:
            # Agar 'admin_profil' related_name topilmasa (lekin bu yerdagi rasmda u mavjud)
            pass 
            
        return False
    
class IsShifokor(permissions.BasePermission):
    """
    Faqat shifokor maqomiga ega foydalanuvchilarga ruxsat beradi.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and hasattr(request.user, 'shifokor_profil'))
    
class IsSuperAdmin(permissions.BasePermission):
    message = "Bu amalni faqat Super Admin bajara oladi."

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        # Django superuser ham ruxsat
        if user.is_superuser:
            return True
        # AdminProfil orqali rol
        return hasattr(user, "admin_profil") and user.admin_profil.rol == "super_admin"


class IsClinicAdmin(permissions.BasePermission):
    message = "Bu amalni faqat Klinika Admin bajara oladi."

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        return (
            hasattr(user, "admin_profil")
            and user.admin_profil.rol == "klinika_admin"
            and user.admin_profil.klinika is not None
        )