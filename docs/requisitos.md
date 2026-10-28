# Requisitos do APP-BARBEARIA

## Funcionamento

O sistema será usado por uma barbearia com um barbeiro.

O atendimento será de terça a sábado, das 9h às 12h e das 13h às 18h.

## Serviços

| Serviço | Preço | Duração |
|---|---|---|
| Corte | R$ 40,00 | 30 minutos |
| Barba | R$ 30,00 | 30 minutos |
| Corte e barba | R$ 60,00 | 60 minutos |

## Agendamento

O cliente deverá informar nome, telefone, serviço, data e horário.

Todos os campos serão obrigatórios.

Os horários de início serão oferecidos a cada 30 minutos, conforme a disponibilidade.

O atendimento deverá terminar dentro do horário de funcionamento, sem ocupar o intervalo de almoço.

Não será permitido agendar em datas ou horários que já passaram.

Não será permitido marcar atendimentos que ocupem o mesmo período. Um serviço de 60 minutos deverá reservar todo esse tempo na agenda.

Após confirmar o agendamento, o sistema deverá mostrar o serviço, a data e o horário escolhido.

## Área do barbeiro

O barbeiro deverá entrar com usuário e senha.

Na agenda, poderá consultar os atendimentos por data, com nome do cliente, telefone, serviço e horário.

Também poderá cancelar um agendamento ou marcar o atendimento como concluído.

Os agendamentos terão três situações: agendado, cancelado e concluído.

Ao cancelar um agendamento, o horário ficará disponível novamente.

Os dados dos clientes deverão aparecer somente na área do barbeiro.

## Armazenamento

Os agendamentos deverão continuar salvos depois que o sistema for fechado e aberto novamente.

## Limites

A primeira versão não terá pagamento online, mensagens automáticas ou cadastro de vários barbeiros.