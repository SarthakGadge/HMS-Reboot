from django.db import models
from django.db.models import Count, Q
from rest_framework import viewsets, status
from rooms.models import Room
from rooms.serializers import RoomSerializer
from userauth.Rolepermission import IsAdmin, IsStaff, IsStudent, IsSuperAdmin
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Room, Bed, Amenity
from userauth.models import Student
from django.db.models import Count
# RoomBookingSerializer
from .serializers import RoomsOverviewSerializer, BedSerializer, AmenitySerializer, CustomBedSerializerForAdmin
from django_filters.rest_framework import DjangoFilterBackend
from .filters import RoomFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView


class RoomViewSet(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    queryset = Room.objects.all()
    filter_backends = [DjangoFilterBackend]  # Enable filtering
    filterset_class = RoomFilter

    def get_permissions(self):
        if self.action in ['get', 'retrieve']:
            return [IsAdmin(), IsStaff(), IsStudent()]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return super().get_permissions()

    def get(self, request, *args, **kwargs):
        room_instance = Room.objects.all()
        serializer = RoomSerializer(room_instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        admin_instance = self.request.user.admin_profile
        serializer.save(admin_id=admin_instance)

    def destroy(self, request, *args, **kwargs):
        room_instance = self.get_object()
        room_instance.delete()
        return Response({"message": "Room deleted successfully"}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs, partial=True)


class AmenityViewset(ListCreateAPIView):
    permission_classes = [IsAdmin]
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer


class BedViewSet(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        elif self.request.method in ["PUT"]:
            return [IsStudent()]
        elif self.request.method in ["DELETE"]:
            return [IsAdmin()]

    def get(self, request):
        bed_instance = Bed.objects.all()
        serializer = BedSerializer(bed_instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, bed_id):
        user_instance = request.user.id
        student_instance = get_object_or_404(Student, user_id=user_instance)
        bed_instance = get_object_or_404(Bed, id=bed_id)
        request.data['student'] = student_instance.id
        serializer = BedSerializer(bed_instance, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, bed_id):
        bed_instance = get_object_or_404(Bed, id=bed_id)
        bed_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoomsOverviewView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, *args, **kwargs):
        admin_instance = self.request.user.admin_profile
        rooms_count = Room.objects.filter(admin_id=admin_instance).count()
        floors = Room.objects.filter(admin_id=admin_instance).values(
            'floor_number').annotate(room_count=Count('id'))

        data = {
            'admin_id': admin_instance.id,
            'total_room_count': rooms_count,
            'rooms_per_floor': [
                {
                    'floor_number': floor['floor_number'],
                    'room_count': floor['room_count']
                }
                for floor in floors
            ]
        }

        serializer = RoomsOverviewSerializer(data)
        return Response(serializer.data)


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


class BedViewForAdmin(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        beds = Bed.objects.select_related('room').all()
        serializer = CustomBedSerializerForAdmin(beds, many=True)
        return Response(serializer.data)

class BedOccupancyView(APIView):
        """
        API to get bed occupancy percentage based on unavialbale beds.
        """
        def get(self, requset):
            try:
                occupancy = Bed.occupancy_percentage()
                return Response({
                    "Occupancy_percentage" : occupancy
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    "error" : str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
