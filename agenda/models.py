from django.db import models


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
    fim = models.DateTimeField()
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