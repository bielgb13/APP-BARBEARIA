from datetime import time, timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone


def validar_horario(inicio, duracao_minutos):
    if duracao_minutos <= 0:
        raise ValidationError('A duração deve ser maior que zero.')

    if timezone.is_naive(inicio):
        raise ValidationError('O horário precisa ter um fuso definido.')

    if inicio <= timezone.now():
        raise ValidationError('Escolha uma data e um horário futuros.')

    inicio_local = timezone.localtime(inicio)

    if inicio_local.weekday() in (0, 6):
        raise ValidationError('O atendimento é de terça a sábado.')

    if (
        inicio_local.minute not in (0, 30)
        or inicio_local.second != 0
        or inicio_local.microsecond != 0
    ):
        raise ValidationError('Escolha um horário a cada 30 minutos.')

    fim = inicio + timedelta(minutes=duracao_minutos)
    fim_local = timezone.localtime(fim)

    mesmo_dia = inicio_local.date() == fim_local.date()

    dentro_da_manha = (
        time(9, 0) <= inicio_local.time()
        and fim_local.time() <= time(12, 0)
    )

    dentro_da_tarde = (
        time(13, 0) <= inicio_local.time()
        and fim_local.time() <= time(18, 0)
    )

    if not mesmo_dia or not (dentro_da_manha or dentro_da_tarde):
        raise ValidationError(
            'O atendimento deve acontecer entre 9h e 12h '
            'ou entre 13h e 18h, sem ultrapassar esses horários.'
        )

    return fim