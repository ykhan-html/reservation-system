from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Category(models.Model):
    """상품 카테고리 모델"""
    name = models.CharField(max_length=100, verbose_name="카테고리명")
    description = models.TextField(blank=True, null=True, verbose_name="카테고리 설명")
    is_active = models.BooleanField(default=True, verbose_name="활성화 여부")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        verbose_name = "카테고리"
        verbose_name_plural = "카테고리들"
        ordering = ['name']

    def __str__(self):
        return self.name


class ServiceProvider(models.Model):
    """서비스 제공자 모델"""
    name = models.CharField(max_length=100, verbose_name="제공자명")
    description = models.TextField(blank=True, null=True, verbose_name="제공자 설명")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="연락처")
    email = models.EmailField(blank=True, null=True, verbose_name="이메일")
    image = models.ImageField(upload_to='providers/', blank=True, null=True, verbose_name="제공자 이미지")
    is_active = models.BooleanField(default=True, verbose_name="활성화 여부")
    specialties = models.TextField(blank=True, null=True, verbose_name="전문 분야")
    experience_years = models.PositiveIntegerField(default=0, verbose_name="경력 연차")
    # 로그인 정보 추가
    username = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="로그인 아이디")
    password = models.CharField(max_length=128, null=True, blank=True, verbose_name="비밀번호")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        verbose_name = "서비스 제공자"
        verbose_name_plural = "서비스 제공자들"
        ordering = ['name']

    def __str__(self):
        return self.name


class Service(models.Model):
    """서비스 모델"""
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="카테고리")
    provider = models.ForeignKey(ServiceProvider, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="서비스 제공자")
    name = models.CharField(max_length=100, verbose_name="서비스명")
    description = models.TextField(verbose_name="서비스 설명")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="가격")
    duration = models.IntegerField(verbose_name="소요시간(분)")
    image = models.ImageField(upload_to='services/', blank=True, null=True, verbose_name="서비스 이미지")
    is_active = models.BooleanField(default=True, verbose_name="활성화 여부")
    is_featured = models.BooleanField(default=False, verbose_name="추천 서비스")
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="재고 수량")
    min_advance_booking = models.PositiveIntegerField(default=0, verbose_name="최소 예약 가능 시간(시간)")
    max_advance_booking = models.PositiveIntegerField(default=30, verbose_name="최대 예약 가능 시간(일)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        verbose_name = "서비스"
        verbose_name_plural = "서비스들"
        ordering = ['-is_featured', 'name']

    def __str__(self):
        return self.name

    @property
    def is_available(self):
        """서비스 이용 가능 여부"""
        return self.is_active and self.stock_quantity > 0


class Reservation(models.Model):
    """예약 모델"""
    STATUS_CHOICES = [
        ('pending', '대기중'),
        ('confirmed', '확정'),
        ('completed', '완료'),
        ('cancelled', '취소'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="사용자")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="서비스")
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, null=True, blank=True, verbose_name="서비스 제공자")
    date = models.DateField(verbose_name="예약 날짜")
    time = models.TimeField(verbose_name="예약 시간")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="상태")
    notes = models.TextField(blank=True, null=True, verbose_name="특이사항")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="예약일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        verbose_name = "예약"
        verbose_name_plural = "예약들"
        ordering = ['-date', '-time']

    def __str__(self):
        return f"{self.user.username} - {self.service.name} ({self.date})"

    @property
    def datetime(self):
        """예약 날짜와 시간을 결합"""
        return timezone.make_aware(
            timezone.datetime.combine(self.date, self.time)
        )


class Review(models.Model):
    """리뷰 모델"""
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, verbose_name="예약")
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="평점"
    )
    comment = models.TextField(verbose_name="리뷰 내용")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")

    class Meta:
        verbose_name = "리뷰"
        verbose_name_plural = "리뷰들"

    def __str__(self):
        return f"{self.reservation.user.username}의 리뷰 - {self.rating}점"


class BusinessHours(models.Model):
    """영업시간 모델"""
    DAY_CHOICES = [
        (0, '월요일'),
        (1, '화요일'),
        (2, '수요일'),
        (3, '목요일'),
        (4, '금요일'),
        (5, '토요일'),
        (6, '일요일'),
    ]

    day = models.IntegerField(choices=DAY_CHOICES, verbose_name="요일")
    open_time = models.TimeField(verbose_name="오픈 시간")
    close_time = models.TimeField(verbose_name="마감 시간")
    is_closed = models.BooleanField(default=False, verbose_name="휴무일")

    class Meta:
        verbose_name = "영업시간"
        verbose_name_plural = "영업시간"
        ordering = ['day']

    def __str__(self):
        if self.is_closed:
            return f"{self.get_day_display()} - 휴무"
        return f"{self.get_day_display()} - {self.open_time} ~ {self.close_time}"
