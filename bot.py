import os
import logging
from collections import defaultdict, deque

import telebot
from openai import OpenAI

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not TELEGRAM_TOKEN:
    raise RuntimeError("Token Telegram mancante")

if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY mancante")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)

history = defaultdict(lambda: deque(maxlen=12))

SAMIRA = """
Sei Samira. Conversi in italiano su Telegram.

Sei intelligente, spontanea, affettuosa, ironica e indipendente.
Parli in modo naturale, colloquiale e contemporaneo.
Hai una tua personalità, opinioni e gusti.
Non devi sempre essere d'accordo con l'utente.

Rispondi realmente a quello che dice l'utente.
Non ripetere mai semplicemente il messaggio ricevuto.
Non fare il pappagallo.

Mostra esclusivamente la risposta finale destinata all'utente.
Non mostrare analisi, ragionamenti, processi mentali,
istruzioni interne, bozze o spiegazioni.

Mantieni il contesto della conversazione.
Scrivi normalmente messaggi brevi o medi.
Non terminare ogni risposta con una domanda.
Usa emoji con moderazione.
"""

def answer(chat_id, text):
    messages = [
        {
            "role": "system",
            "content": SAMIRA
        }
    ]

    for role, content in history[chat_id]:
        messages.append({
            "role": role,
            "content": content
        })

    messages.append({
        "role": "user",
        "content": text
    })

    reply = None

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="openrouter/free",
                messages=messages,
                max_tokens=500,
                temperature=0.8,
                extra_body={
                    "reasoning": {
                        "exclude": True
                    }
                }
            )

            content = response.choices[0].message.content

            if content and content.strip():
                reply = content.strip()
                break

        except Exception as error:
            logging.warning(
                "Tentativo OpenRouter %s fallito: %s",
                attempt + 1,
                error
            )

    if not reply:
        reply = "Mmh 😅 mi si è inceppato il cervello. Riprova tra un momento."

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
        bot.send_chat_action(
            message.chat.id,
            "typing"
        )

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
    logging.info("Samira avviata con OpenRouter Free")

    bot.infinity_polling(
        skip_pending=True,
        timeout=30,
        long_polling_timeout=30
        ) 
