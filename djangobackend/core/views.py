from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

class WhoamiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "name": request.user.name,
            "email": request.user.email,
            "settings": request.user.settings,
            "uid": request.user.uid,
            "isAdmin": request.user.is_staff,
        })