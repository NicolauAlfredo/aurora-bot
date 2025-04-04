import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yagmail

# Carregar variáveis de ambiente
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASSWORD")
EMAIL_DESTINO = os.getenv("EMAIL_DESTINO")

# Ativar logs
logging.basicConfig(level=logging.INFO)

# Categorias e perguntas
PERGUNTAS = [
    ("📅 Data e Hora", [
        "Qual a data de hoje? (dd/mm/aaaa)",
        "Que horas são agora? (hh:mm)"
    ]),
    ("☀️ Rotina e Autodisciplina", [
        "Acordei na hora que eu planejei?",
        "Como me senti ao acordar? (corpo, mente, emoção)",
        "Quantas horas de sono eu tive?",
        "Fiz alguma atividade para cuidar do meu corpo (alongamento, água, higiene, treino)?",
        "Hoje estou começando o meu dia com foco ou distraído?"
    ]),
    ("🎯 Objetivos e Visão de Futuro", [
        "Qual é o meu grande objetivo de vida?", 
        "Onde eu quero estar daqui a 5 anos?",
        "O que preciso fazer hoje para me aproximar desse futuro?",
        "Que hábito posso reforçar hoje que me transforma no profissional que quero ser?"
    ]),
    ("🧠 Aperfeiçoamento Pessoal", [
        "O que estou estudando neste momento? E por quê?",
        "Qual conhecimento novo quero aprender hoje?",
        "Ontem eu evoluí em alguma habilidade? Qual?",
        "O que posso fazer melhor que ontem?",
        "Em que momento do dia eu serei mais produtivo?"
    ]),
    ("❤️ Atitude e Valores", [
        "Estou sendo uma pessoa educada e respeitosa com os outros?",
        "Fui honesto comigo mesmo e com os outros ontem?",
        "Tenho falado com gentileza e agido com empatia?",
        "Qual foi a minha maior tentação ontem? Eu resisti ou cedi?",
        "Estou sendo o tipo de pessoa que eu admiraria?"
    ]),
    ("🔥 Foco e Motivação", [
        "Qual é a única coisa que, se eu fizer hoje, tornará meu dia incrível?",
        "O que me motiva de verdade a não desistir?",
        "Qual frase ou pensamento me inspira hoje?",
        "Qual será o meu mini-desafio do dia?"
    ]),
    ("🙏 Espiritualidade", [
        "Já falei com Deus hoje?",
        "Senti-me conectado com algo maior do que eu?",
        "Há algo pelo qual quero agradecer agora?",
        "Quero pedir orientação ou ajuda a Deus sobre alguma coisa?"
    ]),
    ("📓 Autoavaliação do Dia", [
        "O que correu bem hoje?",
        "O que poderia ter sido feito de forma diferente?",
        "O que aprendi hoje sobre mim mesmo?",
        "De 0 a 10, que nota dou ao meu dia?"
    ]),
    ("✍️ Reflexão Escrita (no caderno)", [
        "Com base nas tuas respostas de hoje, responde agora no teu caderno:",
        "1. O que mais me surpreendeu nas minhas respostas de hoje?",
        "2. Em que estou a melhorar e em que estou a falhar?",
        "3. Como posso começar melhor o meu dia amanhã?",
        "4. O que Deus me inspirou a perceber hoje?"
    ])
]

# Dicionário para armazenar estado do utilizador
user_data = {}

# Início do comando /refletir
async def start_reflexao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {
        "respostas": [],
        "categoria_idx": 0,
        "pergunta_idx": 0
    }
    await enviar_proxima_pergunta(update, context)

async def enviar_proxima_pergunta(update, context):
    user_id = update.effective_user.id
    dados = user_data[user_id]

    if dados["categoria_idx"] >= len(PERGUNTAS):
        # Enviou todas as perguntas
        await update.message.reply_text("✅ Obrigado por responderes. Estou a enviar o teu resumo por email.")
        enviar_email(user_id)
        return

    categoria, perguntas = PERGUNTAS[dados["categoria_idx"]]
    if dados["pergunta_idx"] == 0:
        await update.message.reply_text(f"🧭 *{categoria}*", parse_mode="Markdown")

    pergunta_atual = perguntas[dados["pergunta_idx"]]
    await update.message.reply_text(pergunta_atual)

async def receber_resposta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in user_data:
        await update.message.reply_text("Escreve /refletir para começar.")
        return

    dados = user_data[user_id]
    categoria, perguntas = PERGUNTAS[dados["categoria_idx"]]

    dados["respostas"].append((categoria, perguntas[dados["pergunta_idx"]], update.message.text))

    # Avançar para próxima pergunta
    dados["pergunta_idx"] += 1
    if dados["pergunta_idx"] >= len(perguntas):
        dados["categoria_idx"] += 1
        dados["pergunta_idx"] = 0

    await enviar_proxima_pergunta(update, context)

def enviar_email(user_id):
    dados = user_data[user_id]
    yag = yagmail.SMTP(GMAIL_USER, GMAIL_PASS)

    corpo = "📝 Reflexão Diária\n\n"
    for cat, pergunta, resposta in dados["respostas"]:
        corpo += f"📌 {cat}\n"
        corpo += f"- {pergunta}\n"
        corpo += f"  ✍️ {resposta}\n\n"

    yag.send(
        to=EMAIL_DESTINO,
        subject="📩 Reflexão Diária - Aurora Bot",
        contents=[corpo]
    )

# Inicializar bot
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("refletir", start_reflexao))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receber_resposta))
    print("🤖 Aurora está viva. Ctrl+C para parar.")
    app.run_polling()

if __name__ == "__main__":
    main()
