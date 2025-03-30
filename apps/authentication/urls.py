from django.urls import path
from .views.auth_views import LoginAPIView, LogoutAPIView, PasswordChangeAPIView

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='auth-login'),
    path('logout/', LogoutAPIView.as_view(), name='auth-logout'),
    path('change-password/', PasswordChangeAPIView.as_view(), name='auth-change-password'),
]
