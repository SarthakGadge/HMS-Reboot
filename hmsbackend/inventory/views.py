from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Inventory
from .serializers import InventorySerializer
from userauth.Rolepermission import IsStaff, IsAdmin
from django.shortcuts import get_object_or_404
from userauth.models import Staff, Admin


class InventoryCreateView(APIView):

    def post(self, request, *args, **kwargs):

        user = request.user.id

        if request.user.role not in ['admin', 'staff', 'superadmin']:
            return Response({"msg": "You do not have the authorization for this action"}, status=status.HTTP_401_UNAUTHORIZED)

        staff = get_object_or_404(Staff, user_id=user)
        data = request.data.copy()
        data['status'] = 'not_approved'
        data['staff'] = staff.id
        data['admin'] = None
        serializer = InventorySerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):

        if request.user.role not in ['admin', 'superadmin']:
            return Response({"msg": "You do not have the authorization for this action"}, status=status.HTTP_401_UNAUTHORIZED)

        inventory_item = get_object_or_404(Inventory, pk=pk)
        user_id = request.user.id
        admin = get_object_or_404(Admin, user_id=user_id)
        if inventory_item.status == 'not_approved':
            inventory_item.status = 'approved'
            inventory_item.admin = admin
            inventory_item.save()

            serializer = InventorySerializer(inventory_item)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"detail": "Already approved"}, status=status.HTTP_400_BAD_REQUEST)
