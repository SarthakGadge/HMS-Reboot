from django.urls import path, include
from .views import StaffView

urlpatterns = [
    path("staff/", StaffView.as_view(), name="staff"),
    path("staff/<int:pk>", StaffView.as_view(), name="staff"),
]
