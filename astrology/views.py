from calendar import month

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from django.utils import timezone
from .serializers import BSCalendarDataSerializer, FestivalSerializer, KundaliSerializer, PanchangSerializer
from .models import BSCalendarData, Festival, Kundali, Panchang
from .services import get_kundali, get_panchang,get_planet_positions
from users.models import UserProfile
import datetime


def get_or_fetch_panchang_for_date(target_date):
    try:
        panchang = Panchang.objects.get(date=target_date)
        return panchang, True
    except Panchang.DoesNotExist:
        data = get_panchang(str(target_date))
        panchang = Panchang.objects.create(date=target_date, data=data)
        return panchang, False

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
        today = timezone.localdate()
        try:
            panchang, cached = get_or_fetch_panchang_for_date(today)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response({
            "cached": cached,
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

        try:
            panchang, cached = get_or_fetch_panchang_for_date(date)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response({
            "cached": cached,
            "panchang": PanchangSerializer(panchang).data
        })

class CalendarMonthView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        bs_year = request.query_params.get('bs_year')
        bs_month = request.query_params.get('bs_month')

        if not bs_year or not bs_month:
            return Response(
                {"error": "Please provide ?bs_year=YYYY&bs_month=M"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            bs_year = int(bs_year)
            bs_month = int(bs_month)
        except ValueError:
            return Response(
                {"error": "Year and month must be integers"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get calendar data
        try:
            cal_data = BSCalendarData.objects.get(
                bs_year=bs_year,
                bs_month=bs_month
            )
        except BSCalendarData.DoesNotExist:
            return Response(
                {"error": f"Calendar data not found for BS {bs_year}-{bs_month}"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get festivals for this month
        festivals = Festival.objects.filter(
            bs_date__startswith=f"{bs_year}-{bs_month:02d}-"
        )

        # Get all panchangs for this month (start to end date)
        start_date = cal_data.ad_month_start
        end_date = start_date + datetime.timedelta(
            days=cal_data.num_days
        )
        panchangs = Panchang.objects.filter(
            date__gte=start_date,
            date__lt=end_date
        )

        return Response({
            "calendar": BSCalendarDataSerializer(cal_data).data,
            "festivals": FestivalSerializer(festivals, many=True).data,
            "panchangs": PanchangSerializer(panchangs, many=True).data,
            "meta": {
                "month_name": self._get_bs_month_name(bs_month),
                "num_days": cal_data.num_days,
                "today": str(datetime.date.today()),
            }
        })

    def _get_bs_month_name(self, month):
        months = [
            'बैशाख', 'जेठ', 'असार', 'श्रावण', 'भाद्र', 'आश्विन',
            'कार्तिक', 'मंसिर', 'पौष', 'माघ', 'फाल्गुन', 'चैत्र'
        ]
        return months[month - 1] if 1 <= month <= 12 else 'Unknown'

class FestivalListView(APIView):
    """
    GET /api/astrology/festivals/
    GET /api/astrology/festivals/?month=1&year=2082
    List festivals, optionally filtered by month/year
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        bs_year = request.query_params.get('bs_year')
        bs_month = request.query_params.get('bs_month')

        queryset = Festival.objects.all()

        if bs_year:
            queryset = queryset.filter(year=int(bs_year))

        if bs_month:
            queryset = queryset.filter(
                bs_date__startswith=f"{bs_year}-{int(bs_month):02d}-"
            )

        festivals = queryset.order_by('ad_date')
        return Response(FestivalSerializer(festivals, many=True).data)

class CurrentDateView(APIView):
    """
    GET /api/astrology/current-date/
    Returns today's date in both AD and BS formats
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        today_ad = timezone.localdate()
        bs_year = bs_month = bs_day = None

        try:
            panchang, _ = get_or_fetch_panchang_for_date(today_ad)
        except Exception:
            panchang = None

        # Try to find matching BS date from calendar data
        # (This is a simplification — in production you'd use a proper conversion)
        try:
            cal = BSCalendarData.objects.filter(
                ad_month_start__lte=today_ad
            ).order_by('-ad_month_start').first()

            if cal:
                days_diff = (today_ad - cal.ad_month_start).days
                bs_day = days_diff + 1
                bs_month = cal.bs_month
                bs_year = cal.bs_year

                # Handle month overflow
                if bs_day > cal.num_days:
                    bs_day = 1
                    bs_month += 1
                    if bs_month > 12:
                        bs_month = 1
                        bs_year += 1
        except Exception as e:
            bs_year = bs_month = bs_day = None

        return Response({
            "today_ad": str(today_ad),
            "today_bs": ({
                "year": bs_year,
                "month": bs_month,
                "day": bs_day,
            } if bs_year else None),
            "panchang": PanchangSerializer(panchang).data if panchang else None,
        })