from django.shortcuts import render
from .serializers import AdminCreationSerializer, CustomUserSerializer
from rest_framework import status
from rest_framework import viewsets
from userauth.models import Admin
from rest_framework.views import APIView
from userauth.Rolepermission import IsSuperAdmin
from rest_framework.views import Response


class CreateAdminView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request, *args, **kwargs):
        # Extract user data
        user_data = request.data.get('user', {})
        user_serializer = CustomUserSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()  # Create the CustomUser instance
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        student_data = {
            'user': user.id,
            'hostel': request.data.get('hostel'),
            'name': request.data.get('name'),
            'dob': request.data.get('dob'),
            'contact': request.data.get('contact'),
            'nationality': request.data.get('nationality'),
            'gender': request.data.get('gender', 'other'),
            'guardian_name': request.data.get('guardian_name'),
            'guardian_contact': request.data.get('guardian_contact')
        }

        # Validate and create the Student instance
        admin_serializer = AdminCreationSerializer(data=student_data)
        if admin_serializer.is_valid():
            student = admin_serializer.save()
            return Response({
                "user": user_serializer.data,
                "admin": admin_serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(admin_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        admins = Admin.objects.all()
        admin_serializer = AdminCreationSerializer(admins, many=True)
        return Response({
            "admins": admin_serializer.data
        }, status=status.HTTP_200_OK)

    def patch(self, request, pk, *args, **kwargs):
        try:
            admin = Admin.objects.get(pk=pk)
        except Admin.DoesNotExist:
            return Response({"msg": "Admin not found."}, status=status.HTTP_404_NOT_FOUND)
        admin_serializer = AdminCreationSerializer(
            admin, data=request.data, partial=True)
        if admin_serializer.is_valid():
            admin_serializer.save()
            return Response(admin_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(admin_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        try:
            admin = Admin.objects.get(pk=pk)
        except Admin.DoesNotExist:
            return Response({"msg": "Admin not found."}, status=status.HTTP_404_NOT_FOUND)
        admin.delete()
        return Response({"msg": "Admin deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class AdminViewSet(viewsets.ModelViewSet):
    admins = Admin.objects.all()
    serializer_class = AdminCreationSerializer
    permission_classes = [IsSuperAdmin]

    def list(self, request):
        admins = self.queryset
        serializer = self.get_serializer(admins, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        admin = self.get_object()
        serializer = self.get_serializer(admin)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        admin = self.get_object
        serializer = self.get_serializer(
            admin, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        admin = self.get_object()
        admin.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
