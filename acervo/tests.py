from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from core.models import Organizacao, Perfil
from .models import Livro, Exemplar, Membro, Emprestimo, Reserva
from datetime import date
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

class LivroAPITest(APITestCase):

    def test_usuario_nao_autenticado(self):
        resposta = self.client.get('/api/livros/')
        self.assertEqual(resposta.status_code, 403)

    def test_usuario_sem_perfil(self):
        usuario = User.objects.create_user(
            username='TesteSemPerfil'
        )

        self.client.force_authenticate(user=usuario)

        resposta = self.client.get('/api/livros/')
        self.assertEqual(resposta.status_code, 403)

    def test_isolamento_organizacoes(self):
        org_a = Organizacao.objects.create(nome='Biblioteca A')
        org_b = Organizacao.objects.create(nome='Biblioteca B')

        usuario = User.objects.create_user(username='AuroraTeste')

        Perfil.objects.create(
            usuario=usuario,
            organizacao=org_a,
            papel='admin'
        )

        livro = Livro.objects.create(
            organizacao=org_b,
            titulo='Livro Restrito',
            autor='Sayaka',
            ano=2025,
            tipo_acervo='digital',
            categoria='800'
        )

        self.client.force_authenticate(user=usuario)

        resposta = self.client.get(f'/api/livros/{livro.id}/')

        self.assertEqual(resposta.status_code, 404)

    def test_permissoes_por_papel(self):
        org = Organizacao.objects.create(nome='Biblioteca A')

        usuario = User.objects.create_user(username='SayakaTeste')

        perfil = Perfil.objects.create(
            usuario=usuario,
            organizacao=org,
            papel='operador'
        )

        livro = Livro.objects.create(
            organizacao=org,
            titulo='Abismo da Consciência',
            autor='Sayaka',
            ano=2026,
            tipo_acervo='digital',
            categoria='800'
        )

        self.client.force_authenticate(user=usuario)

        url = f'/api/livros/{livro.id}/'

        resposta = self.client.patch(
            url, {'ano': 2025}, format='json'
        )

        self.assertEqual(resposta.status_code, 403)

        perfil.papel = 'admin'
        perfil.save()

        resposta = self.client.patch(
            url, {'ano': 2025}, format='json'
        )

        self.assertEqual(resposta.status_code, 200)

    def test_ano_futuro(self):
        org = Organizacao.objects.create(nome='Biblioteca A')

        usuario = User.objects.create_user(username='AuroraTeste')

        Perfil.objects.create(
            usuario=usuario,
            organizacao=org,
            papel='admin'
        )

        self.client.force_authenticate(user=usuario)

        resposta = self.client.post(
            '/api/livros/',
            {
                'titulo': 'Raízes de Identidade',
                'autor': 'Shiori Amagi',
                'ano': date.today().year + 1,
                'tipo_acervo': 'digital',
                'categoria': '800'
            },
            format='json'
        )

        self.assertEqual(resposta.status_code, 400)
        self.assertIn('ano', resposta.data)

    def test_disponibilidade_exemplar(self):
        org = Organizacao.objects.create(nome='Biblioteca A')

        livro = Livro.objects.create(
            organizacao=org,
            titulo='Ameaça Carmesim',
            autor='Aurora',
            ano=2026,
            tipo_acervo='fisico',
            categoria='800'
        )

        exemplar = Exemplar.objects.create(
            organizacao=org,
            livro=livro,
            codigo='AC-001',
            disponivel=True
        )

        membro = Membro.objects.create(
            organizacao=org,
            nome='Takeshi'
        )

        emprestimo = Emprestimo.objects.create(
            organizacao=org,
            membro=membro,
            exemplar=exemplar,
            data_emprestimo=date.today(),
            data_prevista=date.today()
        )

        exemplar.refresh_from_db()
        self.assertFalse(exemplar.disponivel)

        emprestimo.data_devolucao = date.today()
        emprestimo.save()

        exemplar.refresh_from_db()
        self.assertTrue(exemplar.disponivel)

    def test_calculo_multa(self):
        emprestimo = Emprestimo(
            data_emprestimo=date(2026, 11, 10),
            data_prevista=date(2026, 11, 16),
            data_devolucao=date(2026, 11, 19)
        )

        self.assertEqual(emprestimo.dias_atraso(), 3)
        self.assertEqual(emprestimo.valor_multa(), Decimal('3.00'))

        emprestimo.data_devolucao = date(2026, 11, 16)

        self.assertEqual(emprestimo.dias_atraso(), 0)
        self.assertEqual(emprestimo.valor_multa(), Decimal('0.00'))

    def test_fila_reservas(self):
        org = Organizacao.objects.create(nome='Biblioteca A')

        livro = Livro.objects.create(
            organizacao=org,
            titulo='Ameaça Carmesim',
            autor='Aurora',
            ano=2026,
            tipo_acervo='fisico',
            categoria='800'
        )

        membro1 = Membro.objects.create(
            organizacao=org,
            nome='Takeshi'
        )

        membro2 = Membro.objects.create(
            organizacao=org,
            nome='Aurora'
        )

        agora = timezone.now()

        reserva1 = Reserva.objects.create(
            organizacao=org,
            membro=membro1,
            livro=livro,
            data_reserva=agora
        )

        reserva2 = Reserva.objects.create(
            organizacao=org,
            membro=membro2,
            livro=livro,
            data_reserva=agora + timedelta(minutes=1)
        )

        self.assertEqual(reserva1.posicao_fila(), 1)
        self.assertEqual(reserva2.posicao_fila(), 2)

        reserva1.atendida = True
        reserva1.save()

        self.assertEqual(reserva1.posicao_fila(), '-')
        self.assertEqual(reserva2.posicao_fila(), 1)

    def test_novos_endpoints(self):
        org = Organizacao.objects.create(nome='Biblioteca Teste')

        usuario = User.objects.create_user(username='AdminTeste')

        perfil = Perfil.objects.create(
            usuario=usuario,
            organizacao=org,
            papel='admin'
        )

        livro = Livro.objects.create(
            organizacao=org,
            titulo='Ameaça Carmesim',
            autor='Aurora',
            ano=2025,
            tipo_acervo='fisico',
            categoria='800'
        )

        self.client.force_authenticate(user=usuario)

        recursos = [
            ('autores', {'nome': 'Aurora'}),
            ('exemplares', {'livro': livro.id, 'codigo': 'AC-001'}),
            ('membros', {
                'nome': 'Takeshi',
                'email': 'takeshi@example.com',
                'ativo': True
            }),
        ]

        registros = {}

        for recurso, dados in recursos:
            url = f'/api/{recurso}/'

            resposta = self.client.post(url, dados, format='json')

            self.assertEqual(
                resposta.status_code, 201, resposta.data
            )

            registros[recurso] = resposta.data['id']

        recursos = [
            ('emprestimos', {
                'membro': registros['membros'],
                'exemplar': registros['exemplares'],
                'data_emprestimo': date.today().isoformat(),
                'data_prevista': date.today().isoformat()
            }),
            ('reservas', {
                'membro': registros['membros'],
                'livro': livro.id
            }),
        ]

        for recurso, dados in recursos:
            resposta = self.client.post(
                f'/api/{recurso}/', dados, format='json'
            )

            self.assertEqual(
                resposta.status_code, 201, resposta.data
            )

            registros[recurso] = resposta.data['id']

        for recurso, pk in registros.items():
            resposta = self.client.get(f'/api/{recurso}/')
            self.assertEqual(resposta.status_code, 200)

            resposta = self.client.get(f'/api/{recurso}/{pk}/')
            self.assertEqual(resposta.status_code, 200)

        perfil.papel = 'operador'
        perfil.save()

        for recurso, pk in registros.items():
            resposta = self.client.get(f'/api/{recurso}/{pk}/')
            self.assertEqual(resposta.status_code, 200)

            resposta = self.client.patch(
                f'/api/{recurso}/{pk}/', {}, format='json'
            )
            self.assertEqual(resposta.status_code, 403)

            resposta = self.client.delete(f'/api/{recurso}/{pk}/')
            self.assertEqual(resposta.status_code, 403)

        perfil.papel = 'admin'
        perfil.save()

        alteracoes = {
            'autores': {'nome': 'Aurora Haruyoki'},
            'exemplares': {'codigo': 'AC-002'},
            'membros': {'nome': 'Takeshi Haruyoki'},
            'emprestimos': {
                'data_devolucao': date.today().isoformat()
            },
            'reservas': {'atendida': True},
        }

        for recurso, dados in alteracoes.items():
            pk = registros[recurso]

            resposta = self.client.patch(
                f'/api/{recurso}/{pk}/', dados, format='json'
            )

            self.assertEqual(
                resposta.status_code, 200, resposta.data
            )

        for recurso, pk in reversed(list(registros.items())):
            resposta = self.client.delete(f'/api/{recurso}/{pk}/')
            self.assertEqual(resposta.status_code, 204)

    def test_dashboard_metricas(self):
        org = Organizacao.objects.create(nome='Biblioteca A')
        usuario = User.objects.create_user(username='AdminDashboard')

        Perfil.objects.create(
            usuario=usuario,
            organizacao=org,
            papel='admin'
        )

        self.client.force_authenticate(user=usuario)
        resposta = self.client.get('/api/dashboard/')

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.data['kpi']['total'], 0)
        self.assertEqual(resposta.data['ranking'], [])
        self.assertEqual(resposta.data['serie'], [])
        self.assertEqual(
            resposta.data['distribuicao']['abertos'], 0
        )
        self.assertEqual(
            resposta.data['distribuicao']['devolvidos'], 0
        )

    def test_dashboard_operador(self):
        org = Organizacao.objects.create(nome='Biblioteca B')
        usuario = User.objects.create_user(username='OperadorDashboard')

        Perfil.objects.create(
            usuario=usuario,
            organizacao=org,
            papel='operador'
        )

        self.client.force_authenticate(user=usuario)
        resposta = self.client.get('/api/dashboard/')

        self.assertEqual(resposta.status_code, 200)
        self.assertIn('kpi', resposta.data)
        self.assertIn('ranking', resposta.data)
        self.assertNotIn('serie', resposta.data)