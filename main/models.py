from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_staff = models.BooleanField(default=False, verbose_name='Является сотрудником')
    avatar = models.ImageField(upload_to='user_avatars/', null=True, blank=True, verbose_name='Аватар')
    phone_number = models.CharField(max_length=15, null=True, blank=True, verbose_name='Телефонный номер')
    description = models.TextField(null=True, blank=True, verbose_name='О себе')
    gyms = models.ManyToManyField('Gym', null=True, related_name='members')  # Изменено related_name
    trainees = models.ManyToManyField('self', symmetrical=False, related_name='trainers', blank=True)
    group_number = models.CharField(max_length=15, null=True, blank=True, verbose_name='Номер группы')

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

class Poster(models.Model):
    picture = models.ImageField(upload_to='posters/')
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=255, null=True, blank=True)
    text = models.TextField()
    publish_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Location(models.Model):
    latitude = models.FloatField(verbose_name='Широта')
    longitude = models.FloatField(verbose_name='Долгота')
    address = models.CharField(max_length=200, verbose_name='Адрес')

    def __str__(self):
        return f"{self.latitude}, {self.longitude} - {self.address}"


class Image(models.Model):
    image = models.ImageField(upload_to='gyms/')



class Gym(models.Model):
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    name = models.CharField(max_length=255)
    pictures = models.ManyToManyField(Image, related_name='gyms')
    description = models.TextField(null=True, blank=True, verbose_name='Описание зала')
    location = models.OneToOneField(Location, on_delete=models.CASCADE)
    users = models.ManyToManyField(UserProfile, related_name='user_profiles')  # Изменено related_name для предотвращения конфликта

    def save(self, *args, **kwargs):
        if not self.slug:  # Генерируем slug только если он еще не установлен
            self.slug = slugify(self.name)
        super(Gym, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Schedule(models.Model):
    group = models.IntegerField(verbose_name='Группа')
    timestamp = models.IntegerField(verbose_name='Метка времени')
    address = models.CharField(max_length=255, verbose_name='Адрес')
    club = models.ForeignKey(Gym, on_delete=models.CASCADE, verbose_name='Клуб')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='Пользователь')

    def __str__(self):
        return f"Group {self.group} at {self.address} on {self.timestamp}"
