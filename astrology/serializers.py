from rest_framework import serializers
from .models import BSCalenderData, Festival, Kundali, Panchang

class KundaliSerializer(serializers.ModelSerializer):
    user_name=serializers.CharField(source='user_profile.full_name', read_only=True )

    class Meta:
        model=Kundali
        fields=['id','user_name','chart_data','generated_at']


class PanchangSerializer(serializers.ModelSerializer):
    class Meta:
        model=Panchang
        fields=['id','date','data','fetched_at']

class FestivalSerializer(serializers.ModelSerializer):
    class Meta:
        model=Festival
        fields=['id','bs_date','ad_date','name_english','name_nepali','description','significance','category','year']

class BSCalenderDataSerializer(serializers.ModelSerializer):
    class Meta:
        model=BSCalenderData
        fields=['id','bs_year','bs_month','num_days','start_day_of_week','ad_month_start']

#this helps to get festivals and panchangs for a given month and year in the BS calendar, which can be used to display in the frontend calendar view.
class CalenderMonthSerializer(serializers.Serializer):
    bs_year=serializers.IntegerField()
    bs_month=serializers.IntegerField()
    num_days=serializers.IntegerField()
    start_day_of_week=serializers.IntegerField()
    ad_month_start=serializers.DateField()
    festivals=FestivalSerializer(many=True, read_only=True)
    panchangs=PanchangSerializer(many=True, read_only=True)