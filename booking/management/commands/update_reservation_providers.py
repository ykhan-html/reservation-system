from django.core.management.base import BaseCommand
from booking.models import Reservation, Service


class Command(BaseCommand):
    help = '기존 예약 데이터에 provider 정보를 업데이트합니다.'

    def handle(self, *args, **options):
        self.stdout.write('예약 데이터의 provider 정보를 업데이트하는 중...')

        # provider가 없는 예약들을 찾아서 서비스의 provider로 업데이트
        reservations_without_provider = Reservation.objects.filter(provider__isnull=True)
        
        updated_count = 0
        for reservation in reservations_without_provider:
            if reservation.service and reservation.service.provider:
                reservation.provider = reservation.service.provider
                reservation.save()
                updated_count += 1
                self.stdout.write(f'예약 #{reservation.id} 업데이트: {reservation.service.provider.name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'총 {updated_count}개의 예약이 업데이트되었습니다!')
        ) 