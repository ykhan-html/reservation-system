from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Service, Reservation, Review, BusinessHours, Category, ServiceProvider, Notice


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ServiceProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProvider
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # 비밀번호 해싱
        from django.contrib.auth.hashers import make_password
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # 비밀번호가 제공된 경우에만 해싱
        if 'password' in validated_data:
            from django.contrib.auth.hashers import make_password
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    full_name = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'full_name']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")
        return attrs
    
    def create(self, validated_data):
        full_name = validated_data.pop('full_name', '')
        validated_data.pop('password2')
        
        # full_name을 first_name으로 저장
        validated_data['first_name'] = full_name
        
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='first_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name']


class ServiceSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    provider = ServiceProviderSerializer(read_only=True)
    provider_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    is_available = serializers.ReadOnlyField()
    
    class Meta:
        model = Service
        fields = [
            'id', 'category', 'category_id', 'provider', 'provider_id', 'name', 'description', 'price', 
            'duration', 'image', 'is_active', 'is_featured', 'stock_quantity',
            'min_advance_booking', 'max_advance_booking', 'is_available',
            'created_at', 'updated_at'
        ]


class BusinessHoursSerializer(serializers.ModelSerializer):
    day_display = serializers.CharField(source='get_day_display', read_only=True)

    class Meta:
        model = BusinessHours
        fields = '__all__'


class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = ['id', 'title', 'content', 'priority', 'is_active', 'is_pinned', 'created_at', 'updated_at']


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='reservation.user', read_only=True)
    service_name = serializers.CharField(source='reservation.service.name', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'reservation', 'rating', 'comment', 'created_at', 'user', 'service_name']


class ReservationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    service = ServiceSerializer(read_only=True)
    service_id = serializers.IntegerField(write_only=True)
    provider = ServiceProviderSerializer(read_only=True)
    provider_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    review = ReviewSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = [
            'id', 'user', 'service', 'service_id', 'provider', 'provider_id', 'date', 'time', 
            'status', 'status_display', 'notes', 'created_at', 'updated_at', 'review'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def create(self, validated_data):
        service_id = validated_data.pop('service_id')
        provider_id = validated_data.pop('provider_id', None)
        
        validated_data['service_id'] = service_id
        if provider_id:
            validated_data['provider_id'] = provider_id
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, data):
        # 예약 날짜가 과거가 아닌지 확인
        from django.utils import timezone
        if data['date'] < timezone.now().date():
            raise serializers.ValidationError("과거 날짜는 예약할 수 없습니다.")
        
        # 같은 시간에 중복 예약이 없는지 확인
        existing_reservation = Reservation.objects.filter(
            date=data['date'],
            time=data['time'],
            status__in=['pending', 'confirmed']
        ).first()
        
        if existing_reservation:
            raise serializers.ValidationError("해당 시간에 이미 예약이 있습니다.")
        
        return data


class ReservationCreateSerializer(serializers.ModelSerializer):
    service_id = serializers.IntegerField()
    provider_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Reservation
        fields = ['service_id', 'provider_id', 'date', 'time', 'notes']

    def create(self, validated_data):
        service_id = validated_data.pop('service_id')
        provider_id = validated_data.pop('provider_id', None)
        
        validated_data['service_id'] = service_id
        if provider_id:
            validated_data['provider_id'] = provider_id
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ServiceProviderLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ServiceProviderReservationSerializer(serializers.ModelSerializer):
    """서비스 제공자용 예약 시리얼라이저"""
    user = UserSerializer(read_only=True)
    service = ServiceSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Reservation
        fields = [
            'id', 'user', 'service', 'date', 'time', 'status', 'status_display', 
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'service', 'created_at', 'updated_at'] 