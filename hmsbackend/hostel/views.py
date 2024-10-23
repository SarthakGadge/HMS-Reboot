from django.shortcuts import render
from rest_framework import viewsets
from userauth.Rolepermission import IsSuperAdmin
from .models import Hostel
from .serializers import HostelSerializer
from rest_framework.views import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rooms.models import Room, Bed


class HostelViewSet(viewsets.ModelViewSet):
    queryset = Hostel.objects.all()
    serializer_class = HostelSerializer

    def get_permissions(self):
        if self.request.method in ['GET']:
            return [IsAuthenticated()]
        return [IsSuperAdmin()]

    def list(self, request):
        hostels = self.queryset

        country = request.query_params.get('country')
        state = request.query_params.get('state')
        city = request.query_params.get('city')

        if country:
            hostels = hostels.filter(country__iexact=country)
        if state:
            hostels = hostels.filter(state__iexact=state)
        if city:
            hostels = hostels.filter(city__iexact=city)

        paginator = PageNumberPagination()
        paginator.page_size = None

        serializer = self.get_serializer(hostels, many=True)
        return Response(serializer.data)

    def create(self, request):
        required_fields = ['name', 'address', 'city', 'state',
                           'country', 'postal_code', 'contact_email', 'contact_phone']
        for field in required_fields:
            if not request.data.get(field):
                return Response({"msg": f"{field} is required."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        hostel = self.get_object()
        serializer = self.get_serializer(hostel)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        hostel = self.get_object()
        serializer = self.get_serializer(
            hostel, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        hostel = self.get_object()
        hostel.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class HostelOccupancyView(APIView):
    def get(self, request):
        if request.user.role not in ['admin', 'superadmin']:
            return Response({'msg': 'You do not have the authorization for this action.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            hostels = Hostel.objects.all()  # Get all hostels
            hostel_occupancies = []

            for hostel in hostels:
                # Get all rooms in the hostel
                rooms = Room.objects.filter(hostel=hostel)

                # Get total beds in all rooms of this hostel
                total_beds = Bed.objects.filter(room__in=rooms).count()

                # Get unavailable (occupied) beds in this hostel
                unavailable_beds = Bed.objects.filter(
                    room__in=rooms, status='unavailable').count()

                # Calculate occupancy percentage
                if total_beds == 0:
                    occupancy_percentage = 0
                else:
                    occupancy_percentage = (
                        unavailable_beds / total_beds) * 100

                # Add to result list
                hostel_occupancies.append({
                    "hostel_name": hostel.name,
                    # Rounded to 3 decimal places
                    "occupancy_percentage": round(occupancy_percentage, 3)
                })

            return Response({
                "hostel_occupancies": hostel_occupancies
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
