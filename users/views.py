from email.message import Message
from time import timezone
from warnings import filters

from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User

from rituals import serializers
from .models import Chat, Review, UserProfile
from .serializers import ChatSerializer, MessageSerializer, PriestListSerializer, RegisterSerializer, ReviewSerializer,UserProfileSerializer
from django.db.models import Q
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination


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

class PriestListView(generics.ListAPIView):
    queryset=UserProfile.objects.filter(user_type='purohit', is_verified=True)
    serializer_class=PriestListSerializer
    permission_classes=[permissions.AllowAny]
    filter_backends = [filters.SearchFilter,filters.OrderingFilter]
    search_fields = ['full_name', 'specializations', 'bio']
    ordering_fields = ['experience_years', 'average_rating']
    ordering = ['-average_rating' ]
    pagination_class = PageNumberPagination
class PriestDetailView(generics.RetrieveAPIView):
    queryset=UserProfile.objects.filter(user_type='purohit')
    serializer_class=PriestListSerializer
    permission_classes=[permissions.AllowAny]


class ChatListView(generics.ListAPIView):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return Chat.objects.filter(Q(jajaman=self.request.user) | Q(purohit=self.request.user)).prefetch_related('messages')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class ChatDetailView(generics.RetrieveAPIView):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Chat.objects.filter(Q(jajaman=self.request.user) | Q(purohit=self.request.user))
    

class StartChatView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        purohit_id = request.data.get('purohit_id')
        try:
            purohit_user = User.objects.get(id=purohit_id)
            purohit_profile = UserProfile.objects.get(user=purohit_user, user_type='purohit')
        except:
            return Response({"error": "Priest not found"}, status=status.HTTP_404_NOT_FOUND)
        
        chat , created = Chat.objects.get_or_create(jajaman=request.user, purohit=purohit_user)
        serializer = ChatSerializer(chat, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        return Message.objects.filter(chat_id=chat_id)
    
    def create(self, request, *args, **kwargs):
        chat_id = self.kwargs['chat_id']
        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return Response({"error": "Chat not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user != chat.jajaman and request.user != chat.purohit:
            return Response({"error": "Not a participant of this chat"}, status=status.HTTP_403_FORBIDDEN)
        
        message=Message.objects.create(chat=chat, sender=request.user, message_text=request.data.get('message_text', ''),attachment=request.FILES.get('attachment'))
        
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class MarkMessagesReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, chat_id):
        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return Response({"error": "Chat not found"}, status=status.HTTP_404_NOT_FOUND)
        
        messages = chat.messages.filter(is_read=False).exclude(sender=request.user)
        messages.update(is_read=True, read_at=timezone.now())

        return Response({"message": "Messages marked as read"})
    
class ReviewView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(jajaman=self.request.user)

class ReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        priest_id = self.kwargs['priest_id']
        return Review.objects.filter(purohit_id=priest_id)