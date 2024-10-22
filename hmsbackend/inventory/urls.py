from django.urls import path
from .views import InventoryCreateView

urlpatterns = [
    path("inventory/", InventoryCreateView.as_view(),
         name="post_inventory_for_admin"),
    path("inventory/<int:pk>/", InventoryCreateView.as_view(),
         name="update_request_for_admin"),
]
