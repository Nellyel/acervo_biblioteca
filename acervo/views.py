from django.shortcuts import render, redirect
from .models import Livro
from .forms import LivroForm, PeriodoForm, filtrar_periodo
from django.contrib.auth.decorators import login_required
from .models import Livro, Emprestimo
from .dashboard import calcular_metricas
import csv
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

def org_atual(request):
    if not hasattr(request.user, 'perfil'):
        raise PermissionDenied

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
    if not hasattr(request.user, 'perfil') or not request.user.perfil.eh_admin:
        raise PermissionDenied

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

@login_required
def dashboard(request):
    org = org_atual(request)

    base = filtrar_periodo(
        request,
        Emprestimo.objects.filter(organizacao=org)
    )

    contexto = calcular_metricas(base)
    contexto['form'] = PeriodoForm(request.GET)
    contexto['mostra_series'] = request.user.perfil.eh_admin

    return render(
        request,
        'acervo/dashboard.html',
        contexto
    )

@login_required
def exportar_csv(request):
    org = org_atual(request)

    if not request.user.perfil.eh_admin:
        raise PermissionDenied

    qs = filtrar_periodo(
        request,
        Emprestimo.objects.filter(
            organizacao=org
        ).select_related(
            'exemplar__livro',
            'membro'
        )
    )

    resposta = HttpResponse(
        content_type='text/csv; charset=utf-8'
    )

    resposta['Content-Disposition'] = (
        'attachment; filename="emprestimos.csv"'
    )

    writer = csv.writer(resposta)

    writer.writerow([
        'Livro',
        'Membro',
        'Data do empréstimo',
        'Data prevista',
        'Data devolução',
    ])

    for emprestimo in qs:
        writer.writerow([
            emprestimo.exemplar.livro.titulo,
            emprestimo.membro.nome,
            emprestimo.data_emprestimo,
            emprestimo.data_prevista,
            emprestimo.data_devolucao or '',
        ])

    return resposta
