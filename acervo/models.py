from django.db import models
from core.models import DaOrganizacao
from django.utils import timezone
from decimal import Decimal

class Autor(DaOrganizacao):
    nome = models.CharField(max_length=120)

    def __str__(self):
        return self.nome

class Livro(DaOrganizacao):

    TIPO_ACERVO = [
        ('digital', 'Digital'),
        ('fisico', 'fisico'),
    ]

    CATEGORIA = [
        ('000', 'Generalidades'),
        ('100', 'Filosofia e Psicologia'),
        ('200', 'Religião e Teologia'),
        ('300', 'Ciências Sociais e Direito'),
        ('400', 'Linguística e Idiomas'),
        ('500', 'Ciências Puras'),
        ('600', 'Ciências Aplicadas'),
        ('700', 'Artes e Recreção'),
        ('800', 'Literatura'),
        ('900', 'História e Geografia'),
    ]

    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=100)
    ano = models.IntegerField()

    tipo_acervo = models.CharField(max_length=10, choices=TIPO_ACERVO)
    categoria = models.CharField(max_length=3, choices=CATEGORIA)

    def __str__(self):
        return self.titulo

class Exemplar(DaOrganizacao):
    livro = models.ForeignKey(
        Livro,
        on_delete=models.CASCADE,
        related_name='exemplares'
    )
    codigo = models.CharField(max_length=50)
    disponivel = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Exemplar'
        verbose_name_plural = 'Exemplares'

    def __str__(self):
        return f"{self.livro.titulo} - {self.codigo}"

class Membro(DaOrganizacao):
    nome = models.CharField(max_length=120)
    email = models.EmailField()
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

class Emprestimo(DaOrganizacao):
    membro = models.ForeignKey(
        Membro,
        on_delete=models.PROTECT,
        related_name='emprestimos'
    )

    exemplar = models.ForeignKey(
        Exemplar,
        on_delete=models.PROTECT,
        related_name='emprestimos'
    )

    data_emprestimo = models.DateField(default=timezone.now)
    data_prevista = models.DateField()
    data_devolucao = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.membro.nome} - {self.exemplar}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.data_devolucao:
            self.exemplar.disponivel = True
        else:
            self.exemplar.disponivel = False

        self.exemplar.save()

    def dias_atraso(self):
        data_final = self.data_devolucao or timezone.now().date()

        if data_final > self.data_prevista:
            return (data_final - self.data_prevista).days

        return 0

    def valor_multa(self):
        return Decimal('1.00') * self.dias_atraso()

class Reserva(DaOrganizacao):
    membro = models.ForeignKey(
        Membro,
        on_delete=models.PROTECT,
        related_name='reservas'
    )

    livro = models.ForeignKey(
        Livro,
        on_delete=models.PROTECT,
        related_name='reservas'
    )

    data_reserva = models.DateTimeField(default=timezone.now)
    atendida = models.BooleanField(default=False)

    def posicao_fila(self):
        if self.atendida:
            return '-'

        anteriores = Reserva.objects.filter(
            organizacao=self.organizacao,
            livro=self.livro,
            atendida=False,
            data_reserva__lt=self.data_reserva
        ).count()

        return anteriores + 1

    def __str__(self):
        return f"{self.membro.nome} - {self.livro.titulo}"