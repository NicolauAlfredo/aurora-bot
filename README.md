# Aurora Bot - Reflexão Diária e Desenvolvimento Pessoal

**Aurora** é um bot do Telegram criado para ajudar a cultivar bons hábitos diários e incentivar a reflexão pessoal. Através de uma série de perguntas diárias organizadas em categorias como rotina, objetivos, espiritualidade e mais, o bot permite que você faça uma autoavaliação do seu dia e se conecte consigo mesmo para melhorar continuamente.

## Funcionalidades

- Envio automático de perguntas todos os dias às 21:00.
- Perguntas divididas em categorias como:
  - **Rotina**
  - **Objetivos**
  - **Aperfeiçoamento Pessoal**
  - **Espiritualidade**
  - **Atitude e Valores**
  - **Foco e Motivação**
  - **Reflexão Escrita**
  - **Autoavaliação do Dia**
- Permite que o usuário registre suas respostas e receba um e-mail com um resumo diário.
- Comece a reflexão manualmente a qualquer momento com o comando `/refletir`.
- Respostas enviadas por e-mail ao final do ciclo diário.

## Tecnologias Utilizadas

- **Telegram Bot API**
- **Python 3.x**
- **python-telegram-bot**
- **apscheduler** para agendamento de envio diário de perguntas
- **yagmail** para envio de e-mails com o resumo das respostas
- **dotenv** para variáveis de ambiente

## Instalação

### Pré-requisitos

1. [Instalar Python 3.x](https://www.python.org/downloads/)
2. Instalar `pip` (gerenciador de pacotes do Python)

### Passos para Instalação

1. Clone o repositório:

   ```bash
   git clone https://github.com/seu-usuario/aurora-bot.git
