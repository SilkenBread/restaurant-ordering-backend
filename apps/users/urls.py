from .routers import router
from django.urls import path, include
from .views import LoginAPIView, LogoutAPIView, PasswordChangeAPIView, RegisterAPIView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('', include(router.urls)),
    
    path('auth/login/', LoginAPIView.as_view(), name='login'),
    path('auth/register/', RegisterAPIView.as_view(), name='register'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', LogoutAPIView.as_view(), name='logout'),
    path('auth/password/change/', PasswordChangeAPIView.as_view(), name='password-change'),
]
