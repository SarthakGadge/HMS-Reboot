from rest_framework import serializers
from userauth.models import CustomUser
from userauth.models import Student


class UserCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
            role=validated_data['role']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


# class CustomUserStudentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = ['id', 'username', 'email', 'password']
#         extra_kwargs = {'password': {'write_only': True}}

#     def create(self, validated_data):
#         user = CustomUser(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             role='student'
#         )
#         user.set_password(validated_data['password'])
#         user.save()
#         return user


class CustomStudentSerializerForAdmin(serializers.ModelSerializer):
    room_number = serializers.IntegerField(
        source='bed_set.first.room.room_number', read_only=True)
    floor_number = serializers.IntegerField(
        source='bed_set.first.room.floor_number', read_only=True)
    check_in_date = serializers.DateField(
        source='bed_set.first.checkIn_date', read_only=True)
    check_out_date = serializers.DateField(
        source='bed_set.first.checkOut_date', read_only=True)

    bed_id = serializers.IntegerField(
        source='bed_set.first.id', read_only=True)  # Add bed ID
    room_id = serializers.IntegerField(
        source='bed_set.first.room.id', read_only=True)  # Add room ID

    class Meta:
        model = Student
        fields = "__all__"
