from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import Poster, UserProfile, Gym, User, Image, Location, Schedule


# Сериализатор для модели Poster
class PosterSerializer(serializers.ModelSerializer):
    picture = serializers.ImageField(use_url=True)

    class Meta:
        model = Poster
        fields = ['picture', 'title', 'description', 'text']
        read_only_fields = ['publish_date']


# Базовый сериализатор для пользователя, исключающий чувствительные данные
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


# Сериализатор для регистрации пользователей
class UserRegistrationSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    token = serializers.CharField(read_only=True, source='auth_token.key')

    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name', 'email', 'token')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        UserProfile.objects.create(user=user)
        Token.objects.create(user=user)
        return user


# Сериализатор для входа пользователей
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user:
            return {'user': user}
        raise serializers.ValidationError("Incorrect Credentials")


class ScheduleSerializer(serializers.ModelSerializer):
    club = serializers.SlugRelatedField(slug_field='slug', queryset=Gym.objects.all())

    class Meta:
        model = Schedule
        fields = ['group', 'timestamp', 'address', 'club', 'user']


class ImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = Image
        fields = ['image']


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['latitude', 'longitude', 'address']


# Сериализатор для объектов Gym
class GymSerializer(serializers.ModelSerializer):
    location = LocationSerializer()  # Использование вложенного сериализатора
    pictures = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Gym
        fields = ['slug', 'name', 'pictures', 'description', 'location']


# Сериализатор для профилей пользователей
class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    gyms = GymSerializer(many=True, read_only=True)  # Используем вложенный сериализатор

    class Meta:
        model = UserProfile
        fields = ['user', 'avatar', 'phone_number', 'description', 'gyms']
