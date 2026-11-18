from django.shortcuts import render, redirect
from .models import Livro
from .forms import LivroForm
from django.contrib.auth.decorators import login_required


def org_atual(request):
    return request.user.perfil.organizacao


@login_required
def lista_livros(request):
    org = org_atual(request)
    livros = Livro.objects.filter(organizacao=org)

    nome = request.GET.get('nome', '')
    tipo = request.GET.get('tipo', '')
    categoria = request.GET.get('categoria', '')

    if nome:
        livros = livros.filter(titulo__icontains=nome)

    if tipo:
        livros = livros.filter(tipo_acervo=tipo)

    if categoria:
        livros = livros.filter(categoria=categoria)

    return render(request, 'acervo/lista.html', {
        'livros': livros,
        'tipos_acervo': Livro.TIPO_ACERVO,
        'categorias': Livro.CATEGORIA,
    })


@login_required
def novo_livro(request):
    if request.method == 'POST':
        form = LivroForm(request.POST)

        if form.is_valid():
            livro = form.save(commit=False)
            livro.organizacao = org_atual(request)
            livro.save()
            return redirect('lista')

    else:
        form = LivroForm()

    return render(request, 'acervo/form.html', {'form': form})