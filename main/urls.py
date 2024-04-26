from django.urls import path
from .views import *

urlpatterns = [
    path('api/register/', UserRegistrationAPIView.as_view(), name='api_register'),
    path('api/login/', UserLoginAPIView.as_view(), name='api_login'),
    path('api/posters/', PosterListView.as_view(), name='poster_list'),
]
