from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HostelViewSet, HostelOccupancyView, Gethostelview

router = DefaultRouter()
router.register(r'hostels', HostelViewSet, basename='hostel')

urlpatterns = [
    path('', include(router.urls)),
    path("occupancy_per_hostel/", HostelOccupancyView.as_view(),
         name="occupancy_per_hostel"),
    path("get_hostel/", Gethostelview.as_view(), name='get_hostel')
]
