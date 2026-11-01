from django.contrib import admin
from .forms import AgendamentoAdminForm
from .models import Agendamento, Servico


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco', 'duracao_minutos', 'ativo')


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    form = AgendamentoAdminForm
    list_display = (
        'nome_cliente',
        'servico',
        'inicio',
        'fim',
        'situacao',
    )
    list_filter = ('situacao', 'servico')
    search_fields = ('nome_cliente', 'telefone')
    date_hierarchy = 'inicio'