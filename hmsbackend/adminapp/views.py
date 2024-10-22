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
from .serializers import CustomUserStaffSerializer, CustomUserStudentSerializer, CustomStudentSerializerForAdmin
from django.db.models import Count, Q
from django.db import models
from rooms.models import Room, Bed


class CreateStudentView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, *args, **kwargs):
        # Extract user data
        user_data = request.data.get('user', {})
        admin_id = request.data.get('admin_id')

        if not admin_id:
            return Response({"error": "Admin ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            admin = Admin.objects.get(pk=admin_id)
        except Admin.DoesNotExist:
            return Response({"error": "Admin not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate and create the CustomUser instance
        user_serializer = CustomUserStudentSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()  # Create the CustomUser instance
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Prepare student data with the created user and admin
        student_data = {
            'user': user.id,
            'admin': admin.id,
            'studentID': request.data.get('studentID'),
            'name': request.data.get('name'),
            'dob': request.data.get('dob'),
            'contact': request.data.get('contact'),
            'nationality': request.data.get('nationality'),
            'gender': request.data.get('gender', 'other'),
            'guardian_name': request.data.get('guardian_name'),
            'guardian_contact': request.data.get('guardian_contact'),
            'hostel': request.data.get('hostel'),

        }

        # Validate and create the Student instance
        student_serializer = StudentSerializer(data=student_data)
        if student_serializer.is_valid():
            student = student_serializer.save()
            return Response({
                "user": user_serializer.data,
                "student": student_serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(student_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        student = Student.objects.all()
        student_serializer = StudentSerializer(student, many=True)

        return Response({
            "student": student_serializer.data
        }, status=status.HTTP_200_OK)


class CreateStaffView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, *args, **kwargs):
        # Retrieve all staff members
        staff = Staff.objects.all()
        staff_serializer = StaffSerializer(staff, many=True)

        return Response({
            "staff": staff_serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user_data = {
            'username': request.data.get('user[username]'),
            'email': request.data.get('user[email]'),
            'password': request.data.get('user[password]')
        }
        admin_id = request.data.get('admin_id')
        # Validate admin ID
        if not admin_id:
            return Response({"error": "Admin ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            admin = Admin.objects.get(pk=admin_id)
        except Admin.DoesNotExist:
            return Response({"error": "Admin not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate and create the CustomUser
        user_serializer = CustomUserStaffSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()  # Create the CustomUser instance
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Prepare staff data (ensure user and admin are included)
        staff_data = {
            'user': user.id,  # Passing user instance to StaffSerializer
            'admin': admin.id,
            'name': request.data.get('name'),
            'shift': request.data.get('shift'),
            'Department': request.data.get('Department'),
            'gender': request.data.get('gender'),  # Add gender
            'email': request.data.get('email'),    # Add email
            'contact': request.data.get('contact'),
            'photo': request.FILES.get('photo'),
            'hostel': request.data.get('hostel'),
        }

        staff_serializer = StaffSerializer(data=staff_data)
        if staff_serializer.is_valid():
            staff = staff_serializer.save()
            return Response({
                "user": user_serializer.data,
                "staff": staff_serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(staff_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
