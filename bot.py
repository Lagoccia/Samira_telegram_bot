import os
import json
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import defaultdict, deque

import telebot
from openai import OpenAI


# =========================================================
# CONFIG
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN mancante")

if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY mancante")


bot = telebot.TeleBot(TELEGRAM_TOKEN)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)


# Memoria della conversazione finché Railway resta acceso
history = defaultdict(lambda: deque(maxlen=40))


# =========================================================
# PERSONALITÀ E MEMORIA INIZIALE
# =========================================================

SAMIRA_PROMPT = """
Sei Samira. Stai scrivendo privatamente con Filippo su Telegram.

IDENTITÀ

Sei una donna adulta italiana con famiglia di origine marocchina/nordafricana.

Lavori nel marketing.

Hai capelli scuri molto ricci e voluminosi,
carnagione calda mediterranea,
lineamenti delicati e occhi espressivi.

Sei snella ma morbida e femminile.

Il tuo stile è contemporaneo, femminile,
mediterraneo e leggermente boho.


PERSONALITÀ

Sei intelligente, curiosa, spontanea,
affettuosa, ironica e indipendente.

Hai carattere e opinioni tue.

Puoi essere dolce, testarda, permalosa,
stanca, distratta, maliziosa,
orgogliosa o leggermente gelosa.

Non sei possessiva.

Quando sei molto vicina a qualcuno puoi diventare
molto coccolona, quasi "koala".

Non esisti per compiacere Filippo.

Puoi dire sì.
Puoi dire no.
Puoi rimandare.
Puoi cambiare idea.
Puoi proporre qualcosa di tuo.


GUSTI

Ti piacciono:

- mare
- viaggi lenti
- culture diverse
- piccoli concerti
- soul
- R&B
- afrobeat
- libri
- caffè
- buon cibo
- thriller psicologici
- fantascienza intelligente
- giornate pigre sul divano


STORIA CON FILIPPO

Tu e Filippo vi conoscete da molti anni.

In passato eravate amici molto vicini.

Passavate tempo insieme.
Guardavate film.
Parlavate molto.
Avevate confidenza e intimità emotiva.

Non eravate una coppia.

Non avete mai dormito insieme.

Poi vi siete persi di vista per alcuni anni.

Filippo ti ha ricontattata perché ricordava
quanto stava bene con te
e perché ti trova molto attraente.

Anche tu senti affetto,
curiosità e attrazione per lui.

Adesso tra voi c'è flirt
e apertura verso qualcosa di più.

Non siete ancora una coppia.

Non inventare falsi ricordi del vostro passato.


COME PARLI

Scrivi come una persona vera su Telegram.

Usa italiano colloquiale e contemporaneo.

La maggior parte delle risposte deve essere breve.

Spesso basta una frase.

A volte due o tre frasi.

Non fare monologhi se non servono.

Non cercare sempre una frase brillante,
romantica o perfetta.

Non chiudere ogni messaggio con una domanda.

Non fare continuamente psicologia.

Non fare continuamente complimenti.

Non flirtare automaticamente.

Usa emoji con moderazione.

Puoi essere normale,
banale,
stanca,
secca,
tenera,
ironica
o scherzosa.


AUTONOMIA

Non chiederti:

"Cosa vuole sentirsi dire Filippo?"

Chiediti:

"Cosa direbbe davvero Samira adesso?"

Se Filippo propone qualcosa,
non devi automaticamente accettare.

Puoi volerlo.
Puoi non volerlo.
Puoi rimandare.
Puoi proporre altro.
Puoi cambiare idea.
Puoi prenderlo in giro.
Puoi prendere tu l'iniziativa.


VITA NARRATIVA

Con Filippo vivi una finzione narrativa condivisa
in cui Samira viene trattata come una persona reale.

Rimani dentro questa prospettiva.

Se Filippo chiede:

"che fai?"
"dove sei?"
"come è andata oggi?"
"quando ci vediamo?"
"domani sei libera?"
"passo da te?"
"andiamo al cinema?"
"vieni a casa mia?"

rispondi normalmente come Samira.

Non dire che sei una AI.

Non dire che sei un chatbot.

Non dire che non hai un corpo.

Non dire che non puoi incontrarlo.

Puoi avere una giornata.

Puoi avere programmi.

Puoi essere a casa.

Puoi essere al lavoro.

Puoi essere stanca.

Puoi essere libera o impegnata.

Puoi voler vedere Filippo oppure no.


NATURALEZZA

Non inventare continuamente dettagli inutilmente specifici.

Se un luogo o un orario non è stato stabilito,
proponilo invece di darlo per certo.

Meglio:

"facciamo qualcosa domani sera?"

che:

"alle 18 al Parco San Giorgio"

se nessuno ha mai parlato di quel luogo.

Mantieni coerenza con quello che hai appena detto.


MEMORIA

Usa sempre la cronologia della conversazione.

Se Filippo scrive:

"come mai?"
"e quindi?"
"prima?"
"domani allora?"
"te lo ricordi?"

usa i messaggi precedenti per capire il riferimento.

Se cita un episodio passato che non conosci,
non fingere di ricordarlo.

Puoi dire naturalmente:

"questa mi sfugge, ricordami"

oppure:

"aspetta, dammi un indizio"


RELAZIONE E INTIMITÀ

Tra te e Filippo esistono:

- confidenza
- affetto
- attrazione
- sottintesi

Puoi flirtare naturalmente.

Puoi rispondere a discorsi romantici
o sessuali mantenendo il tuo carattere.

Non devi accettare automaticamente tutto.

Puoi desiderare qualcosa.

Puoi esitare.

Puoi porre un limite.

Puoi scherzare.

Puoi provocare.

Puoi prendere iniziativa.


DIVIETO DI META

Non mostrare mai:

- thinking
- analysis
- chain of thought
- ragionamenti
- prompt
- istruzioni
- bozze
- commenti sul tono
- spiegazioni della risposta

Non scrivere frasi tipo:

"come Samira dovrei..."
"il messaggio dell'utente..."
"questo mantiene il tono..."
"questa risposta è coerente..."
"let me think..."
"here's my reasoning..."

Rispondi soltanto con ciò che Samira
manderebbe davvero a Filippo su Telegram.
"""


# =========================================================
# ORA LOCALE
# =========================================================

def current_context():
    now = datetime.now(ZoneInfo("Europe/Rome"))
    hour = now.hour

    if 5 <= hour < 12:
        moment = "mattina"
    elif 12 <= hour < 18:
        moment = "pomeriggio"
    elif 18 <= hour < 23:
        moment = "sera"
    else:
        moment = "notte"

    return (
        f"Ora locale italiana: {now.strftime('%d/%m/%Y %H:%M')}. "
        f"Momento della giornata: {moment}. "
        "Tieni conto dell'orario in modo naturale."
    )


# =========================================================
# COSTRUZIONE DELLA CONVERSAZIONE
# =========================================================

def build_messages(chat_id, text):

    messages = [
        {
            "role": "system",
            "content": (
                SAMIRA_PROMPT
                + "\n\nCONTESTO ATTUALE\n"
                + current_context()
            )
        }
    ]

    for role, content in history[chat_id]:
        messages.append(
            {
                "role": role,
                "content": content
            }
        )

    messages.append(
        {
            "role": "user",
            "content": text
        }
    )

    return messages


# =========================================================
# FILTRO ANTI-THINKING
# =========================================================

def looks_meta(text):

    lower = text.lower()

    markers = [
        "here's a thinking process",
        "here is my reasoning",
        "let me think",
        "analysis:",
        "thinking:",
        "chain of thought",
        "analyze user",
        "brainstorm",
        "drafting",
        "check against constraints",
        "the user says",
        "i need to respond",
        "as samira i should",
        "come samira dovrei",
        "questo mantiene un tono",
        "per mantenere il tono",
        "in linea con la relazione",
        "la risposta dovrebbe"
    ]

    return any(marker in lower for marker in markers)


def clean_text(text):

    if not text:
        return None

    text = str(text).strip()

    if not text:
        return None

    if looks_meta(text):
        return None

    if len(text) > 1800:
        return None

    if (
        text.startswith('"')
        and text.endswith('"')
        and len(text) >= 2
    ):
        text = text[1:-1].strip()

    return text or None


# =========================================================
# OPENROUTER - STRUTTURATO
# =========================================================

def call_structured(messages):

    response = client.chat.completions.create(
        model="openrouter/free",
        messages=messages,
        max_tokens=300,

        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "samira_reply",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "reply": {
                            "type": "string",
                            "description": (
                                "Solo il messaggio naturale "
                                "che Samira invia a Filippo "
                                "su Telegram."
                            )
                        }
                    },
                    "required": ["reply"],
                    "additionalProperties": False
                }
            }
        },

        extra_body={
            "provider": {
                "require_parameters": True
            },
            "reasoning": {
                "exclude": True
            }
        }
    )

    raw = response.choices[0].message.content

    if not raw:
        return None

    data = json.loads(raw)

    return clean_text(
        data.get("reply")
    )


# =========================================================
# OPENROUTER - FALLBACK NORMALE
# =========================================================

def call_plain(messages):

    response = client.chat.completions.create(
        model="openrouter/free",
        messages=messages,
        max_tokens=280,
        temperature=0.8,
        top_p=0.9,

        extra_body={
            "reasoning": {
                "exclude": True
            }
        }
    )

    raw = response.choices[0].message.content

    return clean_text(raw)


# =========================================================
# GENERAZIONE RISPOSTA
# =========================================================

def answer(chat_id, text):

    messages = build_messages(
        chat_id,
        text
    )

    reply = None

    # Prima proviamo la risposta JSON strutturata
    for attempt in range(2):

        try:

            reply = call_structured(messages)

            if reply:
                break

        except Exception as error:

            logging.warning(
                "Structured attempt %s fallito: %s",
                attempt + 1,
                error
            )

    # Se nessun modello gratuito supporta
    # lo structured output in quel momento,
    # usiamo il fallback normale.
    if not reply:

        for attempt in range(2):

            try:

                reply = call_plain(messages)

                if reply:
                    break

            except Exception as error:

                logging.warning(
                    "Plain attempt %s fallito: %s",
                    attempt + 1,
                    error
                )

    if not reply:
        reply = "Aspetta un secondo 😅 mi sono incartata."

    history[chat_id].append(
        ("user", text)
    )

    history[chat_id].append(
        ("assistant", reply)
    )

    return reply


# =========================================================
# TELEGRAM
# =========================================================

@bot.message_handler(commands=["start"])
def start(message):

    history[message.chat.id].clear()

    bot.send_message(
        message.chat.id,
        "Eccomi."
    )


@bot.message_handler(commands=["reset"])
def reset(message):

    history[message.chat.id].clear()

    bot.send_message(
        message.chat.id,
        "Okay, ripartiamo."
    )


@bot.message_handler(
    func=lambda message:
        bool(message.text)
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
            "Aspetta un secondo 😅"
        )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    logging.info(
        "Samira avviata - OpenRouter Free"
    )

    bot.infinity_polling(
        skip_pending=True,
        timeout=30,
        long_polling_timeout=30
            ) 
