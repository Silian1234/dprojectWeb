from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.contrib.auth import login, authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .forms import *
from .serializers import *


def csrf(request):
    return JsonResponse({'csrfToken': get_token(request)})


class UserRegistrationAPIView(APIView):
    def post(self, request, *args, **kwargs):
        form = UserRegistrationForm(data=request.data)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Аутентифицируем пользователя сразу после регистрации
            # Возвращаем успешный ответ с информацией о пользователе
            return Response({
                'username': user.username,
                'email': user.email,
                'avatar': user.userprofile.avatar.url if user.userprofile.avatar else None
            }, status=status.HTTP_201_CREATED)
        else:
            # Возвращаем информацию об ошибках в форме
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # Аутентификация сессии пользователя
            return Response({
                'message': 'Успешная аутентификация',
                'username': user.username,
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Неверные учетные данные'
            }, status=status.HTTP_401_UNAUTHORIZED)

class PosterListView(APIView):
    def get(self, request):
        posters = Poster.objects.all()
        serializer = PosterSerializer(posters, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)