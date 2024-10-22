from django.shortcuts import render
from userauth.serializers import StaffSerializer
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from userauth.Rolepermission import IsAdmin, IsStudent, IsStaff, IsSuperAdmin
from userauth.models import Staff


class StaffView(APIView):
    permission_classes = [IsStaff | IsAdmin | IsSuperAdmin]

    def get(self, request, pk=None, *args, **kwargs):
        if pk:  # Retrieve a specific student
            staff = self.get_object(pk)
            if isinstance(staff, Response):  # If the response is an error response
                return staff  # Return the error response
            serializer = StaffSerializer(staff)
            return Response(serializer.data)
        else:  # List all students
            staff = Staff.objects.all()
            serializer = StaffSerializer(staff, many=True)
            return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        user = request.user.id  # Get the user ID
        if Staff.objects.filter(user=user).exists():
            return Response({"detail": "A staff record already exists for this user."}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()  # Create a copy of request data
        data['user'] = user  # Add user ID

        serializer = StaffSerializer(data=data)  # Use the modified data
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, *args, **kwargs):
        staff = self.get_object(pk)
        if isinstance(staff, Response):  # Check if an error response was returned
            return staff
        serializer = StaffSerializer(staff, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        staff = self.get_object(pk)
        if isinstance(staff, Response):  # Check if an error response was returned
            return staff
        serializer = StaffSerializer(
            staff, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        staff = self.get_object(pk)
        if isinstance(staff, Response):  # Check if an error response was returned
            return staff
        staff.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object(self, pk):
        try:
            return Staff.objects.get(pk=pk)
        except Staff.DoesNotExist:
            return Response({"detail": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
