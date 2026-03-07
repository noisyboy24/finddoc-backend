# D:\BMI\core\filters.py - YAKUNIY TUZATILGAN KOD

import django_filters
from .models import Shifokor, KlinikaTekshiruvi

class ShifokorFilter(django_filters.FilterSet):
    """
    Shifokorlarni filtrlash. Jinsi filtri 'Ayol'/'Erkak' so'zlarini 'A'/'E' kodlariga tarjima qiladi.
    Ish Staji (yillar) bo'yicha diapazon filtrlari qo'shildi.
    """
    
    # Ish staji diapazon filtrlari (Yangi qo'shildi)
    ish_staji_min = django_filters.NumberFilter(field_name='ish_staji', lookup_expr='gte') # Katta yoki teng (Minimum)
    ish_staji_max = django_filters.NumberFilter(field_name='ish_staji', lookup_expr='lte') # Kichik yoki teng (Maksimum)

    # Boshqa filtrlarga o'zgartirish kiritilmadi (Ular allaqachon ishlayapti)
    mutaxassislik = django_filters.CharFilter(field_name='mutaxassislik', lookup_expr='iexact')
    klinika = django_filters.CharFilter(field_name='klinika__nom', lookup_expr='icontains') 
    jinsi = django_filters.CharFilter(method='filter_by_jinsi') 
    qabul_narxi_min = django_filters.NumberFilter(field_name='qabul_narxi', lookup_expr='gte')
    qabul_narxi_max = django_filters.NumberFilter(field_name='qabul_narxi', lookup_expr='lte')

    class Meta:
        model = Shifokor
        fields = [
            'mutaxassislik', 
            'klinika', 
            'jinsi', 
            'qabul_narxi_min', 
            'qabul_narxi_max',
            # Yangi maydonlar Meta'ga qo'shildi:
            'ish_staji_min', 
            'ish_staji_max'
        ] 
    
    # filter_by_jinsi funksiyasi (o'zgarishsiz)
    def filter_by_jinsi(self, queryset, name, value):
        value_lower = value.lower() 
        if value_lower == 'ayol' or value_lower == 'a':
            return queryset.filter(jinsi__iexact='A')
        elif value_lower == 'erkak' or value_lower == 'e':
            return queryset.filter(jinsi__iexact='E')
        return queryset
        
class KlinikaTekshiruviFilter(django_filters.FilterSet):
    # Klinika nomlari bo'yicha qisman qidiruvni qo'shish
    klinika_nomi = django_filters.CharFilter(
        field_name='klinika__nom', 
        lookup_expr='icontains',
        label='Klinika nomi bo\'yicha qidiruv' # Swagger UI da yaxshi ko'rinishi uchun
    )
    
    class Meta:
        model = KlinikaTekshiruvi 
        fields = {
            'nom': ['icontains'], # Tekshiruv nomi bo'yicha qisman qidiruv
            'narx': ['lte', 'gte'], # Narx bo'yicha diapazon
        }
