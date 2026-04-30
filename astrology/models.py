from django.db import models
from users.models import UserProfile

# Create your models here.
class Kundali(models.Model):
    user_profile= models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    chart_data= models.JSONField()
    generated_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Kundali of {self.user_profile.full_name}"
    

class Panchang(models.Model):
    date=models.DateField(unique=True)
    data= models.JSONField()
    fetched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Panchang for {self.date}"

class Festival(models.Model):
    bs_date=models.CharField(max_length=20)
    ad_date=models.DateField()
    name_english=models.CharField(max_length=200)
    name_nepali=models.CharField(max_length=200)
    description=models.TextField(blank=True)
    significance= models.TextField(blank=True)
    category = models.CharField(
        max_length=50,
        choices=[
            ('festival','Festival'),
            ('religious','Religious'),
            ('national','National'),
            ('seasonal','Seasonal'),
        ],
        default='festival'
    )
    year = models.IntegerField()

    class Meta:
        unique_together = ('bs_date', 'ad_date')
        ordering=['bs_date']
        indexes=[
            models.Index(fields=['ad_date']),
            models.Index(fields=['bs_date']),
        ]

    def __str__(self):
        return f"{self.name_nepali} ({self.bs_date})"

class BSCalendarData(models.Model):
    bs_year=models.IntegerField()
    bs_month=models.IntegerField()
    num_days=models.IntegerField()
    start_day_of_week=models.IntegerField()
    ad_month_start=models.DateField()

    class Meta:
        unique_together = ('bs_year', 'bs_month')
        ordering=['bs_year','bs_month']
        indexes=[
            models.Index(fields=['bs_year', 'bs_month']),
            
        ]
    def __str__(self):
        return f"BS Year: {self.bs_year}--{self.bs_month}"
    

class Horoscope(models.Model):
    RASHI_CHOICES = [
        ('aries', 'मेष'),
        ('taurus', 'वृषभ'),
        ('gemini', 'मिथुन'),
        ('cancer', 'कर्क'),
        ('leo', 'सिंह'),
        ('virgo', 'कन्या'),
        ('libra', 'तुला'),
        ('scorpio', 'वृश्चिक'),
        ('sagittarius', 'धनु'),
        ('capricorn', 'मकर'),
        ('aquarius', 'कुम्भ'),
        ('pisces', 'मीन'),
    ]

    HOROSCOPE_TYPE_CHOICES = [
        ('daily', 'Daily'),

    ]

    rashi = models.CharField(max_length=20, choices=RASHI_CHOICES)
    horoscope_type = models.CharField(max_length=20, choices=HOROSCOPE_TYPE_CHOICES, default='daily')

    date=models.DateField()
    prediction=models.TextField()

    love_score=models.IntegerField(default=3)
    career_score=models.IntegerField(default=3)
    health_score=models.IntegerField(default=3)
    money_score=models.IntegerField(default=3)

    lucky_color=models.CharField(max_length=50, blank=True)
    lucky_number=models.IntegerField(null=True, blank=True)
    lucky_time=models.CharField(max_length=50, blank=True)

    advice=models.TextField(blank=True)
    api_response=models.JSONField(blank=True, null=True)

    fetched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('rashi', 'horoscope_type', 'date')
        ordering=['-date', 'rashi']
        indexes=[
            models.Index(fields=['rashi', 'date']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.get_rashi_display()} - {self.date} ({self.horoscope_type})"

