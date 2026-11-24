# APP-BARBEARIA

Projeto acadêmico de um sistema de agendamento para uma barbearia com um único barbeiro. O cliente escolhe o serviço, consulta os horários livres e faz a reserva informando nome e telefone. O barbeiro acompanha os atendimentos pela área administrativa.

## Como funciona

A barbearia atende de terça a sábado, das 9h às 12h e das 13h às 18h. Os horários de início são oferecidos a cada 30 minutos. O sistema considera a duração do serviço para verificar se o atendimento cabe no expediente e se há outra reserva no mesmo período.

Por exemplo, se um cliente marcar corte e barba às 17h, o atendimento vai até as 18h. Nesse caso, o horário das 17h30 também fica ocupado. Se o barbeiro cancelar a reserva, os horários voltam a aparecer na consulta.

O cliente recebe a confirmação na própria página, com serviço, data e horário. Na área administrativa, o barbeiro pode consultar a agenda por dia, pesquisar pelo telefone e marcar um atendimento como concluído ou cancelado. A primeira versão funciona localmente e não inclui pagamentos, mensagens automáticas ou gestão de várias unidades.

## Como executar no Windows

O projeto usa Python 3.13, Django e SQLite. Com o Git e o Python 3.13 instalados, abra o PowerShell e execute os comandos abaixo para preparar uma cópia do projeto.

```powershell
git clone https://github.com/bielgb13/APP-BARBEARIA.git
cd APP-BARBEARIA
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
```

No último comando, escolha o usuário e a senha que serão usados para acessar a administração. Para iniciar o servidor, execute:

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

Deixe o terminal aberto enquanto usa o sistema. Na primeira execução, entre na [área administrativa](http://127.0.0.1:8000/admin/), abra **Serviços** e cadastre os serviços abaixo como ativos.

| Serviço | Preço | Duração |
| --- | --- | --- |
| Corte | R$ 40,00 | 30 minutos |
| Barba | R$ 30,00 | 30 minutos |
| Corte e barba | R$ 60,00 | 60 minutos |

Depois, abra a [página de agendamento](http://127.0.0.1:8000/agendar/) para consultar os horários e fazer uma reserva.

## Testes

Na pasta que contém o arquivo `manage.py`, execute:

```powershell
.\.venv\Scripts\python.exe manage.py test agenda
```

Os testes verificam as regras de horário, a disponibilidade dos serviços e o fluxo de agendamento do cliente.

## Autor

Gabriel Ferreira da Silva