from userauth.utils import generate_and_send_otp
from django.contrib.auth import get_user_model
import json
import random
import jwt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.contrib.auth import get_user_model, authenticate, login
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .Rolepermission import IsStudent, IsAdmin, IsStaff
from .models import Student, Admin, Staff
from .serializers import StudentSerializer, StaffSerializer, UserSerializer
from django.utils import timezone
from .utils import generate_and_send_otp


User = get_user_model()


# Send otp via email
def send_otp_via_email(user, otp, purpose="authentication"):
    """
    Send OTP via Email.
    """
    subject = f"Your OTP for {purpose}"
    message_template = f"""
    Dear {user.username},

    Your OTP for {purpose} is: {otp}

    This OTP will expire in 10 minutes.

    If you didn't request this OTP, please ignore this email.

    Best regards,
    HMS Team
    """

    # Create the email
    email_message = EmailMultiAlternatives(
        subject=subject,
        body=message_template.format(otp=otp),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    # Send the email
    response = email_message.send()

    # Return True if the email was sent successfully, otherwise False
    return bool(response)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = User.objects.get(email=email)

            if not user.check_password(password):
                return Response({"msg": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

            if not user.is_active:
                if user.can_send_otp():
                    otp = str(random.randint(1000, 9999))
                    user.otp = otp
                    user.otp_expiry = timezone.now() + timezone.timedelta(minutes=10)
                    user.max_otp_try -= 1
                    if user.max_otp_try == 0:
                        user.otp_max_out = timezone.now() + timezone.timedelta(hours=1)
                    user.save()
                    send_otp_via_email(user, otp)
                    return Response({"msg": "Your email address has not been verified. An OTP has been sent to your email for account activation"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'msg': "Max OTP attempts reached. Try again later."}, status=status.HTTP_400_BAD_REQUEST)

            # User is active and password is correct
            authenticated_user = authenticate(
                request, email=email, password=password)
            if authenticated_user:
                login(request, authenticated_user)
                refresh = RefreshToken.for_user(authenticated_user)

                # Create a custom JWT token
                payload = {
                    'user_id': authenticated_user.id,
                    'username': authenticated_user.username,
                    'email': authenticated_user.email,
                    'role': authenticated_user.role
                }
                jwt_token = jwt.encode(
                    payload, settings.SECRET_KEY, algorithm='HS256')

                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'jwt_token': jwt_token,  # Include the JWT token in the response
                    'username': authenticated_user.username,
                    'email': authenticated_user.email,
                    'role': authenticated_user.role,
                }, status=status.HTTP_200_OK)
            else:
                return Response({"msg": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        except User.DoesNotExist:
            return Response({'msg': "User not found"}, status=status.HTTP_404_NOT_FOUND)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        try:
            user = User.objects.get(email=email)

            if user.otp == otp and user.is_otp_valid():
                user.is_active = True
                user.otp = None
                user.otp_expiry = None
                user.max_otp_try = 5
                user.otp_max_out = None
                user.save()

                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            else:
                return Response({'msg': "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({'msg': "Invalid OTP"}, status=status.HTTP_404_NOT_FOUND)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        role = request.data.get('role')

        required_fields = ['username', 'email', 'password', 'role']

        for field in required_fields:
            if not request.data.get(field):
                return Response({'msg': f'{field.capitalize()} is required'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'msg': 'Username already in use.'}, status=400)

        # Additional validation for password complexity (optional)
        if len(password) < 8:
            return Response({'msg': 'Password must be at least 8 characters long.'}, status=400)

        if role not in ['student', 'staff',]:
            return Response({'msg': 'Invalid role selected.'})

        if User.objects.filter(email=email).exists():
            return Response({'msg': 'Email already in use.'})

        user = User.objects.create_user(
            username=username, email=email, password=password, role=role)
        user.is_active = False  # Deactivate account until email is verified
        user.save()

        # Generate OTP and send it via email
        if generate_and_send_otp(user):
            return Response({'msg': "Verify your email to complete registration. OTP sent for account activation"})
        else:
            return Response({"msg": "Error sending OTP. Please try again later."})


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.user.email
        role = request.user.role
        username = request.user.username
        data = {
            'email': email,
            'role': role,
            'username': username
        }
        return Response(data)


'''
{
    "email": "user@example.com"
}

next verify ->

{
    "email": "user@example.com",
    "otp": "1234",
    "new_password": "newSecurePassword123"
}

'''


class ForgotPasswordRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)
            otp = str(random.randint(1000, 9999))
            user.password_reset_otp = otp
            user.password_reset_otp_expiry = timezone.now() + timezone.timedelta(minutes=10)
            user.save()

            send_otp_via_email(user, otp, purpose="password reset")

            return Response({"message": "Password reset OTP sent to your email"}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)


class ForgotPasswordVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        if not all([email, otp, new_password]):
            return Response({"error": "Email, OTP, and new password are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)

            if user.password_reset_otp == otp and user.password_reset_otp_expiry > timezone.now():
                # OTP is valid, reset the password
                user.set_password(new_password)
                user.password_reset_otp = None
                user.password_reset_otp_expiry = None
                user.save()

                return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)


User = get_user_model()


class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            # print(user.username)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user's account is already active
        if user.is_active == 1:
            return Response({"error": "This account is already active"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            generate_and_send_otp(user=user)
            return Response({"msg": "Your email address has not been verified. An OTP has been sent to your email for account activation"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": "Problem while sending OTP"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RetrieveUserCredentialsView(APIView):

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)
