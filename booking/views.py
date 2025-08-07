from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Service, Reservation, Review, BusinessHours, Category, ServiceProvider
from .serializers import (
    ServiceSerializer, ReservationSerializer, ReviewSerializer,
    BusinessHoursSerializer, UserSerializer, ReservationCreateSerializer,
    UserRegistrationSerializer, CategorySerializer, ServiceProviderSerializer,
    ServiceProviderLoginSerializer, ServiceProviderReservationSerializer
)


def index(request):
    """메인 페이지"""
    return render(request, 'booking/index.html')


def register_page(request):
    """회원가입 페이지"""
    return render(request, 'booking/register.html')


def login_page(request):
    """로그인 페이지"""
    return render(request, 'booking/login.html')


def profile_page(request):
    """회원관리 페이지"""
    return render(request, 'booking/profile.html')


def product_management_page(request):
    """상품관리 페이지"""
    if not request.user.is_staff:
        return render(request, 'booking/403.html')
    return render(request, 'booking/product_management.html')


def provider_management_page(request):
    """서비스 제공자 관리 페이지"""
    if not request.user.is_staff:
        return render(request, 'booking/403.html')
    return render(request, 'booking/provider_management.html')


def provider_login_page(request):
    """서비스 제공자 로그인 페이지"""
    return render(request, 'booking/provider_login.html')


def provider_dashboard_page(request):
    """서비스 제공자 대시보드 페이지"""
    return render(request, 'booking/provider_dashboard.html')


class RegisterView(APIView):
    """회원가입 API"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': '회원가입이 완료되었습니다.',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """로그인 API"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'error': '사용자명과 비밀번호를 입력해주세요.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return Response({
                'message': '로그인이 완료되었습니다.',
                'user': UserSerializer(user).data
            })
        else:
            return Response({
                'error': '사용자명 또는 비밀번호가 올바르지 않습니다.'
            }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """로그아웃 API"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        logout(request)
        return Response({'message': '로그아웃되었습니다.'})


class ProfileUpdateView(APIView):
    """프로필 수정 API"""
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request):
        user = request.user
        data = request.data.copy()
        
        # 비밀번호 변경이 있는 경우
        if 'password' in data and data['password']:
            if 'password2' not in data or data['password'] != data['password2']:
                return Response({
                    'error': '비밀번호가 일치하지 않습니다.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 비밀번호 검증
            from django.contrib.auth.password_validation import validate_password
            try:
                validate_password(data['password'])
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(data['password'])
        
        # 다른 필드들 업데이트
        if 'full_name' in data:
            user.first_name = data['full_name']
        if 'email' in data:
            user.email = data['email']
        
        user.save()
        
        return Response({
            'message': '프로필이 업데이트되었습니다.',
            'user': UserSerializer(user).data
        })


class CategoryViewSet(viewsets.ModelViewSet):
    """카테고리 관리 API"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """관리자만 수정 가능"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]


class ServiceProviderViewSet(viewsets.ModelViewSet):
    """서비스 제공자 관리 API"""
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """권한에 따른 쿼리셋"""
        if self.request.user.is_staff:
            return ServiceProvider.objects.all()
        return ServiceProvider.objects.filter(is_active=True)

    def get_permissions(self):
        """관리자만 수정 가능"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    @action(detail=False, methods=['get'])
    def active(self, request):
        """활성화된 서비스 제공자 조회"""
        providers = ServiceProvider.objects.filter(is_active=True)
        serializer = self.get_serializer(providers, many=True)
        return Response(serializer.data)


class ServiceProviderLoginView(APIView):
    """서비스 제공자 로그인 API"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ServiceProviderLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            try:
                provider = ServiceProvider.objects.get(username=username, is_active=True)
                from django.contrib.auth.hashers import check_password
                if check_password(password, provider.password):
                    # 세션에 제공자 정보 저장
                    request.session['provider_id'] = provider.id
                    request.session['provider_name'] = provider.name
                    return Response({
                        'message': '로그인 성공',
                        'provider': {
                            'id': provider.id,
                            'name': provider.name,
                            'username': provider.username
                        }
                    })
                else:
                    return Response({'error': '비밀번호가 올바르지 않습니다.'}, status=400)
            except ServiceProvider.DoesNotExist:
                return Response({'error': '존재하지 않는 사용자입니다.'}, status=400)
        return Response(serializer.errors, status=400)


class ServiceProviderLogoutView(APIView):
    """서비스 제공자 로그아웃 API"""
    def post(self, request):
        if 'provider_id' in request.session:
            del request.session['provider_id']
            del request.session['provider_name']
        return Response({'message': '로그아웃 성공'})


class ServiceProviderReservationViewSet(viewsets.ReadOnlyModelViewSet):
    """서비스 제공자용 예약 관리 API"""
    serializer_class = ServiceProviderReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """로그인한 제공자의 예약만 조회"""
        provider_id = self.request.session.get('provider_id')
        if not provider_id:
            return Reservation.objects.none()
        return Reservation.objects.filter(provider_id=provider_id)

    def get_permissions(self):
        """세션 기반 인증"""
        return [permissions.AllowAny()]

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """예약 상태 업데이트"""
        provider_id = request.session.get('provider_id')
        if not provider_id:
            return Response({'error': '로그인이 필요합니다.'}, status=401)
        
        try:
            reservation = Reservation.objects.get(id=pk, provider_id=provider_id)
            new_status = request.data.get('status')
            if new_status in ['pending', 'confirmed', 'completed', 'cancelled']:
                reservation.status = new_status
                reservation.save()
                serializer = self.get_serializer(reservation)
                return Response(serializer.data)
            else:
                return Response({'error': '유효하지 않은 상태입니다.'}, status=400)
        except Reservation.DoesNotExist:
            return Response({'error': '예약을 찾을 수 없습니다.'}, status=404)


class ServiceViewSet(viewsets.ModelViewSet):
    """서비스 관리 API"""
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """권한에 따른 쿼리셋"""
        if self.request.user.is_staff:
            return Service.objects.all()
        return Service.objects.filter(is_active=True)

    def get_permissions(self):
        """관리자만 수정 가능"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    @action(detail=True, methods=['get'])
    def available_times(self, request, pk=None):
        """특정 서비스의 예약 가능한 시간 조회"""
        service = self.get_object()
        date_str = request.query_params.get('date')
        
        if not date_str:
            return Response(
                {"error": "date 파라미터가 필요합니다."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "올바른 날짜 형식이 아닙니다. (YYYY-MM-DD)"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 영업시간 확인
        weekday = target_date.weekday()
        business_hours = BusinessHours.objects.filter(day=weekday).first()
        
        if not business_hours or business_hours.is_closed:
            return Response([])
        
        # 예약된 시간 조회
        booked_times = Reservation.objects.filter(
            date=target_date,
            status__in=['pending', 'confirmed']
        ).values_list('time', flat=True)
        
        # 30분 간격으로 가능한 시간 생성
        available_times = []
        current_time = business_hours.open_time
        end_time = business_hours.close_time
        
        while current_time < end_time:
            # 서비스 소요시간을 고려하여 예약 가능한지 확인
            service_end_time = (
                datetime.combine(target_date, current_time) + 
                timedelta(minutes=service.duration)
            ).time()
            
            if service_end_time <= end_time:
                # 해당 시간대에 예약이 없는지 확인
                is_available = True
                check_time = current_time
                
                while check_time < service_end_time:
                    if check_time in booked_times:
                        is_available = False
                        break
                    check_time = (
                        datetime.combine(target_date, check_time) + 
                        timedelta(minutes=30)
                    ).time()
                
                if is_available:
                    available_times.append(current_time.strftime('%H:%M'))
            
            current_time = (
                datetime.combine(target_date, current_time) + 
                timedelta(minutes=30)
            ).time()
        
        return Response(available_times)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """추천 서비스 조회"""
        services = Service.objects.filter(is_active=True, is_featured=True)
        serializer = self.get_serializer(services, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """카테고리별 서비스 조회"""
        category_id = request.query_params.get('category_id')
        if category_id:
            services = Service.objects.filter(is_active=True, category_id=category_id)
        else:
            services = Service.objects.filter(is_active=True)
        serializer = self.get_serializer(services, many=True)
        return Response(serializer.data)


class ReservationViewSet(viewsets.ModelViewSet):
    """예약 관리 API"""
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """사용자별 예약 조회"""
        if self.request.user.is_staff:
            return Reservation.objects.all()
        return Reservation.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """액션에 따른 시리얼라이저 선택"""
        if self.action == 'create':
            return ReservationCreateSerializer
        return ReservationSerializer

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """예약 취소"""
        reservation = self.get_object()
        
        if reservation.status in ['completed', 'cancelled']:
            return Response(
                {"error": "이미 완료되거나 취소된 예약입니다."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reservation.status = 'cancelled'
        reservation.save()
        
        return Response({"message": "예약이 취소되었습니다."})

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """예약 확정 (관리자만)"""
        if not request.user.is_staff:
            return Response(
                {"error": "권한이 없습니다."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        reservation = self.get_object()
        reservation.status = 'confirmed'
        reservation.save()
        
        return Response({"message": "예약이 확정되었습니다."})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """예약 완료 (관리자만)"""
        if not request.user.is_staff:
            return Response(
                {"error": "권한이 없습니다."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        reservation = self.get_object()
        reservation.status = 'completed'
        reservation.save()
        
        return Response({"message": "예약이 완료되었습니다."})

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """다가오는 예약 조회"""
        today = timezone.now().date()
        upcoming_reservations = self.get_queryset().filter(
            date__gte=today,
            status__in=['pending', 'confirmed']
        ).order_by('date', 'time')
        
        serializer = self.get_serializer(upcoming_reservations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def history(self, request):
        """예약 내역 조회"""
        reservations = self.get_queryset().order_by('-date', '-time')
        serializer = self.get_serializer(reservations, many=True)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """리뷰 관리 API"""
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """사용자별 리뷰 조회"""
        if self.request.user.is_staff:
            return Review.objects.all()
        return Review.objects.filter(reservation__user=self.request.user)

    def perform_create(self, serializer):
        """리뷰 생성 시 예약 완료 여부 확인"""
        reservation = serializer.validated_data['reservation']
        
        if reservation.user != self.request.user:
            raise permissions.PermissionDenied("자신의 예약에만 리뷰를 작성할 수 있습니다.")
        
        if reservation.status != 'completed':
            raise permissions.PermissionDenied("완료된 예약에만 리뷰를 작성할 수 있습니다.")
        
        # 이미 리뷰가 있는지 확인
        if Review.objects.filter(reservation=reservation).exists():
            raise permissions.PermissionDenied("이미 리뷰를 작성했습니다.")
        
        serializer.save()

    @action(detail=False, methods=['get'])
    def service_reviews(self, request):
        """서비스별 리뷰 조회"""
        service_id = request.query_params.get('service_id')
        if not service_id:
            return Response(
                {"error": "service_id 파라미터가 필요합니다."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reviews = Review.objects.filter(reservation__service_id=service_id)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)


class BusinessHoursViewSet(viewsets.ReadOnlyModelViewSet):
    """영업시간 조회 API"""
    queryset = BusinessHours.objects.all()
    serializer_class = BusinessHoursSerializer
    permission_classes = [permissions.AllowAny]


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """사용자 정보 조회 API"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """자신의 정보만 조회 가능"""
        return User.objects.filter(id=self.request.user.id)
