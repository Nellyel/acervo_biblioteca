from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, BasePermission, SAFE_METHODS
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.db.models import ProtectedError
from rest_framework.views import APIView
from rest_framework.response import Response
from .dashboard import calcular_metricas
from .forms import filtrar_periodo

from .models import Livro, Autor, Exemplar, Membro, Emprestimo, Reserva

from .serializers import (
    LivroSerializer,
    AutorSerializer,
    ExemplarSerializer,
    MembroSerializer,
    EmprestimoSerializer,
    ReservaSerializer
)


def obter_organizacao(user):
    if not hasattr(user, 'perfil'):
        raise PermissionDenied(
            'Usuário sem perfil cadastrado.'
        )

    return user.perfil.organizacao


class PermissaoAcervo(BasePermission):

    def has_permission(self, request, view):
        if not hasattr(request.user, 'perfil'):
            return False

        if request.method in SAFE_METHODS:
            return True

        return request.user.perfil.eh_admin


class BaseListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, PermissaoAcervo]

    def get_queryset(self):
        org = obter_organizacao(self.request.user)
        return self.serializer_class.Meta.model.objects.filter(
            organizacao=org
        )

    def perform_create(self, serializer):
        org = obter_organizacao(self.request.user)
        serializer.save(organizacao=org)


class BaseDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, PermissaoAcervo]

    def get_queryset(self):
        org = obter_organizacao(self.request.user)
        return self.serializer_class.Meta.model.objects.filter(
            organizacao=org
        )

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError:
            raise ValidationError(
                'Este registro possui vínculos e não pode ser excluído.'
            )


class LivroListCreate(BaseListCreate):
    serializer_class = LivroSerializer


class LivroDetail(BaseDetail):
    serializer_class = LivroSerializer


class AutorListCreate(BaseListCreate):
    serializer_class = AutorSerializer


class AutorDetail(BaseDetail):
    serializer_class = AutorSerializer


class ExemplarListCreate(BaseListCreate):
    serializer_class = ExemplarSerializer


class ExemplarDetail(BaseDetail):
    serializer_class = ExemplarSerializer


class MembroListCreate(BaseListCreate):
    serializer_class = MembroSerializer


class MembroDetail(BaseDetail):
    serializer_class = MembroSerializer


class EmprestimoListCreate(BaseListCreate):
    serializer_class = EmprestimoSerializer


class EmprestimoDetail(BaseDetail):
    serializer_class = EmprestimoSerializer

    def perform_destroy(self, instance):
        if not instance.data_devolucao:
            raise ValidationError(
                'Devolva o exemplar antes de excluir o empréstimo.'
            )

        super().perform_destroy(instance)


class ReservaListCreate(BaseListCreate):
    serializer_class = ReservaSerializer


class ReservaDetail(BaseDetail):
    serializer_class = ReservaSerializer

class DashboardApi(APIView):
    permission_classes = [IsAuthenticated, PermissaoAcervo]

    def get(self, request):
        org = obter_organizacao(request.user)

        base = filtrar_periodo(
            request,
            Emprestimo.objects.filter(organizacao=org)
        )

        dados = calcular_metricas(base)
        dados['ranking'] = list(dados['ranking'])

        if not request.user.perfil.eh_admin:
            dados.pop('serie', None)

        return Response(dados)