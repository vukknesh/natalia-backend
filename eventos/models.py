from __future__ import unicode_literals
from django.utils import timezone

from datetime import datetime, date
from django.conf import settings
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from rest_framework.response import Response


class EventoManager(models.Manager):

    def filter_by_instance(self, instance):

        qs = super(EventoManager, self).filter(
            user=instance.user)
        return qs


class Evento(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    comentario = models.CharField(max_length=255, null=True, blank=True)
    desmarcado = models.BooleanField(default=False)
    remarcacao = models.BooleanField(default=False)
    bonus = models.BooleanField(default=False)
    starting_date = models.DateTimeField(
        auto_now=False, auto_now_add=False, default=timezone.now)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    objects = EventoManager()

    class Meta:
        ordering = ['starting_date']

    def __unicode__(self):
        return f'{self.user.first_name} - {self.starting_date}'

    def __str__(self):
        return f'{self.user.first_name} - {self.starting_date}'

    def get_absolute_url(self):
        return reverse("eventos:thread", kwargs={"id": self.id})

    def get_delete_url(self):
        return reverse("eventos:delete", kwargs={"id": self.id})


def update_evento(sender, instance, **kwargs):
    user = instance.user
    now = datetime.now(timezone.utc)
    print(f'instance ={instance}')
    print(f'now ={now}')

    print('type of starting date ....')
    print(type(instance.starting_date))
    if type(instance.starting_date) == 'str':
        dt_obj = datetime.datetime.strptime(
            instance.starting_date, '%Y-%m-%d %H:%M:%S.%f')
        year = dt_obj.year
        month = dt_obj.month
    else:
        year = instance.starting_date.year
        month = instance.starting_date.month
    print(f'year ={year}')
    print(f'month ={month}')

    dt = date.today()
    print(f'dt ={dt}')
    dia_pg = user.profile.dia_pagamento
    print(f'dia_pg ={dia_pg}')
    month_mais = month + 1
    print(f'month_mais ={month_mais}')
    month_menos = month - 1
    print(f'month_menos ={month_menos}')
    if month_menos == 0:
        month_menos = 12
        year = year - 1

    if month_mais == 13:
        month_mais = 1
        year = year + 1

    if dt.day < dia_pg:
        print(f'dt < dia_pg')
        start_date = f'{year}-{month_menos}-{dia_pg}T00:00:00Z'
        end_date = f'{year}-{month}-{dia_pg}T00:00:00Z'
    else:
        print(f'dt > dia_pg')
        start_date = f'{year}-{month}-{dia_pg}T00:00:00Z'
        end_date = f'{year}-{month_mais}-{dia_pg}T00:00:00Z'

    print(f'start_date ={start_date}')
    print(f'end_date ={end_date}')
    # aulas_do_mes = user.evento_set.filter(starting_date__year__gte=year,
    #                                       starting_date__month__gte=month,
    #                                       starting_date__year__lte=year,
    #                                       starting_date__month__lte=month)
    aulas_do_mes = user.evento_set.filter(starting_date__gte=start_date,
                                          starting_date__lt=end_date)

    print(f'aulas_do_mes = {aulas_do_mes}')

    if(user.profile.plano == "4 Aulas"):
        if(aulas_do_mes.count() >= 4):
            instance.bonus = True
            pass
    if(user.profile.plano == "8 Aulas"):

        if(aulas_do_mes.count() >= 8):
            instance.bonus = True
            pass

    if(user.profile.plano == "12 Aulas"):

        if(aulas_do_mes.count() >= 12):
            instance.bonus = True
            pass
    print(f'instance{instance.comentario} pre save')


pre_save.connect(update_evento, sender=Evento)


# def update_evento(sender, instance, **kwargs):
#     user = instance.user
#     now = datetime.now(timezone.utc)
#     # print now.year, now.month, now.day, now.hour, now.minute, now.second
#     year = instance.starting_date.year
#     month = instance.starting_date.month
#     aulas_do_mes = user.evento_set.filter(starting_date__year__gte=year,
#                                           starting_date__month__gte=month,
#                                           starting_date__year__lte=year,
#                                           starting_date__month__lte=month)
#     my_list = list(aulas_do_mes)
#     my_list.append(instance)
#     newlist = sorted(my_list, key=lambda x: x.starting_date, reverse=True)
#     if(user.profile.plano == "4 Aulas"):

#         if(aulas_do_mes.count() >= 4):
#             a = newlist[0]
#             a.bonus = True
#             pass
#     if(user.profile.plano == "8 Aulas"):

#         if(aulas_do_mes.count() >= 8):
#             instance.bonus = True
#             pass

#     if(user.profile.plano == "12 Aulas"):

#         if(aulas_do_mes.count() >= 12):
#             instance.bonus = True
#             pass
#     print(f'instance{instance} pre save')


# pre_save.connect(update_evento, sender=Evento)
