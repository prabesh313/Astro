from rest_framework import serializers
from django.contrib.auth.models import User
from .models import PriestSchedule, UserProfile, Chat, Message, Review
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    user_type = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'user_type']

    def create(self, validated_data):
        user_type = validated_data.pop('user_type')
        user = User.objects.create_user(username=validated_data['username'],email=validated_data['email'],password=validated_data['password'])
        UserProfile.objects.create(user=user,user_type=user_type,full_name=validated_data['username'])
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    user_type_display = serializers.CharField(
        source='get_user_type_display', read_only=True
    )

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'user_type', 'user_type_display','full_name', 'birth_date', 'birth_time', 'birth_place',
            'birth_latitude', 'birth_longitude', 'is_verified','specializations', 'experience_years', 'hourly_rate',
            'phone_number', 'address', 'bio', 'profile_image','average_rating', 'total_reviews', 'created_at'
        ]


class PriestListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'full_name', 'specializations', 'experience_years','hourly_rate', 'average_rating', 'total_reviews', 'profile_image','is_verified', 'bio'
        ]


class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'sender_username', 'message_text','attachment', 'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'is_read']


class ChatSerializer(serializers.ModelSerializer):
    jajaman_username = serializers.CharField(source='jajaman.username', read_only=True)
    purohit_username = serializers.CharField(source='purohit.username', read_only=True)
    purohit_profile = PriestListSerializer(source='purohit.userprofile', read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = [
            'id', 'jajaman', 'jajaman_username', 'purohit', 'purohit_username','purohit_profile', 'is_active', 'created_at', 'updated_at','last_message', 'unread_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
            return MessageSerializer(last_msg).data
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0


class ReviewSerializer(serializers.ModelSerializer):
    jajaman_username = serializers.CharField(source='jajaman.username', read_only=True)
    jajaman_name = serializers.CharField(source='jajaman.userprofile.full_name', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'purohit', 'jajaman', 'jajaman_username', 'jajaman_name','rating', 'comment', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PriestScheduleSerializer(serializers.ModelSerializer):
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    class Meta:
        model = PriestSchedule
        fields = ['id', 'busy_date', 'event_type', 'event_type_display','event_title', 'start_time', 'end_time', 'location', 'contact_person', 'phone_number', 'created_at','notes' 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class BusyDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriestSchedule
        fields = ['id', 'busy_date']