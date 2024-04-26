from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_staff = models.BooleanField(default=False, verbose_name='Является сотрудником')
    avatar = models.ImageField(upload_to='user_avatars/', null=True, blank=True, verbose_name='Аватар')
    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()

class Poster(models.Model):
    image = models.ImageField(upload_to='posters/')
    title = models.CharField(max_length=200)
    text = models.TextField()
    publish_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title