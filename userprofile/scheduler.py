
from datetime import datetime, date, timedelta
import os
import time
from .models import Profile

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from financeiro.views import resumo_mensal

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")


# @register_job(scheduler, "interval", seconds=30, replace_existing=True)
# @register_job(scheduler, 'interval', seconds=30, replace_existing=True)
@register_job(scheduler, trigger='cron', day='last', hour='20', replace_existing=True)
def resetDia():
    Profile.objects.all().update(aulas_remarcadas=0)
    print("Profile done")
    resumo_mensal()


register_events(scheduler)


def start():
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(sayHello, 'interval', seconds=10)
    # scheduler.add_job(sayHello, trigger='cron', hour='23', minute='59')
    scheduler.start()
