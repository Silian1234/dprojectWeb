from rest_framework import serializers
from .models import Poster

class PosterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poster
        fields = ['image', 'title', 'text', 'publish_date']
