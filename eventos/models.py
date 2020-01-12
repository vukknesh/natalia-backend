from __future__ import unicode_literals
from datetime import datetime, timezone
from datetime import datetime
from django.conf import settings
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


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
    # print now.year, now.month, now.day, now.hour, now.minute, now.second
    year = now.year
    month = now.month
    aulas_do_mes = user.evento_set.filter(starting_date__year__gte=year,
                                          starting_date__month__gte=month,
                                          starting_date__year__lte=year,
                                          starting_date__month__lte=month)
    if(user.profile.plano == "4 Aulas"):

        if(aulas_do_mes.count() > 4):
            instance.bonus = True
            pass
    if(user.profile.plano == "8 Aulas"):
        print(f'eentrou 8')

        if(aulas_do_mes.count() > 8):
            print(f'eentrou >    8')
            instance.bonus = True
            print(f'instance.bonus {instance.bonus}')
            pass

    if(user.profile.plano == "12 Aulas"):

        if(aulas_do_mes.count() > 12):
            instance.bonus = True
            pass
    print(f'instance{instance} pre save')
    instance.save()
    print(f'instance{instance} post save')


post_save.connect(update_evento, sender=Evento)
