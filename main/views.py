from django.http import JsonResponse
from django.middleware.csrf import get_token
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from .serializers import *
from drf_yasg.utils import swagger_auto_schema

# Можете добавить вашу настройку аутентификации на уровне проекта в settings.py

class GymViewSet(viewsets.ModelViewSet):
    queryset = Gym.objects.all()
    serializer_class = GymSerializer
    lookup_field = 'slug'
    #authentication_classes = [TokenAuthentication]  # Предполагаем, что используете Token Authentication
    permission_classes = [AllowAny]  # Только аутентифицированные пользователи могут получить доступ

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.select_related('user').all()  # Добавляем select_related для оптимизации запроса
    serializer_class = UserProfileSerializer
    #authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]

def csrf(request):
    return JsonResponse({'csrfToken': get_token(request)})

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=UserRegistrationSerializer)
    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'username': user.username,
                'email': user.email,
                'avatar': user.userprofile.avatar.url if user.userprofile.avatar else None
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=UserLoginSerializer)
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'Успешная аутентификация',
                'username': user.username,
                'token': token.key
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'Успешная аутентификация',
                'username': user.username,
                'token': token.key
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class UserRegistrationAPIView(APIView):
    permission_classes = [AllowAny]  # Разрешаем регистрацию любому пользователю

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)  # Используйте Serializer вместо Form
        if serializer.is_valid():
            user = serializer.save()
            # Аутентификация с использованием DRF, вместо Django login
            return Response({
                'username': user.username,
                'email': user.email,
                'avatar': user.userprofile.avatar.url if user.userprofile.avatar else None
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)  # Предполагается наличие такого Serializer
        if serializer.is_valid():
            user = serializer.validated_data['user']
            # DRF аутентификация с Token
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'Успешная аутентификация',
                'username': user.username,
                'token': token.key
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class PosterListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        posters = Poster.objects.all()
        serializer = PosterSerializer(posters, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PosterDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            poster = Poster.objects.get(pk=pk)
        except Poster.DoesNotExist:
            return Response({'error': 'Poster not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PosterSerializer(poster)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PosterViewSet(viewsets.ModelViewSet):
    queryset = Poster.objects.all()
    serializer_class = PosterSerializer
    permission_classes = [AllowAny]  # Разрешить доступ всем пользователям
    parser_classes = (MultiPartParser, FormParser)  # Добавить парсеры для обработки файлов


router = DefaultRouter()
router.register(r'blog', PosterViewSet)
