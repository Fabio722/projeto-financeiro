import os
import telebot
from telebot import types
from dotenv import load_dotenv
import database  # Isso importa o seu arquivo database.py

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Dicionário para Guardar o estado do usuário (quem está registrando o quê)
user_states = {}

def menu_principal():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💰 Registrar Ganho", "💸 Registrar Gasto")
    markup.add("📊 Resumo de Hoje")
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Olá! Sou seu assistente financeiro. Como posso te ajudar?", reply_markup=menu_principal())

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text

    # 1. Se clicar nos botões do menu
    if text in ["💰 Registrar Ganho", "💸 Registrar Gasto"]:
        tipo = "ganho" if "Ganho" in text else "gasto"
        user_states[chat_id] = {"tipo": tipo, "step": "valor"}
        bot.reply_to(message, f"Entendido! Qual o valor do {tipo}? (Ex: 50.00)")

    # 2. Se o bot estiver esperando o valor
    elif chat_id in user_states and user_states[chat_id]["step"] == "valor":
        try:
            valor = float(text.replace(',', '.'))
            user_states[chat_id]["valor"] = valor
            user_states[chat_id]["step"] = "categoria"
            bot.reply_to(message, "Valor anotado! Qual a categoria? (Ex: Alimentação, Trabalho, Lazer)")
        except:
            bot.reply_to(message, "Por favor, digite apenas números para o valor (Ex: 20.50)")

    # 3. Se o bot estiver esperando a categoria
    elif chat_id in user_states and user_states[chat_id]["step"] == "categoria":
        categoria = text
        user_states[chat_id]["categoria"] = categoria
        user_states[chat_id]["step"] = "descricao"
        bot.reply_to(message, "Categoria salva! Agora, digite uma descrição curta:")

    # 4. Se o bot estiver esperando a descrição
    elif chat_id in user_states and user_states[chat_id]["step"] == "descricao":
        dados = user_states[chat_id]
        # Salva no banco de dados usando sua função do database.py
        database.registrar_fluxo(dados["tipo"], dados["categoria"], dados["valor"], text)
        
        bot.reply_to(message, "✅ Sucesso! Movimentação salva no banco de dados.", reply_markup=menu_principal())
        del user_states[chat_id] # Limpa o estado após salvar

    # 5. Se o bot for solicitado o Resumo de Hoje
    elif text == "📊 Resumo de Hoje":
        resumo = database.buscar_resumo_hoje()
        if not resumo:
            bot.reply_to(message, "Nenhuma movimentação registrada hoje.")
        else:
            texto = "📊 *Resumo de Hoje:*\n\n"
            total = 0
            for item in resumo:
                # item[0]=tipo, item[1]=categoria, item[2]=valor, item[3]=descricao
                texto += f"• {item[0].capitalize()}: {item[1]} - R$ {item[2]:.2f}\n"
                # Calcula o saldo (ganho soma, gasto subtrai)
                if item[0] == 'ganho':
                    total += float(item[2])
                else:
                    total -= float(item[2])
            
            texto += f"\n💰 *Saldo final do dia:* R$ {total:.2f}"
            bot.reply_to(message, texto, parse_mode="Markdown")

    else:
        bot.reply_to(message, "Use os botões do menu para começar.")

print("🤖 O Bot do Telegram está online e escutando...")
bot.infinity_polling()