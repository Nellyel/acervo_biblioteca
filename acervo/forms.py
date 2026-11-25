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

class PeriodoForm(forms.Form):
    inicio = forms.DateField(required=False)
    fim = forms.DateField(required=False)


def filtrar_periodo(request, qs):
    form = PeriodoForm(request.GET)

    if form.is_valid():
        if form.cleaned_data['inicio']:
            qs = qs.filter(
                data_emprestimo__gte=form.cleaned_data['inicio']
            )

        if form.cleaned_data['fim']:
            qs = qs.filter(
                data_emprestimo__lte=form.cleaned_data['fim']
            )

    return qs