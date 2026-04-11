from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .models import UserProfile
from .serializers import RegisterSerializer,UserProfileSerializer


# Create your views here.
class RegisterView(generics.CreateAPIView):
    queryset=User.objects.all()
    serializer_class=RegisterSerializer
    permission_classes=[permissions.AllowAny]


class UserProfileView(APIView):
    permission_classes=[permissions.IsAuthenticated]

    def get(self,request):
        try:
            profile=UserProfile.objects.get(user=request.user)
            serializer=UserProfileSerializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response(
                {"message":"Profile not created yet"},
                status=status.HTTP_404_NOT_FOUND
            )
        
    def post(self,request):
        if UserProfile.objects.filter(user=request.user).exists():
            return Response(
                {"message":"Profile already exists.Use PUT to update"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer=UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self,request):
        try:
            profile=UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response(
                {"message":"Profile not created yet.Use POST to create"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer=UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
