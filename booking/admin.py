from django.contrib import admin
from .models import Service, Reservation, Review, BusinessHours, Category, ServiceProvider


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    ordering = ['name']


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'username', 'phone', 'email', 'is_active', 'experience_years', 'created_at']
    list_filter = ['is_active', 'experience_years', 'created_at']
    search_fields = ['name', 'username', 'description', 'specialties', 'phone', 'email']
    list_editable = ['is_active']
    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'description', 'image')
        }),
        ('로그인 정보', {
            'fields': ('username', 'password')
        }),
        ('연락처 정보', {
            'fields': ('phone', 'email')
        }),
        ('전문 정보', {
            'fields': ('specialties', 'experience_years')
        }),
        ('상태 관리', {
            'fields': ('is_active',)
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    def save_model(self, request, obj, form, change):
        """비밀번호를 해싱하여 저장"""
        if 'password' in form.changed_data:
            from django.contrib.auth.hashers import make_password
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)
    
    def response_change(self, request, obj):
        """저장 후 목록으로 리다이렉트 (추가 버튼 제거)"""
        from django.contrib import messages
        from django.shortcuts import redirect
        from django.urls import reverse
        
        messages.success(request, f'서비스 제공자 "{obj.name}"이(가) 성공적으로 저장되었습니다.')
        return redirect(reverse('admin:booking_serviceprovider_changelist'))
    
    def response_add(self, request, obj, post_url_continue=None):
        """추가 후 목록으로 리다이렉트 (추가 버튼 제거)"""
        from django.contrib import messages
        from django.shortcuts import redirect
        from django.urls import reverse
        
        messages.success(request, f'서비스 제공자 "{obj.name}"이(가) 성공적으로 추가되었습니다.')
        return redirect(reverse('admin:booking_serviceprovider_changelist'))
    
    class Media:
        js = ('admin/js/hide_save_buttons.js',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'provider', 'price', 'duration', 'is_active', 'is_featured', 'stock_quantity', 'created_at']
    list_filter = ['is_active', 'is_featured', 'category', 'provider', 'created_at']
    search_fields = ['name', 'description', 'category__name', 'provider__name']
    list_editable = ['is_active', 'is_featured', 'stock_quantity']
    fieldsets = (
        ('기본 정보', {
            'fields': ('category', 'provider', 'name', 'description', 'image')
        }),
        ('가격 및 시간', {
            'fields': ('price', 'duration')
        }),
        ('상태 관리', {
            'fields': ('is_active', 'is_featured', 'stock_quantity')
        }),
        ('예약 설정', {
            'fields': ('min_advance_booking', 'max_advance_booking')
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-is_featured', 'name']


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['user_display', 'service', 'provider', 'date', 'time', 'status', 'created_at']
    list_filter = ['status', 'date', 'service', 'provider', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'service__name', 'provider__name', 'notes']
    list_editable = ['status']
    date_hierarchy = 'date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'service', 'provider')
    
    def user_display(self, obj):
        """사용자 성명 또는 아이디 표시"""
        return obj.user.first_name or obj.user.username
    user_display.short_description = '사용자'
    user_display.admin_order_field = 'user__first_name'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reservation', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['reservation__user__username', 'comment']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('reservation__user', 'reservation__service')


@admin.register(BusinessHours)
class BusinessHoursAdmin(admin.ModelAdmin):
    list_display = ['day', 'open_time', 'close_time', 'is_closed']
    list_filter = ['is_closed']
    list_editable = ['open_time', 'close_time', 'is_closed']
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('day')
