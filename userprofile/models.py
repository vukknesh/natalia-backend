from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.urls import reverse
from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.utils.text import slugify


class Profile(models.Model):
    slug = models.SlugField(unique=True)
    # personal

    aulas_remarcadas = models.IntegerField(default=0)
    #image = models.ImageField(default='defprofile.jpg', upload_to='profile_pics', validators=[validate_file_size])
    PLANO_A = '4 Aulas'
    PLANO_B = '8 Aulas'
    PLANO_C = '12 Aulas'
    PLANO_CHOICES = (
        (PLANO_A, '4 Aulas'),
        (PLANO_B, '8 Aulas'),
        (PLANO_C, '12 Aulas'),
    )
    plano = models.CharField(
        max_length=20,
        choices=PLANO_CHOICES,
        default="4 Aulas"
    )
    endereco = models.CharField(max_length=255, null=True, blank=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse("profiles:detail", kwargs={"id": self.id})

    def get_api_url(self):
        return reverse("profiles-api:detail", kwargs={"id": self.id})


def create_slug(instance, new_slug=None):
    slug = slugify(instance.user.first_name)
    if new_slug is not None:
        slug = new_slug
    qs = Profile.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" % (slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug


def pre_save_profile_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):

    instance.profile.save()


pre_save.connect(pre_save_profile_receiver, sender=Profile)
