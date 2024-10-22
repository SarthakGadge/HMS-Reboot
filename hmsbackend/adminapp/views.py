from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from userauth.serializers import StaffSerializer, StudentSerializer
from superadmin.serializers import AdminCreationSerializer
from userauth.Rolepermission import IsAdmin
from userauth.models import Staff, Student, Admin
from .serializers import UserCreationSerializer, CustomStudentSerializerForAdmin
from django.db.models import Count, Q
from django.utils.crypto import get_random_string
from django.db import models
from rooms.models import Room, Bed
from userauth.utils import user_creation_and_welcome


class CreateUserView(APIView):
    def post(self, request):
        user_role = request.user.role

        # Only allow superadmin and admin to create users
        if user_role not in ['superadmin', 'admin']:
            return Response({"msg": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

        if not request.data.get('email'):
            return Response({"msg": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not request.data.get('username'):
            return Response({"msg": "Username is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not request.data.get('role'):
            return Response({"msg": "Role is required."}, status=status.HTTP_400_BAD_REQUEST)

        if request.data.get('role') not in ['staff', 'student']:
            return Response({"msg": "Please enter a valid role."}, status=status.HTTP_403_FORBIDDEN)

        temp_password = get_random_string(length=8)
        # Add the generated password to the request data
        request.data['password'] = temp_password
        serializer = UserCreationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Send the welcome email with the temporary credentials
            user_creation_and_welcome(user, temp_password)

            return Response({'message': 'User created successfully, an email has been sent to the user.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentViewForAdmin(ListAPIView):
    permission_classes = [IsAdmin]
    queryset = Student.objects.prefetch_related('bed_set__room').all()
    serializer_class = CustomStudentSerializerForAdmin


class DatasetForAdmin(APIView):
    def get(self, request):
        permission_classes = [IsAdmin]
        staff_members = Staff.objects.all()
        student_members = Student.objects.all()

        staff_data = StaffSerializer(staff_members, many=True)
        student_data = StudentSerializer(student_members, many=True)

        return Response({
            "staff": staff_data.data,
            "student": student_data.data
        }, status=status.HTTP_200_OK)


class RoomStatsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        # Total number of rooms
        total_rooms = Room.objects.count()

        # Total beds and their status counts
        total_beds = Bed.objects.count()
        # Assuming 'available' is used for vacant
        total_vacant_beds = Bed.objects.filter(status='available').count()
        total_occupied_beds = total_beds - total_vacant_beds

        # Total beds per floor (grouped by floor number)
        beds_per_floor = (
            Room.objects.values('floor_number')
            .annotate(total_beds=Count('bed'))
        )

        # Total occupied beds per floor
        occupied_beds_per_floor = (
            Room.objects.values('floor_number')
            .annotate(occupied_beds=Count('bed', filter=models.Q(bed__student__isnull=False)))
        )

        # Combining the data for available, unavailable, and occupancy rate per floor
        beds_info_per_floor = []
        for floor_data in beds_per_floor:
            floor_number = floor_data['floor_number']
            total_beds_on_floor = floor_data['total_beds']

            # Find occupied beds for the same floor
            occupied_beds_on_floor = next(
                (item['occupied_beds']
                 for item in occupied_beds_per_floor if item['floor_number'] == floor_number),
                0
            )

            # Calculate available beds on the floor
            available_beds_on_floor = total_beds_on_floor - occupied_beds_on_floor

            # Calculate occupancy rate for the floor
            occupancy_rate = (
                (occupied_beds_on_floor / total_beds_on_floor) * 100
                if total_beds_on_floor > 0 else 0
            )

            # Add floor data to the response list
            beds_info_per_floor.append({
                'floor_number': floor_number,
                'total_beds': total_beds_on_floor,
                'available_beds': available_beds_on_floor,
                'unavailable_beds': occupied_beds_on_floor,
                'occupancy_rate': round(occupancy_rate, 2)
            })

        # Constructing response data
        response_data = {
            'total_rooms': total_rooms,
            'total_beds': total_beds,
            'total_vacant_beds': total_vacant_beds,
            'total_occupied_beds': total_occupied_beds,
            'beds_per_floor': beds_info_per_floor  # Including detailed bed info per floor
        }

        return Response(response_data, status=status.HTTP_200_OK)


class AdminProfileView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        try:
            admin = Admin.objects.get(user=request.user)
            serializer = AdminCreationSerializer(admin)
            response_data = serializer.data
            response_data.pop('user', None)
            response_data['admin_id'] = admin.id
            return Response(response_data)
        except Admin.DoesNotExist:
            return Response({"detail": "Admin profile not found"}, status=status.HTTP_404_NOT_FOUND)
