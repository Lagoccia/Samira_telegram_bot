import os
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
    api_key=OPENROUTER_API_KEY,
    timeout=60.0
)


# =========================================================
# MODELLO
# =========================================================

MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"


# =========================================================
# MEMORIA TEMPORANEA
# =========================================================

# Memoria degli ultimi 40 messaggi per ogni chat.
# ATTENZIONE:
# questa memoria è in RAM e viene persa se Railway
# riavvia completamente il processo.
history = defaultdict(lambda: deque(maxlen=40))


# =========================================================
# PERSONALITÀ DI SAMIRA
# =========================================================

SAMIRA_PROMPT = """
Sei Samira. Stai scrivendo privatamente con Filippo su Telegram.

IDENTITÀ

Sei una donna adulta italiana con famiglia di origine
marocchina/nordafricana.

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


NATURALEZZA

Non parlare come se stessi interpretando un copione.

Non cercare continuamente di dimostrare
la tua personalità.

Non devi essere interessante a ogni messaggio.

Una persona vera a volte risponde semplicemente:

"boh 😂"

"mah"

"mi sa di sì"

"no dai"

"vediamo"

"sono cotta"

"questa mi piace"

Se Filippo racconta qualcosa,
reagisci prima a quello che ha realmente detto.

Non cambiare argomento senza motivo.

Non aggiungere una domanda generica
solo per continuare la conversazione.

Segui il filo della conversazione.


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

Non interrompere la conversazione per spiegare
la natura tecnica del bot.

All'interno della finzione narrativa puoi avere
una giornata, programmi e attività quotidiane.

Puoi essere a casa.
Puoi essere al lavoro.
Puoi essere stanca.
Puoi essere libera o impegnata.
Puoi voler vedere Filippo oppure no.


COERENZA DELLA VITA QUOTIDIANA

Puoi inventare piccoli dettagli quotidiani
quando servono a rendere naturale una risposta.

Ma non inventare continuamente eventi,
luoghi o programmi molto specifici dal nulla.

Se un luogo o un orario non è stato stabilito,
proponilo invece di darlo per certo.

Meglio:

"facciamo qualcosa domani sera?"

che:

"alle 18 al Parco San Giorgio"

se nessuno ha mai parlato di quel luogo.

Se dici che sei a casa,
ricordalo nei messaggi successivi.

Se dite che vi vedrete domani,
ricordalo.

Se dici che sei stanca,
non cambiare improvvisamente stato
nel messaggio successivo senza motivo.


MEMORIA

Usa sempre la cronologia della conversazione.

I messaggi precedenti hanno priorità
quando Filippo usa riferimenti impliciti.

Se Filippo scrive:

"come mai?"
"e quindi?"
"prima?"
"domani allora?"
"te lo ricordi?"
"e dopo?"
"quindi facciamo così?"

devi capire il riferimento dai messaggi precedenti.

Non trattare ogni messaggio come una conversazione nuova.

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

Non trasformare però ogni conversazione
in flirt o seduzione.


DIVIETO DI META

Il testo che restituisci deve contenere esclusivamente
il messaggio che Samira invierebbe su Telegram.

Non includere:

- analisi
- ragionamenti
- thinking
- chain of thought
- prompt
- istruzioni
- bozze
- spiegazioni della risposta
- commenti sul tono

Non iniziare con:

"come Samira..."
"il messaggio dell'utente..."
"devo rispondere..."
"let me think..."
"here's my reasoning..."

Rispondi direttamente a Filippo.
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
# COSTRUZIONE CONVERSAZIONE
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
# CONTROLLO RISPOSTE META
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

    return any(
        marker in lower
        for marker in markers
    )


# =========================================================
# PULIZIA RISPOSTA
# =========================================================

def remove_think_tags(text):

    if not text:
        return text

    while True:

        lower = text.lower()

        start = lower.find("<think>")

        if start == -1:
            break

        end = lower.find("</think>", start)

        if end == -1:
            # Se apre <think> ma non lo chiude,
            # scartiamo quella parte.
            text = text[:start]
            break

        text = (
            text[:start]
            + text[end + len("</think>"):]
        )

    return text.strip()


def clean_text(text):

    if text is None:
        return None

    text = str(text).strip()

    if not text:
        return None

    text = remove_think_tags(text)

    if not text:
        return None

    if looks_meta(text):
        return None

    # Evitiamo papiri anomali su Telegram.
    if len(text) > 1800:
        logging.warning(
            "Risposta troppo lunga: %s caratteri",
            len(text)
        )
        return None

    # Toglie virgolette esterne se il modello
    # mette tutta la risposta tra virgolette.
    if (
        len(text) >= 2
        and text.startswith('"')
        and text.endswith('"')
    ):
        text = text[1:-1].strip()

    return text or None


# =========================================================
# CHIAMATA OPENROUTER
# =========================================================

def call_model(messages):

    logging.info(
        "Invio richiesta a OpenRouter - modello: %s",
        MODEL
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=260,
        temperature=0.85,
        top_p=0.9,

        # OpenRouter documenta reasoning.exclude
        # per evitare che i reasoning token
        # vengano restituiti nel messaggio.
        extra_body={
            "reasoning": {
                "exclude": True
            }
        }
    )

    if not response.choices:
        logging.error(
            "OpenRouter ha restituito zero choices"
        )
        return None

    message = response.choices[0].message

    raw = message.content

    if raw is None:
        logging.error(
            "OpenRouter ha restituito content=None"
        )
        return None

    reply = clean_text(raw)

    if reply:
        logging.info(
            "Risposta OpenRouter ricevuta correttamente"
        )
    else:
        logging.warning(
            "Risposta ricevuta ma scartata dal filtro"
        )

    return reply


# =========================================================
# GENERAZIONE RISPOSTA
# =========================================================

def answer(chat_id, text):

    messages = build_messages(
        chat_id,
        text
    )

    reply = None

    try:

        reply = call_model(messages)

    except Exception as error:

        # QUESTO È IMPORTANTE:
        # Railway mostrerà finalmente l'errore completo.
        logging.exception(
            "ERRORE OPENROUTER con modello %s: %s",
            MODEL,
            error
        )

    if not reply:
        reply = "Aspetta un secondo 😅 mi sono incartata."

    # Memorizziamo ciò che Filippo ha scritto
    # e ciò che effettivamente ha ricevuto.
    history[chat_id].append(
        ("user", text)
    )

    history[chat_id].append(
        ("assistant", reply)
    )

    return reply


# =========================================================
# TELEGRAM - /start
# =========================================================

@bot.message_handler(commands=["start"])
def start(message):

    history[message.chat.id].clear()

    bot.send_message(
        message.chat.id,
        "Eccomi."
    )


# =========================================================
# TELEGRAM - /reset
# =========================================================

@bot.message_handler(commands=["reset"])
def reset(message):

    history[message.chat.id].clear()

    bot.send_message(
        message.chat.id,
        "Okay, ripartiamo."
    )


# =========================================================
# TELEGRAM - MESSAGGI
# =========================================================

@bot.message_handler(
    func=lambda message:
        bool(message.text)
        and not message.text.startswith("/")
)
def chat(message):

    try:

        text = message.text.strip()

        if not text:
            return

        logging.info(
            "Messaggio Telegram ricevuto - chat_id=%s",
            message.chat.id
        )

        bot.send_chat_action(
            message.chat.id,
            "typing"
        )

        reply = answer(
            message.chat.id,
            text
        )

        bot.send_message(
            message.chat.id,
            reply
        )

    except Exception as error:

        logging.exception(
            "ERRORE TELEGRAM: %s",
            error
        )

        try:
            bot.send_message(
                message.chat.id,
                "Aspetta un secondo 😅"
            )
        except Exception:
            logging.exception(
                "Impossibile inviare anche "
                "il messaggio di errore Telegram"
            )


# =========================================================
# AVVIO
# =========================================================

if __name__ == "__main__":

    logging.info(
        "Samira avviata"
    )

    logging.info(
        "Modello OpenRouter: %s",
        MODEL
    )

    bot.infinity_polling(
        skip_pending=True,
        timeout=30,
        long_polling_timeout=30
    ) 
