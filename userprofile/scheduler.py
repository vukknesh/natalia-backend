
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


# @register_job(scheduler, trigger='cron', hour='3', minute='30', replace_existing=True)
# def enviarParabens():
#     usuarios = User.objects.all()
#     now = datetime.now(timezone.utc)

#     for user in usuarios:

#         if user.profile.data_nascimento:
#             data = date(now.year, user.profile.data_nascimento.month,
#                         user.profile.data_nascimento.day)
#             data_menos_um = data - timedelta(1)
#             if now.date() == data.date():
#                 subject = 'Studio Natalia Secchi Deseja Feliz Aniversario'
#                 message = f"Feliz aniversario {user.first_name}. \n \n https://www.murukututu.com/confirm_email/userf87dsafhdsfandjsa7fda6{user.id} \n \n Natalia Secchi!"
#                 from_email = settings.EMAIL_HOST_USER
#                 to_list = [user.email]
#                 send_mail(subject, message, from_email,
#                           to_list, fail_silently=True)

#             if data_menos_um.date() == now.date():
#                 subject = 'Informe de aniversario de aluno'
#                 message = f" {user.first_name}. \n \n faz aniversario no dia {user.profile.data_nascimento} \n \n Natalia Secchi!"
#                 from_email = settings.EMAIL_HOST_USER
#                 to_list = ["leomcn@hotmail.com"]
#                 send_mail(subject, message, from_email,
#                           to_list, fail_silently=True)


# @register_job(scheduler, trigger='interval', minutes=2)
# @register_job(scheduler, trigger='cron', hour='3', minute='15', replace_existing=True)
# def enviar_parabens():
#     usuarios = Profile.objects.all()
#     now = datetime.now(timezone.utc)
#     month = now.month
#     day = now.day

#     tomorrow = now + timedelta(days=1)
#     print(f'day= {day}')
#     print(f'month= {month}')
#     print(f'tomorrow= {tomorrow}')
#     print(f'tomorrow.day= {tomorrow.day}')
#     print(f'tomorrow.month= {tomorrow.month}')
#     aniversariantes_hj = Profile.objects.filter(
#         data_nascimento__day=day).filter(data_nascimento__month=month)

#     aniversariantes_amanha = Profile.objects.filter(
#         data_nascimento__day=tomorrow.day).filter(data_nascimento__month=tomorrow.month)

#     print(f'aniversarioantes hj = {aniversariantes_hj}')
#     print(f'aniversarioantes amanha = {aniversariantes_amanha}')

#     for a in aniversariantes_hj:
#         print(f'a.data_nascimento =  {a.data_nascimento}')
#         subject = 'Studio Natalia Secchi Deseja Feliz Aniversario'
#         message = f"Feliz aniversario {a.user.first_name}."
#         from_email = settings.EMAIL_HOST_USER
#         to_list = [a.user.email]
#         send_mail(subject, message, from_email,
#                   to_list, fail_silently=False)
#     for b in aniversariantes_amanha:
#         print(f'b.data_nascimento =  {b.data_nascimento}')
#         subject = 'AVISO DE ANIVERSARIANTE AMANHA!'
#         message = f"Aluno {a.user.first_name}. vai fazer aniversario amanha!"
#         from_email = settings.EMAIL_HOST_USER
#         to_list = ["nataliasecchi@hotmail.com"]
#         send_mail(subject, message, from_email,
#                   to_list, fail_silently=False)


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
