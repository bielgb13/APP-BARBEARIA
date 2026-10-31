from django.shortcuts import render

from .models import Servico


def inicio(request):
    servicos = Servico.objects.filter(ativo=True).order_by('id')
    return render(request, 'agenda/inicio.html', {'servicos': servicos})