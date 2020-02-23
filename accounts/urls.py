from django.urls import path, include
from .api import RegisterAPI, LoginAPI, UserAPI, RegisterWithPlano, add_aulas_por_aluno, add_pagamentos_por_aluno, get_pagamentos_retroativo
from knox import views as knox_views
from django.conf.urls import url

urlpatterns = [
    path('api/auth', include('knox.urls')),
    path('api/auth/register', RegisterAPI.as_view()),
    path('api/auth/login', LoginAPI.as_view()),
    path('api/auth/user', UserAPI.as_view()),
    path('api/auth/cadastrar-aluno', RegisterWithPlano.as_view(), name='cadastrar'),
    path('api/auth/add-aulas', add_aulas_por_aluno, name='add-aulas'),
    url(r'^api/pagamento-retroativo/(?P<user_id>[\w-]+)$',
        get_pagamentos_retroativo, name='pagamento-retroativo'),
    path('api/auth/add-pagamentos',
         add_pagamentos_por_aluno, name='add-pagamentos'),
    path('api/auth/logout', knox_views.LogoutView.as_view(), name='knox_logout'),


]
