from django.core.management.base import BaseCommand
from astrology.models import BSCalendarData, Festival
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Load calendar data and festivals into database'

    def handle(self, *args, **options):
        self.load_calendar_data()
        self.load_festivals()
        self.stdout.write(self.style.SUCCESS('Successfully loaded calendar data and festivals.'))

    def load_calendar_data(self):
        calendar_data=[
            # 2082
            (2082, 1, 31, 1, date(2025, 4, 14)),
            (2082, 2, 32, 5, date(2025, 5, 15)),
            (2082, 3, 31, 0, date(2025, 6, 16)),
            (2082, 4, 32, 3, date(2025, 7, 17)),
            (2082, 5, 31, 6, date(2025, 8, 18)),
            (2082, 6, 30, 1, date(2025, 9, 18)),
            (2082, 7, 30, 4, date(2025, 10, 18)),
            (2082, 8, 30, 0, date(2025, 11, 17)),
            (2082, 9, 29, 2, date(2025, 12, 17)),
            (2082, 10, 30, 5, date(2026, 1, 15)),
            (2082, 11, 29, 0, date(2026, 2, 14)),
            (2082, 12, 31, 3, date(2026, 3, 16)),
            
            # 2081
            (2081, 1, 31, 0, date(2024, 4, 13)),
            (2081, 2, 31, 3, date(2024, 5, 14)),
            (2081, 3, 32, 5, date(2024, 6, 14)),
            (2081, 4, 31, 1, date(2024, 7, 16)),
            (2081, 5, 31, 4, date(2024, 8, 16)),
            (2081, 6, 31, 0, date(2024, 9, 16)),
            (2081, 7, 30, 2, date(2024, 10, 17)),
            (2081, 8, 29, 5, date(2024, 11, 16)),
            (2081, 9, 30, 0, date(2024, 12, 16)),
            (2081, 10, 29, 3, date(2025, 1, 15)),
            (2081, 11, 30, 5, date(2025, 2, 14)),
            (2081, 12, 31, 1, date(2025, 3, 16)),
            
            # 2083
            (2083, 1, 31, 4, date(2026, 4, 14)),
            (2083, 2, 32, 0, date(2026, 5, 15)),
            (2083, 3, 32, 2, date(2026, 6, 16)),
            (2083, 4, 31, 5, date(2026, 7, 18)),
            (2083, 5, 31, 1, date(2026, 8, 18)),
            (2083, 6, 30, 3, date(2026, 9, 18)),
            (2083, 7, 30, 6, date(2026, 10, 18)),
            (2083, 8, 29, 2, date(2026, 11, 17)),
            (2083, 9, 30, 4, date(2026, 12, 17)),
            (2083, 10, 29, 0, date(2027, 1, 16)),
            (2083, 11, 30, 2, date(2027, 2, 15)),
            (2083, 12, 31, 4, date(2027, 3, 17)),

        ]

        for bs_year, bs_month, num_days, start_day, ad_start in calendar_data:
            BSCalendarData.objects.update_or_create(
                bs_year=bs_year,
                bs_month=bs_month,
                defaults={
                    'num_days': num_days,
                    'start_day_of_week':start_day,
                    'ad_month_start': ad_start,
                }
            )

        self.stdout.write(self.style.SUCCESS(f'Loaded {len(calendar_data)} calendar months'))

    def load_festivals(self):
            festivals=[
#dample data for testing, not accurate
(2083, '2083-1-1', date(2026, 4, 14), 'Nepali New Year', 'नयाँ वर्ष', 'नयाँ वर्षको पहिलो दिन', 'festival'),
(2083, '2083-1-8', date(2026, 4, 21), 'Shivaratri', 'शिवरात्रि', 'भगवान शिवको पूजनको दिन', 'religious'),
(2083, '2083-1-15', date(2026, 4, 28), 'Purnima', 'पूर्णिमा', 'पूर्ण चन्द्रमा', 'religious'),

(2083, '2083-2-15', date(2026, 5, 30), 'Akha Teej', 'आखा तीज', 'महिलाको पर्व', 'festival'),

(2083, '2083-3-15', date(2026, 7, 1), 'Buddha Jayanti', 'बुद्ध जयन्ती', 'गौतम बुद्धको जन्मको दिन', 'religious'),

(2083, '2083-5-14', date(2026, 9, 1), 'Gayatri Jayanti', 'गायत्री जयन्ती', 'गायत्री माताको पूजा', 'religious'),

(2083, '2083-7-15', date(2026, 11, 2), 'Janmashtami', 'जन्माष्टमी', 'कृष्णको जन्मको दिन', 'religious'),

(2083, '2083-8-1', date(2026, 11, 18), 'Ghatasthapana', 'घट स्थापना', 'दशैंको शुरुवात', 'festival'),

(2083, '2083-9-15', date(2026, 12, 31), 'Vijayadashami', 'विजयादशमी', 'बिजयाको पर्व', 'festival'),

(2083, '2083-10-1', date(2027, 1, 16), 'Tihar', 'तिहार', 'दिपावलीको मौसम', 'festival'),

(2083, '2083-10-15', date(2027, 1, 30), 'Bhai Tika', 'भाईटीका', 'भाई-बहिनीको पर्व', 'festival'),
            ]

            for bs_year, bs_date , ad_date , name_en , name_np, significance, category in festivals:
                Festival.objects.update_or_create(
                    bs_date=bs_date,
                    ad_date=ad_date,
                    defaults={
                        'name_english': name_en,
                        'name_nepali': name_np,
                        'significance': significance,
                        'category': category,
                        'year': bs_year,
                    }
                )
            self.stdout.write(f'Loaded {len(festivals)} festivals')