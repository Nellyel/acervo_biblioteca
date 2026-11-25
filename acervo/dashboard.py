from django.db.models import Count, Q
from django.db.models.functions import TruncMonth


def calcular_metricas(base):
    kpi = base.aggregate(
        total=Count('id')
    )

    ranking = (
        base
        .values('exemplar__livro__titulo')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )

    serie_qs = (
        base
        .annotate(mes=TruncMonth('data_emprestimo'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    serie = [
        {
            'mes': item['mes'].strftime('%Y-%m'),
            'total': item['total']
        }
        for item in serie_qs
    ]

    distribuicao = base.aggregate(
        abertos=Count(
            'id',
            filter=Q(data_devolucao__isnull=True)
        ),
        devolvidos=Count(
            'id',
            filter=Q(data_devolucao__isnull=False)
        ),
    )

    return {
        'kpi': kpi,
        'ranking': ranking,
        'serie': serie,
        'distribuicao': distribuicao,
    }