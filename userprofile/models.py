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
    bonus_remarcadas = models.IntegerField(default=0)
    #image = models.ImageField(default='defprofile.jpg', upload_to='profile_pics', validators=[validate_file_size])
    PLANO_A = '4 Aulas'
    PLANO_B = '8 Aulas'
    PLANO_C = '12 Aulas'
    PLANO_D = 'Gratuito'
    PAGAMENTO_A = 'Mensal'
    PAGAMENTO_B = 'Trimestral'
    PAGAMENTO_C = 'Semestral'
    PAGAMENTO_D = 'Anual'
    ESTADO_A = 'Solteiro(a)'
    ESTADO_B = 'Casado(a)'
    ESTADO_C = 'Separado(a)'
    ESTADO_D = 'Divorciado(a)'
    ESTADO_E = 'Viuvo(a)'
    ESTADO_F = 'Uniao Estavel'
    ESTADO_CHOICES = (
        (ESTADO_A, 'Solteiro(a)'),
        (ESTADO_B, 'Casado(a)'),
        (ESTADO_C, 'Separado(a)'),
        (ESTADO_D, 'Divorciado(a)'),
        (ESTADO_E, 'Viuvo(a)'),
        (ESTADO_F, 'Uniao Estavel'),
    )
    PLANO_CHOICES = (
        (PLANO_A, '4 Aulas'),
        (PLANO_B, '8 Aulas'),
        (PLANO_C, '12 Aulas'),
        (PLANO_D, 'Gratuito'),
    )
    PAGAMENTO_CHOICES = (
        (PAGAMENTO_A, 'Mensal'),
        (PAGAMENTO_B, 'Trimestral'),
        (PAGAMENTO_C, 'Semestral'),
        (PAGAMENTO_D, 'Anual'),
    )
    plano = models.CharField(
        max_length=20,
        choices=PLANO_CHOICES,
        default="4 Aulas"
    )
    data_nascimento = models.DateField(blank=True, null=True)
    rg = models.CharField(max_length=40, null=True, blank=True, default="")
    cpf = models.CharField(max_length=40, null=True, blank=True, default="")
    endereco = models.CharField(max_length=255, null=True, blank=True)
    profissao = models.CharField(max_length=80, null=True, blank=True)
    estado_civil = models.CharField(
        max_length=50, choices=ESTADO_CHOICES, default="Solteiro(a)", null=True, blank=True)
    telefone = models.CharField(max_length=50, null=True, blank=True)
    dia_pagamento = models.IntegerField(default=5, blank=True, null=True)
    plano_pagamento = models.CharField(max_length=20,
                                       choices=PAGAMENTO_CHOICES,
                                       default="Mensal"
                                       )
    is_professor = models.BooleanField(default=False)
    professor = models.ForeignKey(
        User, null=True, blank=True, related_name="professor", on_delete=models.SET_NULL)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE)
    data_rematricula = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        ordering = ['user__first_name', ]

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
