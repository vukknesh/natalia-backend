from django.db.models import Q
from userprofile.models import Profile
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.serializers import ValidationError
from rest_framework.filters import (
    SearchFilter,
    OrderingFilter,
)
from rest_framework.decorators import api_view
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    UpdateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView
)
from rest_framework.pagination import LimitOffsetPagination
from datetime import datetime, timezone
from django.contrib.auth.models import User
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,

)
from django_filters import rest_framework as filters
from .models import Pagamento, AulaAvulsaGrupo, AulaExperimental, AulaPersonal, ResumoMensal


from .permissions import IsOwnerOrReadOnly

from .serializers import (
    PagamentoCreateUpdateSerializer,
    PagamentoDetailSerializer,
    PagamentoListSerializer,
    PagamentoListAllSerializer,
    ResumoMensalListAllSerializer,
    AulaAvulsaGrupoCreateUpdateSerializer,
    AulaExperimentalCreateUpdateSerializer,
    AulaPersonalCreateUpdateSerializer
)

import django_filters
from django.db.models import Q


class PagamentoFilter(filters.FilterSet):
    multi_name_fields = django_filters.CharFilter(
        method='filter_by_all_name_fields')

    class Meta:
        model = Pagamento
        fields = []

    def filter_by_all_name_fields(self, queryset, name, value):
        return queryset.filter(
            Q(city__icontains=value) | Q(address__icontains=value) | Q(
                state__icontains=value)
        )


class PagamentoCreateAPIView(CreateAPIView):
    queryset = Pagamento.objects.all()
    serializer_class = PagamentoCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AulaAvulsaGrupoCreateAPIView(CreateAPIView):
    queryset = AulaAvulsaGrupo.objects.all()
    serializer_class = AulaAvulsaGrupoCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.data['user']:
            id = self.request.data['user']
            print(f'id = {id}')
            u = User.objects.get(id=id)
        if u is None:
            u = User.objects.first()
        serializer.save(user=u)


class AulaExperimentalCreateAPIView(CreateAPIView):
    queryset = AulaExperimental.objects.all()
    serializer_class = AulaExperimentalCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.data['user']:
            id = self.request.data['user']
            print(f'id = {id}')
            u = User.objects.get(id=id)
        if u is None:
            u = User.objects.first()
        serializer.save(user=u)


class AulaPersonalCreateAPIView(CreateAPIView):
    queryset = AulaPersonal.objects.all()
    serializer_class = AulaPersonalCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.data['user']:
            id = self.request.data['user']
            print(f'id = {id}')
            u = User.objects.get(id=id)
        if u is None:
            u = User.objects.first()
        serializer.save(user=u)


class PagamentoDetailAPIView(RetrieveAPIView):
    queryset = Pagamento.objects.all()
    serializer_class = PagamentoDetailSerializer
    lookup_field = 'id'
    permission_classes = [AllowAny]
    # lookup_url_kwarg = "abc"


class PagamentoUpdateAPIView(UpdateAPIView):
    queryset = Pagamento.objects.all()
    serializer_class = PagamentoCreateUpdateSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]

    # def perform_update(self, serializer):
    #     pagamento_obj = self.get_object()
    #     print(f'pagamento_obj = {pagamento_obj}')

    #     instance = serializer.save()
    # pag_user = instance.user
    # todos_pag = Pagamento.objects.filter(
    #     user=pag_user, data__gt=instance.data)[:12]
    # print(f'todos_pag ={todos_pag}')
    # plano_pag = instance.user.profile.plano_pagamento

    # if(plano_pag == "Trimestral"):
    #     for pp in todos_pag[:2]:
    #         pp.pago = True
    #         pp.save()

    # if(plano_pag == "Semestral"):
    #     for pp in todos_pag[:5]:
    #         pp.pago = True
    #         pp.save()
    # if(plano_pag == "Anual"):
    #     for pp in todos_pag[:11]:
    #         pp.pago = True
    #         pp.save()

    # return instance


class PagamentoDeleteAPIView(DestroyAPIView):
    queryset = Pagamento.objects.all()
    serializer_class = PagamentoDetailSerializer
    lookup_field = 'id'
    permission_classes = [IsAdminUser]


class PagamentoListAPIView(ListAPIView):
    serializer_class = PagamentoListSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # this makes post method on listapiview
        return self.list(request, *args, **kwargs)

    def list(self, request):
        if request.data['user_id'] is not None:
            u = User.objects.get(id=request.data['user_id'])
        else:
            u = User.objects.first()

        qs = Pagamento.objects.all()
        queryset_list = Pagamento.objects.filter(
            user=u)

        return Response({"financeiros": PagamentoListSerializer(queryset_list, many=True).data})


class PagamentoListAllAPIView(ListAPIView):
    serializer_class = PagamentoListAllSerializer
    permission_classes = [AllowAny]

    def get_queryset(self, *args, **kwargs):

        queryset_list = Pagamento.objects.all()  # filter(user=self.request.user)

        return queryset_list


class ResumoMensalListAllAPIView(ListAPIView):
    serializer_class = ResumoMensalListAllSerializer
    permission_classes = [AllowAny]

    def get_queryset(self, *args, **kwargs):

        queryset_list = ResumoMensal.objects.all()  # filter(user=self.request.user)

        return queryset_list


@api_view(['GET'])
def get_resumo_mes(request):
    now = datetime.now(timezone.utc)
    year = now.year
    month = now.month

    valor_experimental = 50
    valor_avulsa_grupo = 60
    valor_personal = 120
    valor_matricula = 80
    valor_rematricula = 50

    total_experimental = AulaExperimental.objects.filter(data__year__gte=year,
                                                         data__month__gte=month,
                                                         data__year__lte=year,
                                                         data__month__lte=month).count() * valor_experimental

    total_avulsa = AulaAvulsaGrupo.objects.filter(data__year__gte=year,
                                                  data__month__gte=month,
                                                  data__year__lte=year,
                                                  data__month__lte=month).count() * valor_avulsa_grupo

    total_personal = AulaPersonal.objects.filter(data__year__gte=year,
                                                 data__month__gte=month,
                                                 data__year__lte=year,
                                                 data__month__lte=month).count() * valor_personal

    total_matricula = Profile.objects.filter(created_at__year__gte=year,
                                             created_at__month__gte=month,
                                             created_at__year__lte=year,
                                             created_at__month__lte=month).count() * valor_matricula

    total_rematricula = Profile.objects.filter(data_rematricula__year__gte=year,
                                               data_rematricula__month__gte=month,
                                               data_rematricula__year__lte=year,
                                               data_rematricula__month__lte=month).count() * valor_rematricula

    total_pagamento = 0

    for pagamento in Pagamento.objects.filter(data__year__gte=year, data__month__gte=month, data__year__lte=year, data__month__lte=month).filter(pago=True):
        total_pagamento += pagamento.valor
        # plano = pagamento.user.profile.plano
        # plano_pagamento = pagamento.user.profile.plano_pagamento
        # if (plano == "4 Aulas"):
        #     if(plano_pagamento == "Mensal"):
        #         valor = 180
        #     if(plano_pagamento == "Trimestral"):
        #         valor = 170
        #     if(plano_pagamento == "Semestral"):
        #         valor = 160
        #     if(plano_pagamento == "Anual"):
        #         valor = 150
        # if (plano == "8 Aulas"):
        #     if(plano_pagamento == "Mensal"):
        #         valor = 300
        #     if(plano_pagamento == "Trimestral"):
        #         valor = 280
        #     if(plano_pagamento == "Semestral"):
        #         valor = 260
        #     if(plano_pagamento == "Anual"):
        #         valor = 240
        # if (plano == "12 Aulas"):
        #     if(plano_pagamento == "Mensal"):
        #         valor = 420
        #     if(plano_pagamento == "Trimestral"):
        #         valor = 400
        #     if(plano_pagamento == "Semestral"):
        #         valor = 380
        #     if(plano_pagamento == "Anual"):
        #         valor = 360

    total_mes = total_experimental + total_avulsa + total_matricula + \
        total_pagamento + total_personal + total_rematricula

    return Response({
        "total_experimental": total_experimental,
        "total_avulsa": total_avulsa,
        "total_personal": total_personal,
        "total_matricula": total_matricula,
        "total_rematricula": total_rematricula,
        "total_pagamento": total_pagamento,
        "total_mes": total_mes
    })


def resumo_mensal():
    now = datetime.now(timezone.utc)
    year = now.year
    month = now.month

    valor_experimental = 50
    valor_avulsa_grupo = 60
    valor_personal = 120
    valor_matricula = 80
    valor_rematricula = 50

    total_experimental = AulaExperimental.objects.filter(data__year__gte=year,
                                                         data__month__gte=month,
                                                         data__year__lte=year,
                                                         data__month__lte=month).count() * valor_experimental

    total_avulsa = AulaAvulsaGrupo.objects.filter(data__year__gte=year,
                                                  data__month__gte=month,
                                                  data__year__lte=year,
                                                  data__month__lte=month).count() * valor_avulsa_grupo

    total_personal = AulaPersonal.objects.filter(data__year__gte=year,
                                                 data__month__gte=month,
                                                 data__year__lte=year,
                                                 data__month__lte=month).count() * valor_personal

    total_matricula = Profile.objects.filter(created_at__year__gte=year,
                                             created_at__month__gte=month,
                                             created_at__year__lte=year,
                                             created_at__month__lte=month).count() * valor_matricula

    total_rematricula = Profile.objects.filter(created_at__year__gte=year,
                                               created_at__month__gte=month,
                                               created_at__year__lte=year,
                                               created_at__month__lte=month).count() * valor_rematricula

    total_pagamento = 0

    for pagamento in Pagamento.objects.filter(data__year__gte=year, data__month__gte=month, data__year__lte=year, data__month__lte=month).filter(pago=True):
        total_pagamento += pagamento.valor
        # plano = pagamento.user.profile.plano
        # plano_pagamento = pagamento.user.profile.plano_pagamento
        # if (plano == "4 Aulas"):
        #     if(plano_pagamento == "Mensal"):
        #         valor = 180
        #     if(plano_pagamento == "Trimestral"):
        #         valor = 170
        #     if(plano_pagamento == "Semestral"):
        #         valor = 160
        #     if(plano_pagamento == "Anual"):
        #         valor = 150
        # if (plano == "8 Aulas"):
        #     if(plano_pagamento == "Mensal"):
        #         valor = 300
        #     if(plano_pagamento == "Trimestral"):
        #         valor = 280
        #     if(plano_pagamento == "Semestral"):
        #         valor = 260
        #     if(plano_pagamento == "Anual"):
        #         valor = 240
        # if (plano == "12 Aulas"):
        #     if(plano_pagamento == "Mensal"):
        #         valor = 420
        #     if(plano_pagamento == "Trimestral"):
        #         valor = 400
        #     if(plano_pagamento == "Semestral"):
        #         valor = 380
        #     if(plano_pagamento == "Anual"):
        #         valor = 360

    total_mes = total_experimental + total_avulsa + total_matricula + \
        total_pagamento + total_personal + total_rematricula

    ResumoMensal.objects.create(total_experimental=total_experimental, total_avulsa=total_avulsa, total_personal=total_personal,
                                total_matricula=total_matricula, total_rematricula=total_rematricula, total_pagamento=total_pagamento, total_mes=total_mes)


@api_view(['GET'])
def get_pagamento_professor(request):
    now = datetime.now(timezone.utc)
    year = now.year
    month = now.month

    list_prof = []
    list_prof_rend = []
    for prof in Profile.objects.filter(is_professor=True):
        u = prof.user
        list_prof.append(u.first_name)
        valor_acumulado = 0
        for pr in u.professor.all():
            valor = 0
            plano = pr.user.profile.plano
            plano_pagamento = pr.user.profile.plano_pagamento
            if (plano == "4 Aulas"):
                if(plano_pagamento == "Mensal"):
                    valor = 180
                if(plano_pagamento == "Trimestral"):
                    valor = 170
                if(plano_pagamento == "Semestral"):
                    valor = 160
                if(plano_pagamento == "Anual"):
                    valor = 150
            if (plano == "8 Aulas"):
                if(plano_pagamento == "Mensal"):
                    valor = 300
                if(plano_pagamento == "Trimestral"):
                    valor = 280
                if(plano_pagamento == "Semestral"):
                    valor = 260
                if(plano_pagamento == "Anual"):
                    valor = 240
            if (plano == "12 Aulas"):
                if(plano_pagamento == "Mensal"):
                    valor = 420
                if(plano_pagamento == "Trimestral"):
                    valor = 400
                if(plano_pagamento == "Semestral"):
                    valor = 380
                if(plano_pagamento == "Anual"):
                    valor = 360
            valor_acumulado += valor
        list_prof_rend.append(valor_acumulado)
        print(f'lista_prof {list_prof}')
        print(f'lista_prof_rend {list_prof_rend}')
    resposta = dict(zip(list_prof, list_prof_rend))
    return Response({
        "professores": list_prof,
        "alunos": list_prof_rend,
        "resposta": resposta,
    })
