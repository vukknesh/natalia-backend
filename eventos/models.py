from __future__ import unicode_literals

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db.models.signals import pre_save

from markdown_deux import markdown


class EventoManager(models.Manager):

    def filter_by_instance(self, instance):

        qs = super(EventoManager, self).filter(
            user=instance.user)
        return qs


class Evento(models.Model):
    slug = models.SlugField(unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    comentario = models.CharField(max_length=255, null=True, blank=True)
    desmarcado = models.BooleanField(default=False)
    starting_date = models.DateTimeField(max_length=20, null=True, blank=True)
    ending_date = models.DateTimeField(max_length=20, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    publish = models.DateField(auto_now=True, auto_now_add=False)
    objects = EventoManager()

    class Meta:
        ordering = ['-starting_date']

    def __unicode__(self):
        return str(self.user.first_name)

    def __str__(self):
        return str(self.user.first_name)

    def get_absolute_url(self):
        return reverse("eventos:thread", kwargs={"id": self.id})

    def get_delete_url(self):
        return reverse("eventos:delete", kwargs={"id": self.id})


def create_slug(instance, new_slug=None):
    slug = slugify(instance.starting_date)
    if new_slug is not None:
        slug = new_slug
    qs = Evento.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" % (slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug


def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)


pre_save.connect(pre_save_post_receiver, sender=Evento)
