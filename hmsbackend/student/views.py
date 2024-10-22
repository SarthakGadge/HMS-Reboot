from django.shortcuts import render
from userauth.serializers import StudentSerializer
from userauth.models import Student
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from userauth.Rolepermission import IsAdmin, IsStudent, IsStaff, IsSuperAdmin
from django.contrib.auth import get_user_model, authenticate, login
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


class StudentView(APIView):
    permission_classes = [IsStudent | IsAdmin | IsSuperAdmin]

    def get(self, request, pk=None, *args, **kwargs):
        if pk:  # Retrieve a specific student
            student = self.get_object(pk)
            if isinstance(student, Response):  # If the response is an error response
                return student  # Return the error response
            serializer = StudentSerializer(student)
            return Response(serializer.data)
        else:  # List all students
            students = Student.objects.all()
            serializer = StudentSerializer(students, many=True)
            return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        user = request.user.id  # Get the user ID
        if Student.objects.filter(user=user).exists():
            return Response({"detail": "A student record already exists for this user."}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()  # Create a copy of request data
        data['user'] = user  # Add user ID

        serializer = StudentSerializer(data=data)  # Use the modified data
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, *args, **kwargs):
        student = self.get_object(pk)
        if isinstance(student, Response):  # Check if an error response was returned
            return student
        serializer = StudentSerializer(student, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        student = self.get_object(pk)
        if isinstance(student, Response):  # Check if an error response was returned
            return student
        serializer = StudentSerializer(
            student, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        student = self.get_object(pk)
        if isinstance(student, Response):  # Check if an error response was returned
            return student
        student.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object(self, pk):
        try:
            return Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response({"detail": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
