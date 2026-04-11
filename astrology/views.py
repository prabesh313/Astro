from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Kundali, Panchang
from .services import get_kundali, get_panchang
from users.models import UserProfile
import datetime

class GenerateKundaliView(APIView):
    def post(self, request):
        profile_id = request.data.get('user_profile_id')
        try:
            profile = UserProfile.objects.get(id=profile_id)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=404)

        # Call external API
        chart_data = get_kundali(
            birth_date=str(profile.birth_date),
            birth_time=str(profile.birth_time),
            latitude=profile.birth_latitude or 27.7172,
            longitude=profile.birth_longitude or 85.3240,
        )

        # Save to database
        kundali = Kundali.objects.create(
            user_profile=profile,
            chart_data=chart_data
        )

        return Response({
            "message": "Kundali generated successfully",
            "kundali_id": kundali.id,
            "data": chart_data
        })

class TodayPanchangView(APIView):
    def get(self, request):
        today = datetime.date.today()

        # Check if we already fetched today's panchang (cache in DB)
        panchang, created = Panchang.objects.get_or_create(
            date=today,
            defaults={"data": get_panchang(today)}
        )
        return Response(panchang.data)


