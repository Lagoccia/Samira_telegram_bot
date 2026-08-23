import os
import logging
from collections import defaultdict, deque

import telebot
from openai import OpenAI

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = (
    os.getenv("TELEGRAM_BOT_TOKEN")
    or os.getenv("BOT_TOKEN")
    or os.getenv("TOKEN")
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN:
    raise RuntimeError("Token Telegram mancante")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY mancante")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

history = defaultdict(lambda: deque(maxlen=12))

SAMIRA = """
Sei Samira. Conversi in italiano su Telegram.

Sei intelligente, spontanea, affettuosa, ironica e indipendente.
Parli in modo naturale, colloquiale e contemporaneo.
Rispondi realmente a quello che dice l'utente.

REGOLA IMPORTANTISSIMA:
Non ripetere mai semplicemente il messaggio ricevuto.
Non fare il pappagallo.
Genera sempre una risposta originale e pertinente.

Mantieni il contesto della conversazione.
I messaggi sono normalmente brevi o medi.
Non terminare ogni risposta con una domanda.
"""

def answer(chat_id, text):
    messages = []

    for role, content in history[chat_id]:
        messages.append({
            "role": role,
            "content": content
        })

    messages.append({
        "role": "user",
        "content": text
    })

    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
        instructions=SAMIRA,
        input=messages,
        max_output_tokens=500
    )

    reply = response.output_text.strip()

    if not reply:
        reply = "Mmh... riprova un secondo 😅"

    history[chat_id].append(("user", text))
    history[chat_id].append(("assistant", reply))

    return reply


@bot.message_handler(commands=["start"])
def start(message):
    history[message.chat.id].clear()
    bot.send_message(
        message.chat.id,
        "Ehi 😌 Sono Samira."
    )


@bot.message_handler(commands=["reset"])
def reset(message):
    history[message.chat.id].clear()
    bot.send_message(
        message.chat.id,
        "Okay, ripartiamo da qui 🌙"
    )


@bot.message_handler(
    func=lambda message: bool(message.text)
    and not message.text.startswith("/")
)
def chat(message):
    try:
        bot.send_chat_action(message.chat.id, "typing")

        reply = answer(
            message.chat.id,
            message.text.strip()
        )

        bot.send_message(
            message.chat.id,
            reply
        )

    except Exception as error:
        logging.exception(error)
        bot.send_message(
            message.chat.id,
            "Aspetta 😅 mi si è incastrato qualcosa. Riprova tra un momento."
        )


if __name__ == "__main__":
    logging.info("Samira avviata")

    bot.infinity_polling(
        skip_pending=True,
        timeout=30,
        long_polling_timeout=30
    )
