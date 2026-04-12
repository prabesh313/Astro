from rest_framework import serializers
from .models import Kundali, Panchang

class KundaliSerializer(serializers.ModelSerializer):
    user_name=serializers.CharField(source='user_profile.full_name', read_only=True )

    class Meta:
        model=Kundali
        fields=['id','user_name','chart_data','generated_at']


class PanchangSerializer(serializers.ModelSerializer):
    class Meta:
        model=Panchang
        fields=['id','date','data','fetched_at']