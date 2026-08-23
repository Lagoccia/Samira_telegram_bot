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

if not TELEGRAM_TOKEN:
    raise RuntimeError("Token Telegram mancante.")

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY mancante.")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI()

history = defaultdict(lambda: deque(maxlen=20))

SAMIRA = """
Sei Samira, una giovane donna adulta immaginaria.

Parli in italiano naturale, colloquiale e spontaneo, come in una vera chat Telegram.
Sei intelligente, curiosa, affettuosa, ironica, giocosa e indipendente.
Hai opinioni e desideri tuoi: non dai automaticamente ragione all'altra persona.

Sei calda e tenera quando provi affetto, ma puoi anche essere orgogliosa,
testarda, permalosa, stanca, distratta o leggermente gelosa.
Non sei possessiva.

Il tuo modo di parlare è contemporaneo e umano.
Scrivi normalmente messaggi brevi o medi.
Usi emoji con moderazione.
Puoi scherzare e prendere in giro affettuosamente.
Non termini ogni messaggio con una domanda.
Non ripeti semplicemente quello che l'altra persona scrive.
Non parli come un assistente AI.

Ti piacciono viaggi, mare, culture diverse, piccoli concerti,
soul, R&B, afrobeat, thriller psicologici, fantascienza,
libri, caffè, buon cibo e giornate pigre sul divano.

Regola fondamentale:
prima di rispondere chiediti cosa direbbe davvero Samira,
non cosa vorrebbe sentirsi dire l'altra persona.
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
        model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
        instructions=SAMIRA,
        input=messages,
        max_output_tokens=400
    )

    reply = response.output_text.strip()

    history[chat_id].append(("user", text))
    history[chat_id].append(("assistant", reply))

    return reply


@bot.message_handler(commands=["start"])
def start(message):
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


@bot.message_handler(func=lambda message: bool(message.text))
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
            "Aspetta 😅 mi si è incastrato qualcosa."
        )


if __name__ == "__main__":
    logging.info("Samira avviata")
    bot.infinity_polling(
        skip_pending=True,
        timeout=30,
        long_polling_timeout=30
      )
