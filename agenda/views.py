from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import AgendamentoClienteForm, ConsultaHorariosForm
from .models import Servico


def inicio(request):
    servicos = Servico.objects.filter(ativo=True).order_by('id')
    return render(request, 'agenda/inicio.html', {'servicos': servicos})


def agendar(request):
    confirmacao = request.session.pop('confirmacao_agendamento', None)
    formulario = None
    servico_consultado = None
    data_consultada = None

    if request.method == 'POST':
        confirmacao = None

        consulta = ConsultaHorariosForm({
            'servico': request.POST.get('servico'),
            'data': request.POST.get('inicio_0'),
        })

        formulario = AgendamentoClienteForm(request.POST)

        if formulario.is_valid():
            agendamento = formulario.save()
            inicio_local = timezone.localtime(agendamento.inicio)

            request.session['confirmacao_agendamento'] = {
                'servico': agendamento.servico.nome,
                'data': inicio_local.strftime('%d/%m/%Y'),
                'horario': inicio_local.strftime('%H:%M'),
            }

            return redirect('agenda:agendar')
    else:
        consulta = ConsultaHorariosForm(request.GET or None)

    if consulta.is_bound and consulta.is_valid():
        servico_consultado = consulta.cleaned_data['servico']
        data_consultada = consulta.cleaned_data['data']

        if formulario is None:
            formulario = AgendamentoClienteForm(
                servico_consultado=servico_consultado,
                data_consultada=data_consultada,
            )

    if formulario is not None:
        formulario.fields['inicio'].widget.widgets[0].attrs[
            'readonly'
        ] = True

    return render(
        request,
        'agenda/agendar.html',
        {
            'consulta': consulta,
            'formulario': formulario,
            'servico_consultado': servico_consultado,
            'data_consultada': data_consultada,
            'confirmacao': confirmacao,
        },
    )