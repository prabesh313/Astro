from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from .serializers import KundaliSerializer, PanchangSerializer
from .models import Kundali, Panchang
from .services import get_kundali, get_panchang,get_planet_positions
from users.models import UserProfile
import datetime

class GenerateKundaliView(APIView):
    permission_classes=[permissions.IsAuthenticated]


    def post(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        # Call external API
        try:
            chart_data = get_kundali(
                birth_date=str(profile.birth_date),
                birth_time=str(profile.birth_time),
                latitude=profile.birth_latitude or 27.7172,
                longitude=profile.birth_longitude or 85.3240,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Save to database
        kundali = Kundali.objects.create(
            user_profile=profile,
            chart_data=chart_data
        )

        return Response({
            "message": "Kundali generated successfully",
            "kundali":KundaliSerializer(kundali).data
        }, status=status.HTTP_201_CREATED)
    

class MyKundaliListView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def get(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        kundalis = Kundali.objects.filter(user_profile=profile).order_by('-generated_at')
        serializer = KundaliSerializer(kundalis, many=True)
        return Response(serializer.data)

class TodayPanchangView(APIView):
    permission_classes=[permissions.AllowAny]
    def get(self, request):
        today = datetime.date.today()

        # Check if we already fetched today's panchang (cache in DB)
        try:
            panchang = Panchang.objects.get(date=today)
            return Response(
                {"cached": True, "panchang": PanchangSerializer(panchang).data}
            )
        except Panchang.DoesNotExist:
            pass


        #otherwise fetch from API and save
        try:
            data = get_panchang(str(today))
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        panchang= Panchang.objects.create(
            date=today,
            data=data
        )

        return Response({
            "cached": False,
            "panchang": PanchangSerializer(panchang).data
        })
    

class PanchangByDateView(APIView):
    permission_classes=[permissions.AllowAny]
    def get(self, request):
        date_str = request.query_params.get("date")
        if not date_str:
            return Response({"error": "Date parameter is required (YYYY-MM-DD)"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            date= datetime.date.fromisoformat(date_str)
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Check cache
        try:
            panchang = Panchang.objects.get(date=date)
            return Response(
                {"cached": True, "panchang": PanchangSerializer(panchang).data}
            )
        except Panchang.DoesNotExist:
            pass

        # Fetch from API
        try:
            panchang=Panchang.objects.get(date=date)
            return Response(PanchangSerializer(panchang).data)
        except Panchang.DoesNotExist:
            pass

        #otherwise fetch from API and save
        try:
            data = get_panchang(str(date))
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        panchang= Panchang.objects.create(
            date=date,
            data=data
        )
        return Response(PanchangSerializer(panchang).data)
    

