import logging

from django.http import JsonResponse
from django.middleware.csrf import get_token
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView

from .permission import IsStaff
from .serializers import *
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import UserRegistrationSerializer, UserLoginSerializer

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

    def get_serializer_class(self):
        if self.action == 'register':
            return UserRegistrationSerializer
        elif self.action == 'login':
            return UserLoginSerializer
        else:
            return None

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    @swagger_auto_schema(
        method='post',
        request_body=UserRegistrationSerializer,
        responses={201: openapi.Response('Registration Successful', UserRegistrationSerializer)}
    )
    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = Token.objects.get(user=user)
            return Response({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        method='post',
        request_body=UserLoginSerializer,
        responses={
            200: openapi.Response('Login Successful', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
                    'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
                    'token': openapi.Schema(type=openapi.TYPE_STRING, description='Authentication token')
                }
            )),
            400: 'Invalid username or password'
        }
    )
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'Успешная аутентификация',
                'id': user.id,
                'username': user.username,
                'token': token.key
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserRegistrationAPIView(APIView):
    permission_classes = [AllowAny]  # Разрешаем регистрацию любому пользователю

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
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

logger = logging.getLogger(__name__)


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated, IsStaff]

    def perform_create(self, serializer):
        serializer.save()


class PosterViewSet(viewsets.ModelViewSet):
    queryset = Poster.objects.all()
    serializer_class = PosterSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_permissions(self):
        if self.action == 'create':  # Это срабатывает на POST запросы
            self.permission_classes = [IsAuthenticated, IsStaff]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        logger.info(f"Request headers: {request.headers}")
        logger.info(f"Request data: {request.data}")
        return super().create(request, *args, **kwargs)

router = DefaultRouter()
router.register(r'blog', PosterViewSet)
