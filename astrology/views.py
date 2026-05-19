from calendar import month

from django.shortcuts import render
from rest_framework.generics import ListAPIView
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from django.utils import timezone
from .serializers import BSCalendarDataSerializer, FestivalSerializer, KundaliSerializer, PanchangSerializer,HoroscopeSerializer
from .models import BSCalendarData, Festival, Kundali, Panchang,Horoscope
from .services import get_kundali, get_panchang,get_planet_positions,get_daily_horoscope
from users.models import UserProfile
import datetime
from datetime import date



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
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        today_ad = timezone.localdate()
        bs_year = bs_month = bs_day = None

        try:
            panchang, _ = get_or_fetch_panchang_for_date(today_ad)
        except Exception:
            panchang = None

        # Try to find matching BS date from calendar data
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
    

class DailyHoroscopeView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        rashi = request.query_params.get('rashi','').lower()
        if not rashi:
            return Response({"error": "Please provide ?rashi=aries(or other rashi)"}, status=status.HTTP_400_BAD_REQUEST)
        
        valid_rashis = ['aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces']

        if rashi not in valid_rashis:
            return Response({"error": f"Invalid rashi. Must be one of: {', '.join(valid_rashis)}"}, status=status.HTTP_400_BAD_REQUEST)
        
        today=date.today()

        #check if we alreay have today's horoscope cached
        try:
            horoscope=Horoscope.objects.get(rashi=rashi, date=today,horoscope_type='daily')
            return Response(
                {
                    "cached": True,
                    "horoscope": HoroscopeSerializer(horoscope).data
                }
            )
        except Horoscope.DoesNotExist:
            pass

        #fetch from external API
        try:
            horoscope_data = get_daily_horoscope(rashi)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        #save to database
        horoscope = Horoscope.objects.create(
            rashi=rashi,
            date=today,
            horoscope_type='daily',
            prediction=horoscope_data.get('prediction', ''),
            love_score=horoscope_data.get('love_score', 3),
            career_score=horoscope_data.get('career_score', 3),
            health_score=horoscope_data.get('health_score', 3),
            money_score=horoscope_data.get('money_score', 3),
            lucky_color=horoscope_data.get('lucky_color', ''),
            lucky_number=horoscope_data.get('lucky_number', ''),
            lucky_time=horoscope_data.get('lucky_time', ''),
            advice=horoscope_data.get('advice', ''),
            api_response=horoscope_data.get('raw_response'),
            
        )

        return Response(
            {
                "cached": False,
                "horoscope": HoroscopeSerializer(horoscope).data
            }
        )

#filters queryset and returns horoscope list with filtering by rashi and type
class HoroscopeListView(ListAPIView):
    serializer_class = HoroscopeSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Horoscope.objects.all()
        
        rashi = self.request.query_params.get('rashi')
        if rashi:
            queryset = queryset.filter(rashi=rashi.lower())
        
        horoscope_type = self.request.query_params.get('type')
        if horoscope_type:
            queryset = queryset.filter(horoscope_type=horoscope_type)
        
        return queryset.order_by('-date')

    



class AllRashisHoroscopeView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        rashis = [
            'aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo',
            'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces'
        ]
        
        horoscope_type = request.query_params.get('type', 'daily')
        today = date.today()
        
        results = []
        for rashi in rashis:
            try:
                #try to get from database first
                horoscope = Horoscope.objects.get(
                    rashi=rashi,
                    date=today,
                    horoscope_type=horoscope_type
                )
                results.append(HoroscopeSerializer(horoscope).data)
            except Horoscope.DoesNotExist:
                #try to fetch from API
                try:
                    horoscope_data = get_daily_horoscope(rashi)
                    horoscope = Horoscope.objects.create(
                        rashi=rashi,
                        horoscope_type=horoscope_type,
                        date=today,
                        prediction=horoscope_data.get('prediction', ''),
                        love_score=horoscope_data.get('love_score', 3),
                        career_score=horoscope_data.get('career_score', 3),
                        health_score=horoscope_data.get('health_score', 3),
                        money_score=horoscope_data.get('money_score', 3),
                        lucky_color=horoscope_data.get('lucky_color', ''),
                        lucky_number=horoscope_data.get('lucky_number', ''),
                        lucky_time=horoscope_data.get('lucky_time', ''),
                        advice=horoscope_data.get('advice', ''),
                        api_response=horoscope_data.get('raw_response'),
                    )
                    results.append(HoroscopeSerializer(horoscope).data)
                except Exception as e:
                    print(f"Failed to get horoscope for {rashi}: {str(e)}")
        
        return Response({
            "date": str(today),
            "type": horoscope_type,
            "horoscopes": results
        })