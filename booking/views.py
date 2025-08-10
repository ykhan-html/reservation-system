from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Service, Reservation, Review, BusinessHours, Category, ServiceProvider, Notice
from .serializers import (
    ServiceSerializer, ReservationSerializer, ReviewSerializer,
    BusinessHoursSerializer, UserSerializer, ReservationCreateSerializer,
    UserRegistrationSerializer, CategorySerializer, ServiceProviderSerializer,
    ServiceProviderLoginSerializer, ServiceProviderReservationSerializer, NoticeSerializer
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
        print(f"로그인 요청 데이터: {request.data}")
        print(f"요청 타입: {type(request.data)}")
        print(f"요청 헤더: {request.headers}")
        
        # JSON 데이터 파싱 시도
        username = None
        password = None
        
        # 방법 1: request.data에서 가져오기 (DRF 기본)
        if request.data:
            username = request.data.get('username')
            password = request.data.get('password')
            print(f"request.data에서 파싱: username={username}, password={password}")
        
        # 방법 2: POST 데이터에서 가져오기
        if not username or not password:
            username = request.POST.get('username')
            password = request.POST.get('password')
            print(f"request.POST에서 파싱: username={username}, password={password}")
        
        print(f"최종 사용자명: {username}")
        print(f"최종 비밀번호: {password}")
        
        if not username or not password:
            return Response({
                'error': '사용자명과 비밀번호를 입력해주세요.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        print(f"인증 결과: {user}")
        
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
            old_status = reservation.status
            new_status = request.data.get('status')
            
            if new_status in ['pending', 'confirmed', 'completed', 'cancelled']:
                reservation.status = new_status
                reservation.save()
                
                # 상태가 '확정'으로 변경되거나 '확정'에서 다른 상태로 변경될 때
                # 해당 시간대의 예약 가능 여부가 변경됨을 알림
                status_changed = old_status != new_status
                time_slot_affected = old_status in ['pending', 'confirmed'] or new_status in ['pending', 'confirmed']
                
                serializer = self.get_serializer(reservation)
                response_data = serializer.data
                
                if status_changed and time_slot_affected:
                    response_data['time_slot_updated'] = True
                    response_data['message'] = f'예약 상태가 {reservation.get_status_display()}로 변경되었습니다.'
                    
                    # 해당 날짜의 예약 가능한 시간대를 다시 계산하여 제공
                    if reservation.service.provider:
                        from datetime import datetime, timedelta
                        from .models import BusinessHours
                        
                        target_date = reservation.date
                        weekday = target_date.weekday()
                        business_hours = BusinessHours.objects.filter(day=weekday).first()
                        
                        if business_hours and not business_hours.is_closed:
                            # 해당 쌤의 예약된 시간 조회
                            booked_times = Reservation.objects.filter(
                                date=target_date,
                                status__in=['pending', 'confirmed'],
                                provider=reservation.service.provider
                            ).values_list('time', flat=True)
                            
                            # 30분 간격으로 가능한 시간 생성
                            available_times = []
                            current_time = business_hours.open_time
                            end_time = business_hours.close_time
                            
                            while current_time < end_time:
                                # 서비스 소요시간을 고려하여 예약 가능한지 확인
                                service_end_time = (
                                    datetime.combine(target_date, current_time) + 
                                    timedelta(minutes=reservation.service.duration)
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
                            
                            response_data['available_times'] = available_times
                            response_data['date'] = target_date.strftime('%Y-%m-%d')
                            response_data['provider_id'] = reservation.service.provider.id
                            response_data['service_id'] = reservation.service.id
                
                return Response(response_data)
            else:
                return Response({'error': '유효하지 않은 상태입니다.'}, status=400)
        except Reservation.DoesNotExist:
            return Response({'error': '예약을 찾을 수 없습니다.'}, status=404)

    @action(detail=False, methods=['get'])
    def time_slot_updates(self, request):
        """시간대 업데이트 정보 조회 (메인 페이지용)"""
        provider_id = request.session.get('provider_id')
        if not provider_id:
            return Response({'error': '로그인이 필요합니다.'}, status=401)
        
        # 최근 상태 변경된 예약들 조회 (1시간 이내)
        from django.utils import timezone
        from datetime import timedelta
        
        recent_time = timezone.now() - timedelta(hours=1)
        recent_reservations = Reservation.objects.filter(
            provider_id=provider_id,
            updated_at__gte=recent_time,
            status__in=['pending', 'confirmed']
        ).order_by('-updated_at')
        
        updates = []
        for reservation in recent_reservations:
            # 해당 날짜의 예약 가능한 시간대 계산
            target_date = reservation.date
            weekday = target_date.weekday()
            business_hours = BusinessHours.objects.filter(day=weekday).first()
            
            if business_hours and not business_hours.is_closed:
                from datetime import datetime
                
                # 해당 쌤의 예약된 시간 조회
                booked_times = Reservation.objects.filter(
                    date=target_date,
                    status__in=['pending', 'confirmed'],
                    provider=reservation.service.provider
                ).values_list('time', flat=True)
                
                # 30분 간격으로 가능한 시간 생성
                available_times = []
                current_time = business_hours.open_time
                end_time = business_hours.close_time
                
                while current_time < end_time:
                    # 서비스 소요시간을 고려하여 예약 가능한지 확인
                    service_end_time = (
                        datetime.combine(target_date, current_time) + 
                        timedelta(minutes=reservation.service.duration)
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
                
                updates.append({
                    'date': target_date.strftime('%Y-%m-%d'),
                    'available_times': available_times,
                    'provider_id': reservation.service.provider.id,
                    'service_id': reservation.service.id,
                    'updated_at': reservation.updated_at.isoformat()
                })
        
        return Response(updates)


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
        """권한 설정"""
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
        
        # 현재 사용자의 기존 예약 조회 (로그인한 경우에만)
        user_booked_times = []
        if request.user.is_authenticated:
            user_booked_times = Reservation.objects.filter(
                user=request.user,
                date=target_date,
                status__in=['pending', 'confirmed']
            ).values_list('time', flat=True)
        
        # 해당 서비스의 제공자(쌤)가 예약된 시간 조회
        # 서비스에 직접 연결된 제공자가 있으면 해당 제공자의 예약만 확인
        # 서비스에 제공자가 없으면 모든 예약 확인
        if service.provider:
            # 특정 쌤의 예약만 확인
            provider_booked_times = Reservation.objects.filter(
                date=target_date,
                status__in=['pending', 'confirmed'],
                provider=service.provider
            ).values_list('time', flat=True)
        else:
            # 모든 예약 확인 (기존 로직)
            provider_booked_times = Reservation.objects.filter(
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
                    # 다른 사용자의 예약 확인
                    if check_time in provider_booked_times:
                        is_available = False
                        break
                    # 현재 사용자의 예약 확인
                    if check_time in user_booked_times:
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

    @action(detail=True, methods=['get'])
    def check_time_updates(self, request, pk=None):
        """특정 서비스의 시간대 업데이트 확인"""
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
        
        # 해당 서비스의 제공자가 있는 경우에만 확인
        if not service.provider:
            return Response({"message": "서비스에 연결된 제공자가 없습니다."})
        
        # 영업시간 확인
        weekday = target_date.weekday()
        business_hours = BusinessHours.objects.filter(day=weekday).first()
        
        if not business_hours or business_hours.is_closed:
            return Response({"message": "해당 날짜는 영업하지 않습니다."})
        
        # 현재 사용자의 기존 예약 조회 (로그인한 경우에만)
        user_booked_times = []
        if request.user.is_authenticated:
            user_booked_times = Reservation.objects.filter(
                user=request.user,
                date=target_date,
                status__in=['pending', 'confirmed']
            ).values_list('time', flat=True)
        
        # 해당 쌤의 예약된 시간 조회
        provider_booked_times = Reservation.objects.filter(
            date=target_date,
            status__in=['pending', 'confirmed'],
            provider=service.provider
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
                    # 다른 사용자의 예약 확인
                    if check_time in provider_booked_times:
                        is_available = False
                        break
                    # 현재 사용자의 예약 확인
                    if check_time in user_booked_times:
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
        
        return Response({
            'date': date_str,
            'available_times': available_times,
            'provider_id': service.provider.id,
            'service_id': service.id,
            'last_updated': timezone.now().isoformat()
        })

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

    def create(self, request, *args, **kwargs):
        """예약 생성 시 중복 예약 방지"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 예약 데이터 추출
        service_id = serializer.validated_data['service_id']
        service = Service.objects.get(id=service_id)
        date = serializer.validated_data['date']
        time = serializer.validated_data['time']
        provider_id = serializer.validated_data.get('provider_id')
        
        # 1. 같은 사용자가 같은 서비스에 대해 같은 날짜/시간에 중복 예약하는지 확인
        user_duplicate = Reservation.objects.filter(
            user=request.user,
            service=service,
            date=date,
            time=time,
            status__in=['pending', 'confirmed']
        ).first()
        
        if user_duplicate:
            return Response(
                {"error": "이미 동일한 서비스에 대해 같은 날짜와 시간에 예약이 있습니다."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 2. 같은 서비스에 대해 같은 날짜/시간에 다른 사용자가 이미 예약했는지 확인
        service_duplicate = Reservation.objects.filter(
            service=service,
            date=date,
            time=time,
            status__in=['pending', 'confirmed']
        ).first()
        
        if service_duplicate:
            return Response(
                {"error": "해당 시간에 이미 예약이 있습니다."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 3. provider_id가 제공된 경우, 해당 제공자의 중복 예약 확인
        if provider_id:
            try:
                provider = ServiceProvider.objects.get(id=provider_id)
                provider_duplicate = Reservation.objects.filter(
                    provider=provider,
                    date=date,
                    time=time,
                    status__in=['pending', 'confirmed']
                ).first()
                
                if provider_duplicate:
                    return Response(
                        {"error": "해당 쌤의 시간에 이미 예약이 있습니다."}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ServiceProvider.DoesNotExist:
                return Response(
                    {"error": "존재하지 않는 서비스 제공자입니다."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # 예약 생성
        reservation = serializer.save(user=request.user)
        
        # provider_id가 제공된 경우 해당 제공자로 설정
        if provider_id:
            try:
                provider = ServiceProvider.objects.get(id=provider_id)
                reservation.provider = provider
                reservation.save()
            except ServiceProvider.DoesNotExist:
                pass  # 제공자가 존재하지 않으면 무시
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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


class NoticeViewSet(viewsets.ReadOnlyModelViewSet):
    """공지사항 조회 API"""
    queryset = Notice.objects.filter(is_active=True)
    serializer_class = NoticeSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """활성화된 공지사항만 반환, 상단 고정 우선"""
        return Notice.objects.filter(is_active=True).order_by('-is_pinned', '-priority', '-created_at')


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """사용자 정보 조회 API"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """자신의 정보만 조회 가능"""
        return User.objects.filter(id=self.request.user.id)


def check_time_updates(request, service_id):
    """시간대 업데이트 확인 API"""
    from rest_framework.decorators import api_view
    from rest_framework.response import Response
    from rest_framework import status
    
    date = request.GET.get('date')
    if not date:
        return Response({'error': '날짜가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        service = Service.objects.get(id=service_id)
        
        # 해당 날짜의 예약 가능한 시간 계산
        available_times = []
        
        # 기본 영업시간 가져오기
        business_hours = BusinessHours.objects.filter(
            day_of_week=datetime.strptime(date, '%Y-%m-%d').weekday()
        ).first()
        
        if business_hours:
            # 영업시간 내의 시간대 생성 (30분 단위)
            start_time = business_hours.open_time
            end_time = business_hours.close_time
            
            current_time = start_time
            while current_time < end_time:
                time_str = current_time.strftime('%H:%M')
                
                # 해당 시간에 이미 확정된 예약이 있는지 확인
                confirmed_reservation = Reservation.objects.filter(
                    service=service,
                    date=date,
                    time=time_str,
                    status='confirmed'
                ).exists()
                
                # 해당 시간에 대기 중인 예약이 있는지 확인
                pending_reservation = Reservation.objects.filter(
                    service=service,
                    date=date,
                    time=time_str,
                    status='pending'
                ).exists()
                
                # 확정된 예약이 없고, 대기 중인 예약만 있거나 없는 경우에만 예약 가능
                if not confirmed_reservation:
                    available_times.append(time_str)
                
                # 30분씩 증가
                current_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=30)).time()
        
        return Response({'available_times': available_times})
        
    except Service.DoesNotExist:
        return Response({'error': '서비스를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
