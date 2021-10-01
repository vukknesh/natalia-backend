
from datetime import datetime, date, timedelta
import os
import time
from .models import Profile

from datetime import datetime, timezone, timedelta, date
from django.core.mail import send_mail
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from financeiro.views import resumo_mensal
from django.conf import settings
from calendar import monthrange
from django.contrib.auth.models import User
scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")


# def last_day_of_month(date_value):
#     return date_value.replace(day=monthrange(date_value.year, date_value.month)[1])
# @register_job(scheduler, "interval", seconds=60, replace_existing=True)


@register_job(scheduler, trigger='cron', hour='3', minute='30', replace_existing=True)
def enviarParabens():
    usuarios = User.objects.all()
    now = datetime.now(timezone.utc)

    for user in usuarios:

        if user.profile.data_nascimento:
            data = date(now.year, user.profile.data_nascimento.month,
                        user.profile.data_nascimento.day)
            data_menos_um = data - timedelta(1)
#             if now.date() == data.date():
#                 subject = 'Studio Natalia Secchi Deseja Feliz Aniversario'
#                 message = f"Feliz aniversario {user.first_name}. \n \n https://www.murukututu.com/confirm_email/userf87dsafhdsfandjsa7fda6{user.id} \n \n Natalia Secchi!"
#                 from_email = settings.EMAIL_HOST_USER
#                 to_list = [user.email]
#                 send_mail(subject, message, from_email,
#                           to_list, fail_silently=True)

            if data_menos_um.date() == now.date():
                subject = f'🎂 Amanhã é o aniversário de {user.first_name}'
                message = f"🎂 Amanhã é o aniversário de {user.first_name}"
                from_email = settings.EMAIL_HOST_USER
                to_list = ["nat_secchi@hotmail.com"]
                send_mail(subject, message, from_email,
                          to_list, fail_silently=True)


@register_job(scheduler, trigger='cron', hour='3', minute='10', replace_existing=True)
def resetRemarcadas():
    now = datetime.now(timezone.utc)

    alunos = Profile.objects.all()
    for aluno in alunos:
        if aluno.data_nascimento == now.day:
            # test day for aniverssario
            pass
        if aluno.dia_pagamento == now.day:
            Profile.objects.filter(user=aluno.user).update(
                aulas_remarcadas=0, bonus_remarcadas=0, aulas_reposicao=0)

    # Profile.objects.all().update(aulas_remarcadas=0)


@register_job(scheduler, trigger='cron', day='last', hour='20', replace_existing=True)
def resetDia():

    resumo_mensal()


register_events(scheduler)


def start():
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(sayHello, 'interval', seconds=10)
    # scheduler.add_job(sayHello, trigger='cron', hour='23', minute='59')
    scheduler.start()
