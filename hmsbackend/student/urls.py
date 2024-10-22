from django.urls import path, include
from .views import StudentView


urlpatterns = [
    path('students/', StudentView.as_view(), name='Student_view'),
    path('students/<int:pk>/', StudentView.as_view(), name='student-detail'),
]
