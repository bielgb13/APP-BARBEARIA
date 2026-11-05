from datetime import datetime, time, timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Agendamento
from .regras import validar_horario


def listar_horarios_disponiveis(servico, data):
    if not servico.ativo:
        return []

    fuso = timezone.get_default_timezone()

    inicio_dia = timezone.make_aware(
        datetime.combine(data, time.min),
        fuso,
    )

    fim_dia = timezone.make_aware(
        datetime.combine(data + timedelta(days=1), time.min),
        fuso,
    )

    ocupados = list(
        Agendamento.objects.filter(
            inicio__lt=fim_dia,
            fim__gt=inicio_dia,
        )
        .exclude(situacao=Agendamento.Situacao.CANCELADO)
        .values_list('inicio', 'fim')
    )

    horarios = []

    for hora in range(9, 18):
        if hora == 12:
            continue

        for minuto in (0, 30):
            inicio = timezone.make_aware(
                datetime.combine(data, time(hora, minuto)),
                fuso,
            )

            try:
                fim = validar_horario(
                    inicio,
                    servico.duracao_minutos,
                )
            except ValidationError:
                continue

            tem_conflito = any(
                inicio < fim_ocupado and fim > inicio_ocupado
                for inicio_ocupado, fim_ocupado in ocupados
            )

            if not tem_conflito:
                valor = inicio.strftime('%H:%M:%S')
                texto = inicio.strftime('%H:%M')
                horarios.append((valor, texto))

    return horarios