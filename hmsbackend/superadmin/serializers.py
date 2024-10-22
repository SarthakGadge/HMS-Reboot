from rest_framework import serializers
from userauth.models import Admin, CustomUser


class AdminCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = '__all__'


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
            role='admin'
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
