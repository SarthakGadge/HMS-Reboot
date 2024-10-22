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


class GetHostelView(APIView):
    pass
