from django import forms

from .models import Agendamento


HORARIOS = [('', 'Selecione um horário')]

for hora in range(9, 18):
    if hora == 12:
        continue

    for minuto in (0, 30):
        valor = f'{hora:02d}:{minuto:02d}:00'
        texto = f'{hora:02d}:{minuto:02d}'
        HORARIOS.append((valor, texto))


class DataHoraWidget(forms.SplitDateTimeWidget):
    def __init__(self, attrs=None):
        super().__init__(
            attrs=attrs,
            date_format='%Y-%m-%d',
            time_format='%H:%M:%S',
        )

        self.widgets[0] = forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'type': 'date',
                'aria-label': 'Data do atendimento',
            },
        )

        self.widgets[1] = forms.Select(
            choices=HORARIOS,
            attrs={'aria-label': 'Hora do atendimento'},
        )


class AgendamentoAdminForm(forms.ModelForm):
    inicio = forms.SplitDateTimeField(
        label='Início',
        input_date_formats=['%Y-%m-%d'],
        input_time_formats=['%H:%M:%S'],
        widget=DataHoraWidget(),
        help_text=(
            'Escolha a data e a hora. A duração do serviço '
            'e os horários ocupados serão verificados ao salvar.'
        ),
    )

    class Meta:
        model = Agendamento
        fields = [
            'nome_cliente',
            'telefone',
            'servico',
            'inicio',
            'situacao',
        ]