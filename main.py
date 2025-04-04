import os
import logging
import sqlite3
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Configuração inicial
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
DB_NAME = "reflexao_bot.db"

# Setup do banco de dados
def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        user_id INTEGER,
        chat_id INTEGER,
        message_id INTEGER,
        timestamp DATETIME,
        PRIMARY KEY (user_id, message_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_sessions (
        user_id INTEGER PRIMARY KEY,
        respostas TEXT,
        categoria_idx INTEGER,
        pergunta_idx INTEGER
    )
    ''')
    
    conn.commit()
    conn.close()

setup_database()

# Perguntas (mantidas as mesmas do código original)
PERGUNTAS = [
    ("☀️ Rotina e Autodisciplina", [
        "Acordei na hora que planejei?",
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
    ])
]

INTRO_MSG = """
👋 Olá! Eu sou o Aurora Bot, o seu assistente para reflexão diária criada por Nicolau Alfredo. 
Eu ajudo a organizar as suas reflexões, ajudar no autodesenvolvimento e enviar resumos por email.

📝 O que faço:
1. Eu guio você através de perguntas que ajudam na autoavaliação e no aperfeiçoamento pessoal.
2. No final de cada reflexão, envio um resumo das suas respostas diretamente para o seu email.

🎯 Comandos:
- /refletir: Comece o seu processo de reflexão diária. 

🧭 Como funciona:
- Responda às perguntas com sinceridade e atenção. 
- Após completar as perguntas de reflexão, você receberá um resumo por email e orientações finais para reflexão escrita no seu caderno.

⚠️ Por motivos de privacidade, esta conversa será automaticamente eliminada após 2 horas.
Recomendo que faça download do documento gerado ao final.
"""

# Funções de banco de dados
def save_message(user_id: int, chat_id: int, message_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages VALUES (?, ?, ?, datetime('now'))",
        (user_id, chat_id, message_id)
    )
    conn.commit()
    conn.close()

def get_user_messages(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT chat_id, message_id FROM messages WHERE user_id = ?",
        (user_id,)
    )
    messages = cursor.fetchall()
    conn.close()
    return messages

def clean_old_messages():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM messages WHERE timestamp < datetime('now', '-48 hours')"
    )
    conn.commit()
    conn.close()

# Funções principais do bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(INTRO_MSG)
    save_message(update.effective_user.id, update.message.chat_id, update.message.message_id)

async def start_reflexao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT OR REPLACE INTO user_sessions VALUES (?, ?, ?, ?)",
        (user_id, "[]", 0, 0)
    )
    conn.commit()
    conn.close()
    
    await enviar_proxima_pergunta(update, context)
    save_message(user_id, update.message.chat_id, update.message.message_id)

async def enviar_proxima_pergunta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT respostas, categoria_idx, pergunta_idx FROM user_sessions WHERE user_id = ?",
        (user_id,)
    )
    dados = cursor.fetchone()
    
    if dados[1] >= len(PERGUNTAS):
        await finalizar_reflexao(update, context, dados[0])
        return
    
    categoria, perguntas = PERGUNTAS[dados[1]]
    if dados[2] == 0:
        msg = await update.message.reply_text(f"🧭 *{categoria}*", parse_mode="Markdown")
        save_message(user_id, update.message.chat_id, msg.message_id)
    
    pergunta_atual = perguntas[dados[2]]
    msg = await update.message.reply_text(pergunta_atual)
    save_message(user_id, update.message.chat_id, msg.message_id)

async def receber_resposta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_message(user_id, update.message.chat_id, update.message.message_id)
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT respostas, categoria_idx, pergunta_idx FROM user_sessions WHERE user_id = ?",
        (user_id,)
    )
    dados = list(cursor.fetchone())
    
    categoria, perguntas = PERGUNTAS[dados[1]]
    respostas = eval(dados[0])
    respostas.append((categoria, perguntas[dados[2]], update.message.text))
    
    dados[2] += 1
    if dados[2] >= len(perguntas):
        dados[1] += 1
        dados[2] = 0
    
    cursor.execute(
        "UPDATE user_sessions SET respostas = ?, categoria_idx = ?, pergunta_idx = ? WHERE user_id = ?",
        (str(respostas), dados[1], dados[2], user_id)
    )
    conn.commit()
    conn.close()
    
    await enviar_proxima_pergunta(update, context)

async def finalizar_reflexao(update: Update, context: ContextTypes.DEFAULT_TYPE, respostas_str: str):
    respostas = eval(respostas_str)
    now = datetime.now()
    nome_arquivo = f"reflexao_{now.strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
        arquivo.write(f"📝 Reflexão Diária - {now.strftime('%d/%m/%Y %H:%M')}\n\n")
        for cat, pergunta, resposta in respostas:
            arquivo.write(f"📌 {cat}\n")
            arquivo.write(f"- {pergunta}\n")
            arquivo.write(f"  ✍️ {resposta}\n\n")
    
    with open(nome_arquivo, "rb") as arquivo:
        msg = await update.message.reply_document(
            document=arquivo,
            caption=f"📄 Seu documento de reflexão ({now.strftime('%d/%m/%Y %H:%M')})"
        )
        save_message(update.effective_user.id, update.message.chat_id, msg.message_id)
    
    os.remove(nome_arquivo)
    
    reflexao_msg = """
    ✍️ Reflexão Escrita (no caderno):
    1. O que mais me surpreendeu nas minhas respostas?
    2. Em que estou melhorando e em que estou falhando?
    3. Como posso melhorar amanhã?
    4. O que Deus me inspirou a perceber hoje?
    """
    msg = await update.message.reply_text(reflexao_msg)
    save_message(update.effective_user.id, update.message.chat_id, msg.message_id)
    
    # Agendar limpeza
    await schedule_cleanup(context, update.effective_user.id)

async def schedule_cleanup(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    await asyncio.sleep(7200)  # 2 horas
    messages = get_user_messages(user_id)
    
    for chat_id, message_id in messages:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as e:
            logging.warning(f"Erro ao apagar mensagem: {e}")
    
    # Limpar banco de dados
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM user_sessions WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

async def cleanup_job(context: ContextTypes.DEFAULT_TYPE):
    clean_old_messages()

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("refletir", start_reflexao))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receber_resposta))
    
    # Agendar limpeza periódica
    job_queue = app.job_queue
    if job_queue:
        job_queue.run_repeating(cleanup_job, interval=3600, first=10)  # A cada 1 hora
    
    print("🤖 Bot iniciado com sistema de auto-limpeza")
    app.run_polling()

if __name__ == "__main__":
    main()
