import logging
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.utils.timezone import localtime
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .permission import IsStaff
from .serializers import *

logger = logging.getLogger(__name__)

class GymViewSet(viewsets.ModelViewSet):
    queryset = Gym.objects.all()
    serializer_class = GymSerializer
    lookup_field = 'slug'
    permission_classes = [AllowAny]

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.select_related('user').all()
    serializer_class = UserProfileSerializer
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('username', openapi.IN_FORM, description="Username", type=openapi.TYPE_STRING),
            openapi.Parameter('password', openapi.IN_FORM, description="Password", type=openapi.TYPE_STRING),
            openapi.Parameter('first_name', openapi.IN_FORM, description="First Name", type=openapi.TYPE_STRING),
            openapi.Parameter('last_name', openapi.IN_FORM, description="Last Name", type=openapi.TYPE_STRING),
            openapi.Parameter('email', openapi.IN_FORM, description="Email", type=openapi.TYPE_STRING),
            openapi.Parameter('avatar', openapi.IN_FORM, description="Avatar", type=openapi.TYPE_FILE),
            openapi.Parameter('phone_number', openapi.IN_FORM, description="Phone Number", type=openapi.TYPE_STRING),
            openapi.Parameter('description', openapi.IN_FORM, description="Description", type=openapi.TYPE_STRING),
            openapi.Parameter('is_staff', openapi.IN_FORM, description="Is Staff", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('group_number', openapi.IN_FORM, description="Group Number", type=openapi.TYPE_STRING),
        ]
    )
    def create(self, request, *args, **kwargs):
        user_data = {
            'username': request.data.get('username'),
            'password': request.data.get('password'),
            'first_name': request.data.get('first_name'),
            'last_name': request.data.get('last_name'),
            'email': request.data.get('email')
        }

        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        user.set_password(user_data['password'])
        user.save()

        profile_data = {
            'user': user.id,
            'avatar': request.FILES.get('avatar'),
            'phone_number': request.data.get('phone_number'),
            'description': request.data.get('description'),
            'is_staff': request.data.get('is_staff'),
            'group_number': request.data.get('group_number')
        }

        profile_serializer = self.get_serializer(data=profile_data)
        profile_serializer.is_valid(raise_exception=True)
        self.perform_create(profile_serializer)

        headers = self.get_success_headers(profile_serializer.data)
        return Response(profile_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('username', openapi.IN_FORM, description="Username", type=openapi.TYPE_STRING),
            openapi.Parameter('password', openapi.IN_FORM, description="Password", type=openapi.TYPE_STRING),
            openapi.Parameter('first_name', openapi.IN_FORM, description="First Name", type=openapi.TYPE_STRING),
            openapi.Parameter('last_name', openapi.IN_FORM, description="Last Name", type=openapi.TYPE_STRING),
            openapi.Parameter('email', openapi.IN_FORM, description="Email", type=openapi.TYPE_STRING),
            openapi.Parameter('avatar', openapi.IN_FORM, description="Avatar", type=openapi.TYPE_FILE),
            openapi.Parameter('phone_number', openapi.IN_FORM, description="Phone Number", type=openapi.TYPE_STRING),
            openapi.Parameter('description', openapi.IN_FORM, description="Description", type=openapi.TYPE_STRING),
            openapi.Parameter('is_staff', openapi.IN_FORM, description="Is Staff", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('group_number', openapi.IN_FORM, description="Group Number", type=openapi.TYPE_STRING),
        ]
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        user_data = {
            'username': request.data.get('username', instance.user.username),
            'password': request.data.get('password'),
            'first_name': request.data.get('first_name', instance.user.first_name),
            'last_name': request.data.get('last_name', instance.user.last_name),
            'email': request.data.get('email', instance.user.email)
        }

        user_serializer = UserSerializer(instance.user, data=user_data, partial=partial)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        if 'password' in request.data:
            user.set_password(request.data['password'])
            user.save()

        avatar = request.FILES.get('avatar', instance.avatar if instance.avatar else None)

        profile_data = {
            'avatar': avatar,
            'phone_number': request.data.get('phone_number', instance.phone_number),
            'description': request.data.get('description', instance.description),
            'is_staff': request.data.get('is_staff', instance.is_staff),
            'group_number': request.data.get('group_number', instance.group_number)
        }

        profile_serializer = self.get_serializer(instance, data=profile_data, partial=partial)
        profile_serializer.is_valid(raise_exception=True)
        self.perform_update(profile_serializer)

        return Response(profile_serializer.data)


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
    permission_classes = [AllowAny]

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
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
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

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleItemSerializer
    permission_classes = [AllowAny]

    def get_weekly_schedule(self):
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        schedule = {day: {} for day in days}

        schedules = Schedule.objects.select_related('user', 'club').all()
        for sched in schedules:
            local_timestamp = localtime(sched.timestamp)
            day_name = days[local_timestamp.weekday()]
            hour = local_timestamp.hour
            schedule[day_name][hour] = {
                'time': hour,
                'event': sched
            }

        for day in days:
            for hour in range(12, 19):
                if hour not in schedule[day]:
                    schedule[day][hour] = {
                        'time': hour,
                        'event': None
                    }

        return schedule

    @action(detail=False, methods=['get'])
    def weekly(self, request):
        schedule_data = self.get_weekly_schedule()
        serializer = WeeklyScheduleSerializer(schedule_data)
        return Response(serializer.data)

class PosterViewSet(viewsets.ModelViewSet):
    queryset = Poster.objects.all()
    serializer_class = PosterSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_permissions(self):
        if self.action == 'create':
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
router.register(r'gyms', GymViewSet)
router.register(r'profiles', ProfileViewSet)
router.register(r'schedule', ScheduleViewSet)
