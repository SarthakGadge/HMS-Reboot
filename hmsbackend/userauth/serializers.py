from rest_framework import serializers
from .models import CustomUser, Student, Admin, Staff
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['role', 'username', 'email']  # Add more fields as needed


# id is added as a field in the serializer for bed id and wasnt there before
class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'
