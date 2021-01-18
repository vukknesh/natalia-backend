from __future__ import unicode_literals
from django.utils import timezone

from datetime import datetime, date
from django.conf import settings
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from rest_framework.response import Response


class Horario(models.Model):
    SEGUNDA = 0
    TERCA = 1
    QUARTA = 2
    QUINTA = 3
    SEXTA = 4
    DIA_CHOICES = (
        (SEGUNDA, 'Segunda'),
        (TERCA, 'Terca'),
        (QUARTA, 'Quarta'),
        (QUINTA, 'Quinta'),
        (SEXTA, 'Sexta'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    # dia = models.IntegerField(choices=DIA_CHOICES, default=0)
    dia = models.IntegerField()
    hora_aula = models.TimeField(
        auto_now=False, auto_now_add=False, default=timezone.now)

    class Meta:
        ordering = ['hora_aula']

    def __unicode__(self):
        return f'{self.user.first_name} - {self.hora_aula}'

    def __str__(self):
        return f'{self.user.first_name} - {self.hora_aula}'
