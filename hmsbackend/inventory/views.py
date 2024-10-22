from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Inventory
from .serializers import InventorySerializer
from userauth.Rolepermission import IsStaff, IsAdmin
from django.shortcuts import get_object_or_404
from userauth.models import Staff, Admin


class InventoryCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsStaff()]
        elif self.request.method == 'PATCH':
            return [IsAdmin()]
        return super().get_permissions()

    def post(self, request, *args, **kwargs):
        user = request.user.id  # Get the user ID from the access token

        # Fetch the corresponding staff instance based on the user ID
        staff = get_object_or_404(Staff, user_id=user)

        data = request.data.copy()  # Make a mutable copy of the incoming data
        data['status'] = 'not_approved'  # Force status to 'not_approved'
        data['staff'] = staff.id  # Assign the staff ID, not the object

        # Serialize and validate the data
        serializer = InventorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        # Get the inventory item by primary key
        inventory_item = get_object_or_404(Inventory, pk=pk)

        # Get the user ID from the access token
        user_id = request.user.id

        # Fetch the corresponding admin instance based on the user ID
        admin = get_object_or_404(Admin, user_id=user_id)

        # Only update the status to 'approved' if it's currently 'not_approved'
        if inventory_item.status == 'not_approved':
            inventory_item.status = 'approved'
            inventory_item.admin = admin  # Set the admin ID
            inventory_item.save()  # Save the updated inventory item

            serializer = InventorySerializer(inventory_item)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # If already approved, no change is needed
        return Response({"detail": "Already approved"}, status=status.HTTP_400_BAD_REQUEST)
