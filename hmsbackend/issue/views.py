# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Issue, Bed
from userauth.models import Student
from django.shortcuts import get_object_or_404
from .serializers import IssueSerializer
from userauth.Rolepermission import IsAdmin, IsStudent


class CreateIssueView(APIView):
    def post(self, request):
        user_id = request.user.id
        student = get_object_or_404(Student, user_id=user_id)
        bed = get_object_or_404(Bed, student=student)
        room = bed.room  # Assuming the Bed model has a ForeignKey to Room

        # Create the Issue
        description = request.data.get('description', None)
        if not description:
            return Response({'error': 'Description is required'}, status=status.HTTP_400_BAD_REQUEST)

        issue = Issue.objects.create(
            student=student, room=room, bed=bed, description=description)

        return Response({'message': 'Issue created successfully', 'issue_id': issue.id}, status=status.HTTP_201_CREATED)


class GetIssueView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        issue_instance = Issue.objects.all()
        serializer = IssueSerializer(issue_instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
