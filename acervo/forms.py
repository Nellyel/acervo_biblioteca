from django import forms
from .models import Livro
from datetime import date

class LivroForm(forms.ModelForm):
    class Meta:
        
        model = Livro
        fields = [
            'titulo',
            'autor',
            'ano',
            'tipo_acervo',
            'categoria',
        ]
        
    def clean_ano(self):
        ano = self.cleaned_data.get('ano')
    
        if ano and ano > date.today().year:
            raise forms.ValidationError(
                'O ano de publicação não pode estar no futuro.'
            )
            
        return ano