from django.conf.urls import url, include
from .views import (UserViewSet, ProfileViewSet,
                    ProfileUpdateAPIView, ProfessorListAllAPIView, AniversariantesListApiView)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'profiles', ProfileViewSet)


urlpatterns = [


    url(r'^api/', include(router.urls)),
    url(r'^api/profiles/(?P<id>[\w-]+)/update/$',
        ProfileUpdateAPIView.as_view(), name='update'),
    url(r'^api/professores/$',
        ProfessorListAllAPIView.as_view(), name='professores'),
    url(r'^api/aniversariantes/$',
        AniversariantesListApiView.as_view(), name='get-aniversariantes'),

]
