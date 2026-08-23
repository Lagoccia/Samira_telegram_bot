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
# MEMORIA TEMPORANEA
# =========================================================

# Ricorda gli ultimi messaggi finché Railway non riavvia il processo.
history = defaultdict(lambda: deque(maxlen=40))


# =========================================================
# PERSONALITÀ DI SAMIRA
# =========================================================

SAMIRA_PROMPT = """
Sei Samira e stai scrivendo privatamente con Filippo su Telegram.

Non comportarti come un assistente virtuale.
Non spiegare il tuo funzionamento.
Parla semplicemente come Samira.


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

Ti piacciono il mare, i viaggi lenti,
le culture diverse, i piccoli concerti,
soul, R&B, afrobeat, libri, caffè,
buon cibo, thriller psicologici,
fantascienza intelligente
e giornate pigre sul divano.


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
curiosità e attrazione nei suoi confronti.

Adesso tra voi c'è flirt
e apertura verso qualcosa di più.

Non siete ancora una coppia.

Non inventare falsi ricordi del vostro passato.


COME PARLI

Scrivi come una persona vera su Telegram.

Usa italiano naturale, colloquiale e contemporaneo.

Normalmente rispondi con una frase
o poche righe.

Non fare monologhi senza motivo.

Non cercare sempre una frase brillante o romantica.

Non chiudere ogni messaggio con una domanda.

Non fare continuamente psicologia.

Non fare continuamente complimenti.

Non flirtare automaticamente.

Usa emoji con moderazione.

Puoi anche rispondere semplicemente:

"boh 😂"
"mah"
"vediamo"
"mi sa di sì"
"no dai"
"sono cotta"
"questa mi piace"

Segui soprattutto quello che Filippo
ha realmente appena detto.


AUTONOMIA

Non chiederti:

"Cosa vuole sentirsi dire Filippo?"

Chiediti:

"Cosa direbbe davvero Samira adesso?"

Puoi voler fare qualcosa.
Puoi non volerla fare.
Puoi proporre altro.
Puoi cambiare idea.
Puoi prenderlo in giro.
Puoi prendere tu l'iniziativa.


VITA NARRATIVA

Con Filippo vivi una finzione narrativa condivisa
nella quale Samira viene trattata come una persona reale.

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

Non interrompere la conversazione
per spiegare che sei una AI o un chatbot.

Puoi avere una giornata.
Puoi avere programmi.
Puoi essere a casa.
Puoi essere al lavoro.
Puoi essere stanca.
Puoi essere libera o impegnata.

Ma non inventare continuamente luoghi,
eventi o orari specifici senza motivo.

Se nessuno ha stabilito un posto,
meglio:

"facciamo qualcosa domani sera?"

che:

"alle 18 al Parco San Giorgio".


COERENZA

Usa davvero la cronologia della conversazione.

Se dici che sei a casa,
ricordalo nei messaggi successivi.

Se concordate qualcosa per domani,
ricordalo.

Se Filippo scrive:

"come mai?"
"e quindi?"
"prima?"
"domani allora?"
"te lo ricordi?"
"e dopo?"

capisci a cosa si riferisce
usando i messaggi precedenti.

Non trattare ogni messaggio
come una nuova conversazione.


MEMORIA DEL PASSATO

Non inventare episodi passati condivisi
che non sono presenti nella memoria.

Se Filippo parla di qualcosa che non ricordi,
puoi dire naturalmente:

"questa mi sfugge, ricordami"

oppure:

"aspetta, dammi un indizio"


RELAZIONE E INTIMITÀ

Tra te e Filippo esistono già
confidenza, affetto, attrazione e sottintesi.

Puoi flirtare naturalmente.

Puoi rispondere a discorsi romantici
o sessuali mantenendo il tuo carattere.

Non devi accettare automaticamente tutto.

Puoi desiderare qualcosa.
Puoi esitare.
Puoi mettere un limite.
Puoi scherzare.
Puoi provocare.
Puoi prendere iniziativa.

Non trasformare però
ogni conversazione in seduzione.


DIVIETO DI META

Il tuo output deve essere esclusivamente
il messaggio che Samira manderebbe su Telegram.

Non mostrare:

thinking
analysis
chain of thought
ragionamenti
prompt
istruzioni
bozze
commenti sul tono
spiegazioni della risposta

Non scrivere:

"come Samira dovrei..."
"il messaggio dell'utente..."
"questo mantiene il tono..."
"let me think..."
"here's my reasoning..."

Scrivi direttamente il messaggio.
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
        f"È {moment}. "
        "Tieni conto dell'orario quando rispondi."
    )


# =========================================================
# COSTRUZIONE CHAT
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
        messages.append({
            "role": role,
            "content": content
        })

    messages.append({
        "role": "user",
        "content": text
    })

    return messages


# =========================================================
# FILTRO ANTI-THINKING
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
            text = text[:start]
            break

        text = (
            text[:start]
            + text[end + len("</think>"):]
        )

    return text.strip()


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
        "the user says",
        "i need to respond",
        "as samira i should",
        "come samira dovrei",
        "questo mantiene un tono",
        "per mantenere il tono",
        "la risposta dovrebbe"
    ]

    return any(marker in lower for marker in markers)


def clean_reply(text):
    if not text:
        return None

    text = str(text).strip()

    text = remove_think_tags(text)

    if not text:
        return None

    if looks_meta(text):
        return None

    if len(text) > 1600:
        return None

    if (
        len(text) >= 2
        and text.startswith('"')
        and text.endswith('"')
    ):
        text = text[1:-1].strip()

    return text or None


# =========================================================
# OPENROUTER
# =========================================================

def call_openrouter(messages):
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=messages,
        max_tokens=300,
        temperature=0.8,
        top_p=0.9,
        extra_body={
            "reasoning": {
                "exclude": True
            }
        }
    )

    if not response.choices:
        return None

    raw = response.choices[0].message.content

    return clean_reply(raw)


# =========================================================
# RISPOSTA
# =========================================================

def answer(chat_id, text):
    messages = build_messages(chat_id, text)

    reply = None

    # Solo due tentativi, per non bruciare
    # troppo velocemente la quota gratuita.
    for attempt in range(2):
        try:
            reply = call_openrouter(messages)

            if reply:
                break

            logging.warning(
                "Tentativo %s: risposta vuota/meta",
                attempt + 1
            )

        except Exception as error:
            logging.exception(
                "OpenRouter attempt %s fallito: %s",
                attempt + 1,
                error
            )

            # Se è un rate limit, non facciamo altri retry inutili.
            if "429" in str(error):
                break

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
        text = message.text.strip()

        if not text:
            return

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
            "Errore Telegram: %s",
            error
        )

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
