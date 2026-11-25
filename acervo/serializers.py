from datetime import date
from rest_framework import serializers
from .models import Livro, Autor, Exemplar, Membro, Emprestimo, Reserva


class SerializerDaOrganizacao(serializers.ModelSerializer):

    def get_fields(self):
        fields = super().get_fields()

        request = self.context.get('request')
        user = getattr(request, 'user', None)
        perfil = getattr(user, 'perfil', None)

        for nome in ('livro', 'membro', 'exemplar'):
            if nome in fields:
                campo = fields[nome]

                if perfil:
                    campo.queryset = campo.queryset.filter(
                        organizacao=perfil.organizacao
                    )
                else:
                    campo.queryset = campo.queryset.none()

        return fields


class LivroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Livro
        fields = [
            'id',
            'titulo',
            'autor',
            'ano',
            'tipo_acervo',
            'categoria',
        ]

    def validate_ano(self, value):
        if value > date.today().year:
            raise serializers.ValidationError(
                'O ano de publicação não pode estar no futuro.'
            )

        return value


class AutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Autor
        fields = ['id', 'nome']


class ExemplarSerializer(SerializerDaOrganizacao):
    class Meta:
        model = Exemplar
        fields = ['id', 'livro', 'codigo', 'disponivel']
        read_only_fields = ['disponivel']


class MembroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membro
        fields = ['id', 'nome', 'email', 'ativo']


class EmprestimoSerializer(SerializerDaOrganizacao):
    data_emprestimo = serializers.DateField(default=date.today)
    dias_atraso = serializers.ReadOnlyField()
    valor_multa = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Emprestimo
        fields = [
            'id',
            'membro',
            'exemplar',
            'data_emprestimo',
            'data_prevista',
            'data_devolucao',
            'dias_atraso',
            'valor_multa',
        ]

    def validate(self, attrs):
        exemplar = attrs.get(
            'exemplar', getattr(self.instance, 'exemplar', None)
        )

        if self.instance and exemplar != self.instance.exemplar:
            raise serializers.ValidationError(
                'Não é permitido trocar o exemplar do empréstimo.'
            )

        abertos = Emprestimo.objects.filter(
            exemplar=exemplar,
            data_devolucao__isnull=True
        )

        if self.instance:
            abertos = abertos.exclude(pk=self.instance.pk)

        if abertos.exists():
            raise serializers.ValidationError(
                'Este exemplar possui outro empréstimo em aberto.'
            )

        return attrs


class ReservaSerializer(SerializerDaOrganizacao):
    posicao_fila = serializers.ReadOnlyField()

    class Meta:
        model = Reserva
        fields = [
            'id',
            'membro',
            'livro',
            'data_reserva',
            'atendida',
            'posicao_fila',
        ]