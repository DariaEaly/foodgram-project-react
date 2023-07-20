from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Адрес электронной почты'
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Username'
    )

    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя'
    )

    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')


class Follow(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='follower',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Подписчик')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='following',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Пользователь, на которого подписываются')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'author'],
                                               name='unique_follow')]
