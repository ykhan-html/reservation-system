from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from booking.models import Service, BusinessHours, Category, ServiceProvider
from datetime import time


class Command(BaseCommand):
    help = '초기 데이터를 로드합니다.'

    def handle(self, *args, **options):
        self.stdout.write('초기 데이터를 로드하는 중...')

        # 카테고리 데이터 생성 (골프 레슨)
        categories_data = [
            {
                'name': '기초 레슨',
                'description': '골프 초보자를 위한 기초 레슨',
                'is_active': True,
            },
            {
                'name': '중급 레슨',
                'description': '기본기를 다진 골퍼를 위한 중급 레슨',
                'is_active': True,
            },
            {
                'name': '고급 레슨',
                'description': '스코어 향상을 위한 고급 레슨',
                'is_active': True,
            },
            {
                'name': '특수 레슨',
                'description': '특정 상황별 맞춤형 레슨',
                'is_active': True,
            },
        ]

        categories = {}
        for category_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=category_data['name'],
                defaults=category_data
            )
            categories[category.name] = category
            if created:
                self.stdout.write(f'카테고리 생성: {category.name}')
            else:
                self.stdout.write(f'카테고리 이미 존재: {category.name}')

        # 서비스 제공자 데이터 생성 (골프 프로)
        providers_data = [
            {
                'name': '김태호',
                'description': '15년 경력의 PGA 프로',
                'phone': '010-1234-5678',
                'email': 'kim@example.com',
                'specialties': '기초 스윙, 아이언 플레이',
                'experience_years': 15,
                'is_active': True,
                'username': 'kimtaeho',
                'password': 'password123',
            },
            {
                'name': '이준호',
                'description': '10년 경력의 골프 프로',
                'phone': '010-2345-6789',
                'email': 'lee@example.com',
                'specialties': '드라이버, 퍼팅',
                'experience_years': 10,
                'is_active': True,
                'username': 'leejunho',
                'password': 'password123',
            },
            {
                'name': '박성민',
                'description': '8년 경력의 골프 프로',
                'phone': '010-3456-7890',
                'email': 'park@example.com',
                'specialties': '숏게임, 벙커 플레이',
                'experience_years': 8,
                'is_active': True,
                'username': 'parksungmin',
                'password': 'password123',
            },
            {
                'name': '최영수',
                'description': '12년 경력의 골프 프로',
                'phone': '010-4567-8901',
                'email': 'choi@example.com',
                'specialties': '고급 레슨, 경기 전략',
                'experience_years': 12,
                'is_active': True,
                'username': 'choiyoungsu',
                'password': 'password123',
            },
        ]

        providers = {}
        for provider_data in providers_data:
            # 비밀번호 해싱
            from django.contrib.auth.hashers import make_password
            provider_data['password'] = make_password(provider_data['password'])
            
            provider, created = ServiceProvider.objects.get_or_create(
                name=provider_data['name'],
                defaults=provider_data
            )
            providers[provider.name] = provider
            if created:
                self.stdout.write(f'서비스 제공자 생성: {provider.name}')
            else:
                self.stdout.write(f'서비스 제공자 이미 존재: {provider.name}')

        # 서비스 데이터 생성 (골프 레슨)
        services_data = [
            {
                'name': '기초 스윙 레슨',
                'description': '골프를 처음 시작하는 분을 위한 기초 스윙 레슨입니다. 올바른 자세와 기본 동작을 배웁니다.',
                'price': 50000,
                'duration': 60,
                'category': categories['기초 레슨'],
                'provider': providers['김태호'],
                'stock_quantity': 10,
                'is_featured': True,
            },
            {
                'name': '아이언 레슨',
                'description': '아이언 클럽을 활용한 정확한 샷 레슨입니다. 거리감과 방향성을 향상시킵니다.',
                'price': 60000,
                'duration': 60,
                'category': categories['중급 레슨'],
                'provider': providers['김태호'],
                'stock_quantity': 8,
                'is_featured': True,
            },
            {
                'name': '드라이버 레슨',
                'description': '드라이버를 활용한 파워 샷 레슨입니다. 거리와 정확성을 동시에 향상시킵니다.',
                'price': 70000,
                'duration': 60,
                'category': categories['중급 레슨'],
                'provider': providers['이준호'],
                'stock_quantity': 6,
                'is_featured': True,
            },
            {
                'name': '퍼팅 레슨',
                'description': '퍼팅의 정확성을 향상시키는 레슨입니다. 그린에서의 승부를 좌우하는 중요한 기술을 배웁니다.',
                'price': 40000,
                'duration': 45,
                'category': categories['중급 레슨'],
                'provider': providers['이준호'],
                'stock_quantity': 8,
                'is_featured': False,
            },
            {
                'name': '숏게임 레슨',
                'description': '그린 주변에서의 숏게임 레슨입니다. 칩샷과 피치샷의 정확성을 향상시킵니다.',
                'price': 55000,
                'duration': 60,
                'category': categories['고급 레슨'],
                'provider': providers['박성민'],
                'stock_quantity': 5,
                'is_featured': False,
            },
            {
                'name': '벙커 플레이 레슨',
                'description': '벙커에서의 탈출 기술을 배우는 레슨입니다. 어려운 상황에서도 안정적인 플레이가 가능합니다.',
                'price': 45000,
                'duration': 45,
                'category': categories['고급 레슨'],
                'provider': providers['박성민'],
                'stock_quantity': 4,
                'is_featured': False,
            },
            {
                'name': '경기 전략 레슨',
                'description': '실제 경기에서 활용할 수 있는 전략적 사고와 코스 관리법을 배우는 레슨입니다.',
                'price': 80000,
                'duration': 90,
                'category': categories['특수 레슨'],
                'provider': providers['최영수'],
                'stock_quantity': 3,
                'is_featured': True,
            },
            {
                'name': '심리 관리 레슨',
                'description': '골프 경기에서 중요한 심리적 요소를 다루는 레슨입니다. 압박 상황에서도 안정적인 플레이가 가능합니다.',
                'price': 60000,
                'duration': 60,
                'category': categories['특수 레슨'],
                'provider': providers['최영수'],
                'stock_quantity': 4,
                'is_featured': False,
            },
        ]

        for service_data in services_data:
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults=service_data
            )
            if created:
                self.stdout.write(f'서비스 생성: {service.name}')
            else:
                self.stdout.write(f'서비스 이미 존재: {service.name}')

        # 영업시간 데이터 생성 (골프 레슨)
        business_hours_data = [
            {'day': 0, 'open_time': time(7, 0), 'close_time': time(19, 0), 'is_closed': False},  # 월요일
            {'day': 1, 'open_time': time(7, 0), 'close_time': time(19, 0), 'is_closed': False},  # 화요일
            {'day': 2, 'open_time': time(7, 0), 'close_time': time(19, 0), 'is_closed': False},  # 수요일
            {'day': 3, 'open_time': time(7, 0), 'close_time': time(19, 0), 'is_closed': False},  # 목요일
            {'day': 4, 'open_time': time(7, 0), 'close_time': time(19, 0), 'is_closed': False},  # 금요일
            {'day': 5, 'open_time': time(6, 0), 'close_time': time(20, 0), 'is_closed': False},  # 토요일
            {'day': 6, 'open_time': time(6, 0), 'close_time': time(18, 0), 'is_closed': False},  # 일요일
        ]

        for hours_data in business_hours_data:
            hours, created = BusinessHours.objects.get_or_create(
                day=hours_data['day'],
                defaults=hours_data
            )
            if created:
                self.stdout.write(f'영업시간 생성: {hours.get_day_display()}')
            else:
                self.stdout.write(f'영업시간 이미 존재: {hours.get_day_display()}')

        self.stdout.write(
            self.style.SUCCESS('초기 데이터 로드가 완료되었습니다!')
        ) 