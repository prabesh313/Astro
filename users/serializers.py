from rest_framework import serializers
from .models import UserProfile
from django.contrib.auth.models import User

class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True)

    class Meta:
        model=User
        fields=['username','email','password']

    def create(self,validated_data):
        user=User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']

        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    username=serializers.CharField(source='user.username', read_only=True)
    email=serializers.CharField(source='user.email',read_only=True)

    class Meta:
        model=UserProfile
        fields=['id','username','email','full_name','birth_place','birth_date','birth_time','birth_longitude','birth_latitide']