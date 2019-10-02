# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

class User(AbstractUser):
    username = models.CharField(blank=True, null=True, max_length=50)
    teacher = models.OneToOneField('api.Teacher', blank=True, null = True, related_name="+", on_delete=models.CASCADE)
    student = models.OneToOneField('api.Student', blank=True, null = True, related_name='+', on_delete=models.CASCADE)
    email = models.EmailField(_('email address'), unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return "{}".format(self.email)
