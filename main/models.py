from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    # Связь "один к одному" с встроенной моделью User
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Дополнительные поля
    phone_number = models.CharField(max_length=20, blank=True, verbose_name='Номер телефона')
    is_staff = models.BooleanField(default=False, verbose_name='Является сотрудником')
    avatar = models.ImageField(upload_to='user_avatars/', null=True, blank=True, verbose_name='Аватар')
    def __str__(self):
        return self.user.username

# Сигналы для автоматического создания/обновления профиля пользователя при создании/обновлении объекта User
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()
