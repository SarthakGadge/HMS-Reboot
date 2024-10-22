from rest_framework import serializers
from rooms.models import Room, Amenity, Bed  # RoomBooking
import base64


class BedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bed
        fields = '__all__'


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = "__all__"


class RoomSerializer(serializers.ModelSerializer):
    amenities = serializers.PrimaryKeyRelatedField(
        queryset=Amenity.objects.all(),
        many=True
    )

    class Meta:
        model = Room
        fields = '__all__'


class RoomsPerFloorSerializer(serializers.Serializer):
    floor_number = serializers.IntegerField()
    room_count = serializers.IntegerField()


class CustomBedSerializerForAdmin(serializers.ModelSerializer):
    room = RoomSerializer()

    class Meta:
        model = Bed
        fields = ['checkIn_date', 'checkOut_date', 'room',
                  'status', 'duration', 'student', 'room']


class RoomsOverviewSerializer(serializers.Serializer):
    admin_id = serializers.IntegerField()
    total_room_count = serializers.IntegerField()
    rooms_per_floor = RoomsPerFloorSerializer(many=True)
