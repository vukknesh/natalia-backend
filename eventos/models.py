from __future__ import unicode_literals
from django.utils import timezone

from datetime import datetime
from django.conf import settings
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save


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
    bonus = models.BooleanField(default=False)
    starting_date = models.DateTimeField(
        auto_now=False, auto_now_add=False, default=timezone.now)
    timestamp = models.DateTimeField(auto_now_add=True)
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
    year = instance.starting_date.year
    month = instance.starting_date.month
    aulas_do_mes = user.evento_set.filter(starting_date__year__gte=year,
                                          starting_date__month__gte=month,
                                          starting_date__year__lte=year,
                                          starting_date__month__lte=month)
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
    print(f'instance{instance} pre save')


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
