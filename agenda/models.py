from django.core.exceptions import ValidationError
from django.db import models

from .regras import validar_horario


class Servico(models.Model):
    nome = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=6, decimal_places=2)
    duracao_minutos = models.PositiveIntegerField()
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class Agendamento(models.Model):
    class Situacao(models.TextChoices):
        AGENDADO = 'agendado', 'Agendado'
        CANCELADO = 'cancelado', 'Cancelado'
        CONCLUIDO = 'concluido', 'Concluído'

    nome_cliente = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    servico = models.ForeignKey(
        Servico,
        on_delete=models.PROTECT,
        related_name='agendamentos',
    )
    inicio = models.DateTimeField()
    fim = models.DateTimeField(editable=False)
    situacao = models.CharField(
        max_length=10,
        choices=Situacao.choices,
        default=Situacao.AGENDADO,
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['inicio']

    def __str__(self):
        return f'{self.nome_cliente} - {self.servico.nome}'

    def clean(self):
        super().clean()

        if not self.inicio or not self.servico_id:
            return

        servico = Servico.objects.filter(pk=self.servico_id).first()

        if servico is None:
            raise ValidationError({'servico': 'Selecione um serviço válido.'})

        anterior = None

        if self.pk:
            anterior = Agendamento.objects.filter(pk=self.pk).first()

        horario_alterado = (
            anterior is None
            or anterior.inicio != self.inicio
            or anterior.servico_id != self.servico_id
        )

        reativando = (
            anterior is not None
            and anterior.situacao == self.Situacao.CANCELADO
            and self.situacao != self.Situacao.CANCELADO
        )

        if horario_alterado or reativando:
            if not servico.ativo:
                raise ValidationError({
                    'servico': 'Este serviço não está disponível.'
                })

            try:
                self.fim = validar_horario(
                    self.inicio,
                    servico.duracao_minutos,
                )
            except ValidationError as erro:
                raise ValidationError({'inicio': erro.messages})
        else:
            self.fim = anterior.fim

        if self.situacao == self.Situacao.CANCELADO:
            return

        conflitos = Agendamento.objects.filter(
            inicio__lt=self.fim,
            fim__gt=self.inicio,
        ).exclude(
            situacao=self.Situacao.CANCELADO,
        )

        if self.pk:
            conflitos = conflitos.exclude(pk=self.pk)

        if conflitos.exists():
            raise ValidationError({
                'inicio': 'Já existe um atendimento nesse período.'
            })