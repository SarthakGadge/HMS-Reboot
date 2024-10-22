from django.urls import path, include
from .views import AdminViewSet, CreateAdminView


urlpatterns = [
    path('manage_admins/', CreateAdminView.as_view(), name="register admin"),
    path('manage_admins/<int:pk>/',
         CreateAdminView.as_view(), name='retrieve_admin'),

]
