from django.contrib import admin

from .forms import AgendamentoAdminForm
from .models import Agendamento, Servico


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'preco',
        'duracao_minutos',
        'ativo',
    )
    list_filter = ('ativo',)
    search_fields = ('nome',)


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    form = AgendamentoAdminForm

    list_display = (
        'nome_cliente',
        'telefone',
        'servico',
        'inicio',
        'fim',
        'situacao',
    )

    list_filter = (
        ('inicio', admin.DateFieldListFilter),
        'situacao',
        'servico',
    )

    search_fields = (
        'nome_cliente',
        'telefone',
    )

    date_hierarchy = 'inicio'
    ordering = ('inicio',)
    list_select_related = ('servico',)
    list_per_page = 25