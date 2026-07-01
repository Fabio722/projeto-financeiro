import os
import telebot
from telebot import types
from pathlib import Path
import database


def load_dotenv():
    env_path = Path('.') / '.env'
    if not env_path.is_file():
        return
    with env_path.open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            key, value = line.split('=', 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

load_dotenv()
bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))

# Dicionário para guardar o que o usuário está fazendo
user_states = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💰 Registrar Ganho", "💸 Registrar Gasto")
    markup.add("📊 Resumo de Hoje")
    bot.reply_to(message, "Olá! Escolha uma opção:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    texto = message.text
    chat_id = message.chat.id

    if texto == "💸 Registrar Gasto":
        user_states[chat_id] = 'esperando_valor_gasto'
        bot.reply_to(message, "Qual o valor do gasto?")
    
    elif user_states.get(chat_id) == 'esperando_valor_gasto':
        # Aqui ele pega o valor e salva
        valor = float(texto.replace(',', '.'))
        database.inserir_movimentacao(categoria_id=1, valor=valor, descricao="Gasto via Bot")
        user_states[chat_id] = None
        bot.reply_to(message, "Gasto registrado com sucesso!")

# Inicia o bot
bot.polling()