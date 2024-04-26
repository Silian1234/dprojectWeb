from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


class UserRegistrationForm(UserCreationForm):
    avatar = forms.ImageField(required=False, label='Аватар')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'avatar')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            user_profile = UserProfile.objects.create(
                user=user,
                avatar=self.cleaned_data.get('avatar', None)
            )
        return user
