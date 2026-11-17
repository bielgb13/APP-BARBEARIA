from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .disponibilidade import listar_horarios_disponiveis
from .models import Agendamento, Servico


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


class ConsultaHorariosForm(forms.Form):
    servico = forms.ModelChoiceField(
        queryset=Servico.objects.filter(ativo=True).order_by('nome'),
        label='Serviço',
        empty_label='Selecione um serviço',
    )

    data = forms.DateField(
        label='Data',
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={'type': 'date'},
        ),
    )

    def clean_data(self):
        data = self.cleaned_data['data']

        if data < timezone.localdate():
            raise forms.ValidationError(
                'Escolha a data de hoje ou uma data futura.'
            )

        if data.weekday() in (0, 6):
            raise forms.ValidationError(
                'O atendimento é de terça a sábado.'
            )

        return data


class AgendamentoClienteForm(AgendamentoAdminForm):
    class Meta:
        model = Agendamento
        fields = [
            'nome_cliente',
            'telefone',
            'servico',
            'inicio',
        ]
        labels = {
            'nome_cliente': 'Seu nome',
            'telefone': 'Telefone com DDD',
            'servico': 'Serviço',
        }
        widgets = {
            'nome_cliente': forms.TextInput(
                attrs={'autocomplete': 'name'},
            ),
            'telefone': forms.TextInput(
                attrs={
                    'type': 'tel',
                    'autocomplete': 'tel',
                    'placeholder': '(11) 99999-9999',
                },
            ),
        }

    def __init__(
        self,
        *args,
        servico_consultado=None,
        data_consultada=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.fields['servico'].queryset = (
            Servico.objects.filter(ativo=True).order_by('nome')
        )
        self.fields['servico'].empty_label = 'Selecione um serviço'

        self.horarios_disponiveis = []

        if self.is_bound:
            consulta = ConsultaHorariosForm({
                'servico': self.data.get(self.add_prefix('servico')),
                'data': self.data.get(self.add_prefix('inicio') + '_0'),
            })

            if consulta.is_valid():
                servico_consultado = consulta.cleaned_data['servico']
                data_consultada = consulta.cleaned_data['data']
            else:
                servico_consultado = None
                data_consultada = None

        if servico_consultado is not None and data_consultada is not None:
            self.horarios_disponiveis = listar_horarios_disponiveis(
                servico_consultado,
                data_consultada,
            )

            if not self.is_bound:
                self.initial['servico'] = servico_consultado.pk
                self.initial['inicio'] = [data_consultada, None]

        self.fields['inicio'].widget.widgets[1].choices = [
            ('', 'Selecione um horário'),
            *self.horarios_disponiveis,
        ]

        self.fields['inicio'].help_text = (
            'Os horários consideram a duração do serviço. '
            'Para trocar o serviço ou a data, consulte novamente.'
        )

    def clean_inicio(self):
        inicio = self.cleaned_data['inicio']
        horario = timezone.localtime(inicio).strftime('%H:%M:%S')

        horarios_permitidos = {
            valor for valor, texto in self.horarios_disponiveis
        }

        if horario not in horarios_permitidos:
            raise ValidationError(
                'Este horário não está disponível. '
                'Consulte os horários novamente.'
            )

        return inicio