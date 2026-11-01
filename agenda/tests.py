from datetime import datetime, timedelta
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from .models import Agendamento, Servico
from .regras import validar_horario


class RegrasHorarioTests(SimpleTestCase):
    def horario(self, dia, hora, minuto=0):
        return timezone.make_aware(
            datetime(2026, 11, dia, hora, minuto),
            timezone.get_default_timezone(),
        )

    def setUp(self):
        agora = self.horario(3, 8)

        mock_agora = patch(
            'agenda.regras.timezone.now',
            return_value=agora,
        )

        mock_agora.start()
        self.addCleanup(mock_agora.stop)

    def test_aceita_horarios_validos(self):
        casos = [
            (3, 9, 0, 30),
            (3, 11, 30, 30),
            (3, 13, 0, 60),
            (3, 17, 0, 60),
            (3, 17, 30, 30),
            (7, 9, 0, 30),
        ]

        for dia, hora, minuto, duracao in casos:
            with self.subTest(
                dia=dia, hora=hora, minuto=minuto, duracao=duracao
            ):
                inicio = self.horario(dia, hora, minuto)
                fim = validar_horario(inicio, duracao)

                self.assertEqual(
                    fim,
                    inicio + timedelta(minutes=duracao),
                )

    def test_recusa_horarios_invalidos(self):
        casos = [
            (3, 8, 30, 30),
            (3, 9, 15, 30),
            (3, 11, 30, 60),
            (3, 12, 0, 30),
            (3, 12, 30, 30),
            (3, 17, 30, 60),
            (3, 18, 0, 30),
            (8, 9, 0, 30),
            (9, 9, 0, 30),
        ]

        for dia, hora, minuto, duracao in casos:
            with self.subTest(
                dia=dia, hora=hora, minuto=minuto, duracao=duracao
            ):
                with self.assertRaises(ValidationError):
                    validar_horario(
                        self.horario(dia, hora, minuto),
                        duracao,
                    )

    def test_recusa_passado_e_horario_atual(self):
        for inicio in [self.horario(3, 7), self.horario(3, 8)]:
            with self.subTest(inicio=inicio):
                with self.assertRaises(ValidationError):
                    validar_horario(inicio, 30)

    def test_recusa_duracao_invalida(self):
        for duracao in [0, -30]:
            with self.subTest(duracao=duracao):
                with self.assertRaises(ValidationError):
                    validar_horario(self.horario(3, 9), duracao)

    def test_recusa_horario_sem_fuso(self):
        with self.assertRaises(ValidationError):
            validar_horario(datetime(2026, 11, 3, 9), 30)

    def test_recusa_segundos_e_microssegundos(self):
        inicio = self.horario(3, 9)

        for horario in [
            inicio.replace(second=1),
            inicio.replace(microsecond=1),
        ]:
            with self.subTest(horario=horario):
                with self.assertRaises(ValidationError):
                    validar_horario(horario, 30)


class AgendamentoTests(TestCase):
    def horario(self, hora, minuto=0):
        return timezone.make_aware(
            datetime(2026, 11, 3, hora, minuto),
            timezone.get_default_timezone(),
        )

    def setUp(self):
        mock_agora = patch(
            'agenda.regras.timezone.now',
            return_value=self.horario(8),
        )

        self.relogio = mock_agora.start()
        self.addCleanup(mock_agora.stop)

        self.servico = Servico.objects.create(
            nome='Corte',
            preco='40.00',
            duracao_minutos=30,
        )

    def novo_agendamento(self, hora, minuto=0):
        return Agendamento(
            nome_cliente='Cliente de teste',
            telefone='11999999999',
            servico=self.servico,
            inicio=self.horario(hora, minuto),
        )

    def validar(self, agendamento):
        agendamento.full_clean(exclude=['fim'])

    def salvar(self, agendamento):
        self.validar(agendamento)
        agendamento.save()

    def test_calcula_e_salva_termino(self):
        agendamento = self.novo_agendamento(9)
        self.salvar(agendamento)

        agendamento.refresh_from_db()

        self.assertEqual(agendamento.fim, self.horario(9, 30))

    def test_recusa_periodos_sobrepostos(self):
        self.servico.duracao_minutos = 60
        self.servico.save()

        existente = self.novo_agendamento(10)
        self.salvar(existente)

        for hora, minuto in [(9, 30), (10, 0), (10, 30)]:
            with self.subTest(hora=hora, minuto=minuto):
                novo = self.novo_agendamento(hora, minuto)

                with self.assertRaisesMessage(
                    ValidationError,
                    'Já existe um atendimento nesse período.',
                ):
                    self.validar(novo)

    def test_aceita_atendimentos_encostados(self):
        self.salvar(self.novo_agendamento(10))

        self.salvar(self.novo_agendamento(9, 30))
        self.salvar(self.novo_agendamento(10, 30))

        self.assertEqual(Agendamento.objects.count(), 3)

    def test_cancelamento_libera_horario(self):
        original = self.novo_agendamento(10)
        self.salvar(original)

        original.situacao = Agendamento.Situacao.CANCELADO
        self.salvar(original)

        novo = self.novo_agendamento(10)
        self.salvar(novo)

        self.assertEqual(
            Agendamento.objects.filter(
                situacao=Agendamento.Situacao.AGENDADO,
            ).count(),
            1,
        )

    def test_edicao_nao_conflita_com_o_proprio_registro(self):
        agendamento = self.novo_agendamento(10)
        self.salvar(agendamento)

        agendamento.nome_cliente = 'Nome corrigido'
        self.salvar(agendamento)

        agendamento.refresh_from_db()

        self.assertEqual(agendamento.nome_cliente, 'Nome corrigido')
        self.assertEqual(Agendamento.objects.count(), 1)

    def test_permite_concluir_atendimento_passado(self):
        agendamento = self.novo_agendamento(9)
        self.salvar(agendamento)

        self.relogio.return_value = self.horario(12)

        agendamento.situacao = Agendamento.Situacao.CONCLUIDO
        self.salvar(agendamento)

        agendamento.refresh_from_db()

        self.assertEqual(
            agendamento.situacao,
            Agendamento.Situacao.CONCLUIDO,
        )

    def test_recusa_reativacao_se_horario_foi_ocupado(self):
        original = self.novo_agendamento(10)
        self.salvar(original)

        original.situacao = Agendamento.Situacao.CANCELADO
        self.salvar(original)

        self.salvar(self.novo_agendamento(10))

        original.situacao = Agendamento.Situacao.AGENDADO

        with self.assertRaisesMessage(
            ValidationError,
            'Já existe um atendimento nesse período.',
        ):
            self.validar(original)

    def test_recusa_novo_agendamento_com_servico_inativo(self):
        self.servico.ativo = False
        self.servico.save()

        with self.assertRaisesMessage(
            ValidationError,
            'Este serviço não está disponível.',
        ):
            self.validar(self.novo_agendamento(10))