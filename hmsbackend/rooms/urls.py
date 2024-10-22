from django.urls import path, include
from .views import RoomsOverviewView, BedViewSet, AmenityViewset, RoomStatsView, RoomViewSet, BedViewForAdmin
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'rooms', RoomViewSet, basename='room')
urlpatterns = [
    path('', include(router.urls)),
    path('rooms-overview/', RoomsOverviewView.as_view(), name='rooms-overview'),
    path('bed/', BedViewSet.as_view(), name='get_beds'),
    path('bed/<int:bed_id>/', BedViewSet.as_view(), name='bed-detail'),
    path('amenity/', AmenityViewset.as_view(), name='amenity'),
    path('admin_stats/', RoomStatsView.as_view(), name='RoomsBedsFloorView'),
    path('detailed_beds/', BedViewForAdmin.as_view(), name='bed_view'),
]
