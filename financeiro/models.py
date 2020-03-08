from __future__ import unicode_literals
from django.utils import timezone

from datetime import datetime
from django.conf import settings
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save


class Pagamento(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             on_delete=models.CASCADE)
    pago = models.BooleanField(default=False)
    plano_pagamento = models.CharField(
        max_length=50, default='', null=True, blank=True)
    valor = models.FloatField(default=0.0)
    data = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['data']

    def __str__(self):
        return f'{self.user} - {self.data}'


class AulaExperimental(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             on_delete=models.CASCADE)
    data = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.user} - {self.data}'


class AulaAvulsaGrupo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             on_delete=models.CASCADE)
    data = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.user} - {self.data}'


class AulaPersonal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             on_delete=models.CASCADE)
    data = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.user} - {self.data}'


class Item(models.Model):
    nome = models.CharField(max_length=255, default='', null=True, blank=True)
    descricao = models.CharField(
        max_length=255, default='', null=True, blank=True)
    valor = models.FloatField(default=0.0)
    cod = models.CharField(max_length=255, default='', null=True, blank=True)
    estoque = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return f'{self.nome} - {self.valor} - {self.cod} - estoque {self.estoque}'


class VendaItems(models.Model):
    data = models.DateTimeField(auto_now_add=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             on_delete=models.CASCADE)
    quant = models.IntegerField()

    def __str__(self):
        return f'{self.item.nome} - {self.item.valor} - {self.user.first_name}'


class ResumoMensal(models.Model):
    data = models.DateTimeField(auto_now_add=True)
    total_itens = models.FloatField(default=0.0)
    total_experimental = models.IntegerField()
    total_avulsa = models.IntegerField()
    total_personal = models.IntegerField()
    total_matricula = models.IntegerField()
    total_rematricula = models.IntegerField()
    total_pagamento = models.IntegerField()
    total_mes = models.IntegerField()

    def __str__(self):
        return f'{self.total_mes} - {self.data}'
