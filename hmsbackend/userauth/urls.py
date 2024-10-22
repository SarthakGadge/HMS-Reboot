from django.urls import path
from userauth.views import RetrieveUserCredentialsView
from .views import RegisterView, LoginView, UserProfileView, VerifyOTPView, ForgotPasswordRequestView, ForgotPasswordVerifyView, ResendOTPView
# from .views import StudentProfileView, AdminProfileView, StaffProfileView, , StudentModifyAPIView, StaffModifyView, DatasetForAdmin


urlpatterns = [
    # Authentication Urls
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('forgot-password/', ForgotPasswordRequestView.as_view(),
         name='forgot-password-request'),
    path('reset-password/', ForgotPasswordVerifyView.as_view(),
         name='forgot-password-verify'),
    path('user/', UserProfileView.as_view(), name='user-profile'),
    path('resend_otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('current-user/', RetrieveUserCredentialsView.as_view(),
         name='retrieve-user-credentials'),

    # path('student/', StudentProfileView.as_view(), name='student-view'),
    # path('adminview/', AdminProfileView.as_view(), name='admin-view'),
    # path('staff/', StaffProfileView.as_view(), name='staff-view'),
    # path('staff&student/', DatasetForAdmin.as_view(),
    #  name='staff and student view'),
    # path('modify_student/<int:student_id>/', StudentModifyAPIView.as_view(),
    #  name='modify-student'),  # Correct URL pattern
    # path('modify_staff/<int:staff_id>/', StaffModifyView.as_view(),
    #  name='modify-student'),  # Correct URL pattern
]
