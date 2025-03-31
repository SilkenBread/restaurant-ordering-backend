from django.urls import path
from .views.user_views import BulkUserCreateAPIView, BulkUserTaskStatusAPIView, UserListCreateAPIView, UserRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('', UserListCreateAPIView.as_view(), name='user-list'),
    path('<int:user_id>/', UserRetrieveUpdateDestroyAPIView.as_view(), name='user-retrieve-update-destroy'),

    path('bulk/', BulkUserCreateAPIView.as_view(), name='bulk-user-create'),
    path('bulk/status/<str:task_id>/', BulkUserTaskStatusAPIView.as_view(), name='bulk-user-status')
]
