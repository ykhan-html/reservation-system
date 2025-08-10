from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'services', views.ServiceViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'providers', views.ServiceProviderViewSet)
router.register(r'provider-reservations', views.ServiceProviderReservationViewSet, basename='provider-reservation')
router.register(r'reservations', views.ReservationViewSet, basename='reservation')
router.register(r'reviews', views.ReviewViewSet, basename='review')
router.register(r'business-hours', views.BusinessHoursViewSet)
router.register(r'notices', views.NoticeViewSet)
router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_page, name='register_page'),
    path('login/', views.login_page, name='login_page'),
    path('profile/', views.profile_page, name='profile_page'),
    path('product-management/', views.product_management_page, name='product_management_page'),
    path('provider-management/', views.provider_management_page, name='provider_management_page'),
    path('provider-login/', views.provider_login_page, name='provider_login_page'),
    path('provider-dashboard/', views.provider_dashboard_page, name='provider_dashboard_page'),
    path('api/', include(router.urls)),
    path('api/register/', views.RegisterView.as_view(), name='register'),
    path('api/login/', views.LoginView.as_view(), name='login'),
    path('api/logout/', views.LogoutView.as_view(), name='logout'),
    path('api/profile/update/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('api/provider/login/', views.ServiceProviderLoginView.as_view(), name='provider_login'),
    path('api/provider/logout/', views.ServiceProviderLogoutView.as_view(), name='provider_logout'),
    path('api/services/<int:service_id>/check_time_updates/', views.check_time_updates, name='check_time_updates'),
] 