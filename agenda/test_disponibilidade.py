from datetime import datetime, time

from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch

from .disponibilidade import listar_horarios_disponiveis
from .models import Agendamento, Servico


class DisponibilidadeTests(TestCase):
    def setUp(self):
        self.agora = timezone.make_aware(
            datetime(2026, 11, 3, 8, 0),
            timezone.get_default_timezone(),
        )

        mock_agora = patch(
            'agenda.regras.timezone.now',
            return_value=self.agora,
        )
        mock_agora.start()
        self.addCleanup(mock_agora.stop)

        self.servico = Servico.objects.create(
            nome='Corte',
            preco='40.00',
            duracao_minutos=30,
            ativo=True,
        )

        self.data = datetime(2026, 11, 3).date()

    def horario(self, hora, minuto=0):
        return timezone.make_aware(
            datetime.combine(self.data, time(hora, minuto)),
            timezone.get_default_timezone(),
        )

    def criar_agendamento(self, inicio, fim, situacao):
        return Agendamento.objects.create(
            nome_cliente='Cliente teste',
            telefone='11999999999',
            servico=self.servico,
            inicio=inicio,
            fim=fim,
            situacao=situacao,
        )

    def textos_dos_horarios(self, servico=None, data=None):
        servico = servico or self.servico
        data = data or self.data

        return {
            texto
            for valor, texto in listar_horarios_disponiveis(servico, data)
        }

    def test_lista_horarios_validos_para_servico_de_30_minutos(self):
        horarios = self.textos_dos_horarios()

        self.assertIn('09:00', horarios)
        self.assertIn('11:30', horarios)
        self.assertIn('13:00', horarios)
        self.assertIn('17:30', horarios)
        self.assertEqual(len(horarios), 16)

    def test_respeita_duracao_de_servico_de_60_minutos(self):
        servico_longo = Servico.objects.create(
            nome='Corte e barba',
            preco='60.00',
            duracao_minutos=60,
            ativo=True,
        )

        horarios = self.textos_dos_horarios(servico=servico_longo)

        self.assertIn('11:00', horarios)
        self.assertNotIn('11:30', horarios)
        self.assertIn('17:00', horarios)
        self.assertNotIn('17:30', horarios)
        self.assertEqual(len(horarios), 14)

    def test_remove_horarios_que_se_sobrepoem_a_agendamento_ativo(self):
        self.criar_agendamento(
            inicio=self.horario(9, 30),
            fim=self.horario(10, 30),
            situacao=Agendamento.Situacao.AGENDADO,
        )

        horarios = self.textos_dos_horarios()

        self.assertIn('09:00', horarios)
        self.assertNotIn('09:30', horarios)
        self.assertNotIn('10:00', horarios)
        self.assertIn('10:30', horarios)

    def test_cancelamento_libera_o_horario(self):
        self.criar_agendamento(
            inicio=self.horario(9, 30),
            fim=self.horario(10, 0),
            situacao=Agendamento.Situacao.CANCELADO,
        )

        horarios = self.textos_dos_horarios()

        self.assertIn('09:30', horarios)

    def test_servico_inativo_nao_oferece_horarios(self):
        self.servico.ativo = False
        self.servico.save()

        horarios = listar_horarios_disponiveis(self.servico, self.data)

        self.assertEqual(horarios, [])

    def test_dia_fechado_nao_oferece_horarios(self):
        domingo = datetime(2026, 11, 8).date()

        horarios = listar_horarios_disponiveis(self.servico, domingo)

        self.assertEqual(horarios, [])