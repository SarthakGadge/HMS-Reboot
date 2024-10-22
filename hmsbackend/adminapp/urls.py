from .views import StudentViewForAdmin, DatasetForAdmin, AdminProfileView, CreateUserView
from django.urls import path

urlpatterns = [
    # path('admin_studentview/', CreateStudentView.as_view(), name='create-student'),
    # path('admin_staffview/', CreateStaffView.as_view(), name='create-staff'),
    path('student_info/', StudentViewForAdmin.as_view(), name='create-staff'),
    path('adminview/', AdminProfileView.as_view(), name='get_adminview'),
    path('create_user/', CreateUserView.as_view(),
         name='create-user-by-admin/superadmin'),
    path('staff&student/', DatasetForAdmin.as_view(),
         name='staff and student view'),



]
