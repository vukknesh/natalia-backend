from django.apps import AppConfig
import os
from datetime import datetime
from django.conf import settings


class UserprofileConfig(AppConfig):
    name = 'userprofile'

    def ready(self):
        from . import scheduler
        if settings.SCHEDULER_AUTOSTART:
            scheduler.start()
