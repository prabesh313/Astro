"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,TokenRefreshView
)

from books.views import BookViewSet
from rituals.views import RitualViewSet, MantraViewSet
from users.views import RegisterView, UserProfileView
from astrology.views import CalendarMonthView, CurrentDateView, FestivalListView, GenerateKundaliView, MyKundaliListView, TodayPanchangView,PanchangByDateView

router = DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'rituals', RitualViewSet)
router.register(r'mantras', MantraViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    path('api/users/register/', RegisterView.as_view()),
    path('api/users/login/', TokenObtainPairView.as_view()),
    path('api/users/token/refresh/', TokenRefreshView.as_view()),
    path('api/users/profile/', UserProfileView.as_view()),

    path('api/astrology/kundali/generate/', GenerateKundaliView.as_view()),
    path('api/astrology/kundali/', MyKundaliListView.as_view()),
    path('api/astrology/panchang/today/', TodayPanchangView.as_view()),
    path('api/astrology/panchang/', PanchangByDateView.as_view()),

    path('api/astrology/calendar/month/',CalendarMonthView.as_view()),
    path('api/astrology/festivals/',FestivalListView.as_view()),
    path('api/astrology/current-date/',CurrentDateView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
