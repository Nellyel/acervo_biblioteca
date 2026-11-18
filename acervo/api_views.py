from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Livro
from .serializers import LivroSerializer


class LivroListCreate(generics.ListCreateAPIView):
    serializer_class = LivroSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        org = self.request.user.perfil.organizacao
        return Livro.objects.filter(organizacao=org)

    def perform_create(self, serializer):
        org = self.request.user.perfil.organizacao
        serializer.save(organizacao=org)


class LivroDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LivroSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        org = self.request.user.perfil.organizacao
        return Livro.objects.filter(organizacao=org)