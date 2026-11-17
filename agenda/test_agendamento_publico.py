from datetime import datetime, timedelta
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Agendamento, Servico


@override_settings(TIME_ZONE='America/Sao_Paulo')
class AgendamentoPublicoTests(TestCase):
    def setUp(self):
        agora = timezone.make_aware(
            datetime(2026, 11, 3, 8),
            timezone.get_default_timezone(),
        )

        mock_agora = patch(
            'django.utils.timezone.now',
            return_value=agora,
        )
        mock_agora.start()
        self.addCleanup(mock_agora.stop)

        self.servico = Servico.objects.create(
            nome='Corte',
            preco='40.00',
            duracao_minutos=30,
            ativo=True,
        )

        self.url = reverse('agenda:agendar')

    def dados_validos(self):
        return {
            'nome_cliente': 'Cliente teste',
            'telefone': '11999999999',
            'servico': str(self.servico.pk),
            'inicio_0': '2026-11-04',
            'inicio_1': '09:00:00',
        }

    def criar_agendamento(self):
        inicio = timezone.make_aware(
            datetime(2026, 11, 4, 9),
            timezone.get_default_timezone(),
        )

        agendamento = Agendamento(
            nome_cliente='Cliente existente',
            telefone='11988888888',
            servico=self.servico,
            inicio=inicio,
        )
        agendamento.full_clean()
        agendamento.save()

        return agendamento

    def test_consulta_nao_cria_agendamento(self):
        resposta = self.client.get(
            self.url,
            {
                'servico': self.servico.pk,
                'data': '2026-11-04',
            },
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertIsNotNone(resposta.context['formulario'])
        self.assertIn(
            ('09:00:00', '09:00'),
            resposta.context['formulario'].horarios_disponiveis,
        )
        self.assertEqual(Agendamento.objects.count(), 0)

    def test_confirma_agendamento_sem_duplicar_ao_atualizar(self):
        resposta = self.client.post(
            self.url,
            self.dados_validos(),
        )

        self.assertRedirects(
            resposta,
            self.url,
            fetch_redirect_response=False,
        )

        agendamento = Agendamento.objects.get()

        self.assertEqual(agendamento.nome_cliente, 'Cliente teste')
        self.assertEqual(
            agendamento.situacao,
            Agendamento.Situacao.AGENDADO,
        )
        self.assertEqual(
            agendamento.fim,
            agendamento.inicio + timedelta(minutes=30),
        )

        confirmacao = self.client.get(self.url)

        self.assertEqual(
            confirmacao.context['confirmacao'],
            {
                'servico': 'Corte',
                'data': '04/11/2026',
                'horario': '09:00',
            },
        )

        atualizacao = self.client.get(self.url)

        self.assertIsNone(atualizacao.context['confirmacao'])
        self.assertEqual(Agendamento.objects.count(), 1)

    def test_recusa_horario_ocupado_depois_da_consulta(self):
        self.client.get(
            self.url,
            {
                'servico': self.servico.pk,
                'data': '2026-11-04',
            },
        )

        existente = self.criar_agendamento()

        resposta = self.client.post(
            self.url,
            self.dados_validos(),
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(
            'inicio',
            resposta.context['formulario'].errors,
        )
        self.assertEqual(Agendamento.objects.count(), 1)
        self.assertEqual(Agendamento.objects.get().pk, existente.pk)

    def test_recusa_servico_desativado_depois_da_consulta(self):
        self.client.get(
            self.url,
            {
                'servico': self.servico.pk,
                'data': '2026-11-04',
            },
        )

        self.servico.ativo = False
        self.servico.save()

        resposta = self.client.post(
            self.url,
            self.dados_validos(),
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(
            'servico',
            resposta.context['formulario'].errors,
        )
        self.assertEqual(Agendamento.objects.count(), 0)

    def test_recusa_campos_obrigatorios_vazios(self):
        dados = self.dados_validos()
        dados['nome_cliente'] = ''
        dados['telefone'] = ''

        resposta = self.client.post(self.url, dados)

        self.assertEqual(resposta.status_code, 200)

        erros = resposta.context['formulario'].errors

        self.assertIn('nome_cliente', erros)
        self.assertIn('telefone', erros)
        self.assertEqual(Agendamento.objects.count(), 0)

    def test_consulta_com_data_invalida_exibe_erro(self):
        resposta = self.client.get(
            self.url,
            {
                'servico': self.servico.pk,
                'data': 'data-invalida',
            },
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertIn('data', resposta.context['consulta'].errors)
        self.assertIsNone(resposta.context['formulario'])
        self.assertEqual(Agendamento.objects.count(), 0)

    def test_cliente_nao_consegue_definir_situacao(self):
        dados = self.dados_validos()
        dados['situacao'] = Agendamento.Situacao.CONCLUIDO

        resposta = self.client.post(self.url, dados)

        self.assertRedirects(
            resposta,
            self.url,
            fetch_redirect_response=False,
        )
        self.assertEqual(
            Agendamento.objects.get().situacao,
            Agendamento.Situacao.AGENDADO,
        )