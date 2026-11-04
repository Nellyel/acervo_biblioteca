from datetime import date
from rest_framework import serializers
from .models import Livro


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