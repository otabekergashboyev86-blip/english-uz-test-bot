import os
import re
import random
import unicodedata

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)


# =========================================================
# 111 TA SO'Z
# =========================================================

WORDS = [
    ("Argentina", "argentina"),
    ("Brazil", "Braziliya"),
    ("Canada", "Kanada"),
    ("Italy", "Italiya"),
    ("Japan", "Yaponiya"),
    ("Mexico", "Meksika"),
    ("Poland", "polsha"),
    ("Spain", "Ispaniya"),
    ("Thailand", "Tailand"),
    ("Great Britain", "Buyuk Britaniya"),
    ("The UK", "Qo‘shma qirolliklar (Buyuk Britaniya)"),
    ("The USA (The US)", "Amerika Qo‘shma Shtatlari"),
    ("Turkey", "Turkiya"),
    ("Flag", "bayroq"),
    ("Country", "mamlakat"),
    ("Match", "tanlamoq"),
    ("Look", "qaramoq"),
    ("Listen", "tinglamoq"),
    ("Work", "ishlamoq"),
    ("Person", "odam"),
    ("People", "odamlar"),
    ("Box", "quti"),
    ("Check", "tekshirmoq"),
    ("Repeat", "qaytarmoq"),
    ("Conversation", "muloqot"),
    ("Read", "o‘qimoq"),
    ("Sentence", "gap"),
    ("Help", "yordam bermoq"),
    ("Exercise", "mashq"),
    ("With", "bilan"),
    ("Complete", "tugatmoq"),
    ("Other", "boshqa"),
    ("Map", "xarita"),
    ("Underline", "tagiga chizmoq"),
    ("Job", "kasb, ish"),
    ("Short", "kalta"),
    ("Form", "shakl"),
    ("Question", "savol"),
    ("Answer", "javob"),
    ("Page", "sahifa, bet"),
    ("Again", "qaytadan"),
    ("Correct", "to‘g‘ri, to‘g‘rilamoq"),
    ("Example", "misol"),
    ("Alternative", "tanlov"),
    ("Tell", "gapirib bermoq"),
    ("Pronunciation", "talaffuz"),
    ("Nationality", "millat"),
    ("The same", "bir xil"),
    ("Famous", "mashhur"),
    ("Some", "ba’zi, bir nechta"),
    ("True", "to‘g‘ri"),
    ("False", "noto‘g‘ri"),
    ("Word", "so‘z"),
    ("Make", "qilmoq, yasamoq"),
    ("All", "hamma, barcha"),
    ("Photo", "rasm, surat"),
    ("Order", "tartib"),
    ("Useful phrases", "foydali iboralar"),
    ("Use", "ishlatmoq"),
    ("Partner", "sherik"),
    ("Nice to meet you", "Tanishganimdan xursandman"),
    ("Here", "bu yerda"),
    ("Conference", "konferensiya"),
    ("What’s your name?", "Ismingiz nima?"),
    ("My name is ...", "Mening ismim ..."),
    ("What’s your family name (surname)", "Familiyangiz nima?"),
    ("My family name (surname) is ...", "Mening familiyam ..."),
    ("Where are you from?", "Qayerdansiz?"),
    ("I’m from ...", "Men ...daman"),
    ("Football player", "futbolchi"),
    ("Doctor", "shifokor"),
    ("School teacher", "ustoz / o‘qituvchi"),
    ("Pilot", "uchuvchi"),
    ("Farmer", "fermer"),
    ("Nurse", "hamshira"),
    ("Taxi driver", "taksist"),
    ("Office worker", "ofis xodimi"),
    ("Hospital", "shifoxona"),
    ("Small", "kichkina"),
    ("Good", "yaxshi"),
    ("Team", "jamoa"),
    ("Manager", "menejer"),
    ("Nice", "yaxshi"),
    ("Thai", "tailandlik"),
    ("British", "Britaniyalik"),
    ("Polish", "polshalik"),
    ("Spanish", "ispaniyalik"),
    ("Turkish", "turkiyalik"),
    ("Mexican", "meksikalik"),
    ("Japanese", "yaponiyalik"),
    ("Italian", "italiyalik"),
    ("American", "amerikalik"),
    ("Canadian", "kanadalik"),
    ("Brazilian", "braziliyalik"),
    ("Argentinian", "argentinalik"),
    ("University", "universitet"),
    ("Friend", "do‘st"),
    ("All over the world", "dunyo bo‘ylab"),
    ("And", "va"),
    ("But", "lekin"),
    ("Now", "hozir"),
    ("Hotel", "mehmonxona"),
    ("What’s your phone number?", "telefon raqamingiz qanday?"),
    ("What’s your email address?", "elektron pochtangiz qanday?"),
    ("Sorry, can you say that again?", "Uzr, qaytadan ayta olasizmi?"),
    ("How do you spell (your name)?", "Harflab qanday aytiladi?"),
    ("@", "at"),
    ("Dot", "nuqta"),
    ("Class", "dars, sinf"),
    ("Late", "kech qolmoq"),
    ("Today", "bugun"),
]


# =========================================================
# BAYROQLAR
# =========================================================

FLAGS = {
    "Argentina": "🇦🇷",
    "Brazil": "🇧🇷",
    "Canada": "🇨🇦",
    "Italy": "🇮🇹",
    "Japan": "🇯🇵",
    "Mexico": "🇲🇽",
    "Poland": "🇵🇱",
    "Spain": "🇪🇸",
    "Thailand": "🇹🇭",
    "Great Britain": "🇬🇧",
    "The UK": "🇬🇧",
    "The USA (The US)": "🇺🇸",
    "Turkey": "🇹🇷",
}


ROUND_SIZE = 10


# =========================================================
# STATE
# =========================================================

# Har bir foydalanuvchining alohida testi
state = {}

# Guruhdagi faol musobaqalar
group_sessions = {}


# =========================================================
# JAVOBNI NORMALIZATSIYA QILISH
# =========================================================

def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", str(s)).lower().strip()

    # Har xil apostroflarni oddiy apostrofga aylantiramiz
    for ch in ["’", "‘", "ʻ", "ʼ", "`", "´"]:
        s = s.replace(ch, "'")

    # Bir nechta bo'sh joyni bittaga aylantiramiz
    s = re.sub(r"\s+", " ", s)

    # Oxirdagi oddiy belgilarni olib tashlash
    s = s.strip(" .!?")

    return s.strip()


# =========================================================
# TO'G'RI JAVOBNI TEKSHIRISH
# =========================================================

def is_correct(user_answer: str, expected: str) -> bool:
    user = norm(user_answer)

    expected = str(expected).strip()

    options = set()

    # Asosiy javob
    options.add(norm(expected))

    # Vergul yoki / bilan ajratilgan variantlar
    for part in re.split(r"\s*(?:,|/)\s*", expected):
        if part.strip():
            options.add(norm(part))

    # Qavs ichidagi variantlar
    match = re.search(r"([^()]*)", expected)

    if match:
        before = expected[:match.start()].strip()
        inside = match.group(1).strip()
        after = expected[match.end():].strip()

        if before or after:
            # Qavssiz
            without_parentheses = f"{before} {after}".strip()
            options.add(norm(without_parentheses))

            # Qavs ichidagi so'z bilan
            with_inside = f"{before} {inside} {after}".strip()
            options.add(norm(with_inside))

        if inside:
            options.add(norm(inside))

    return user in options


# =========================================================
# GURUHMI?
# =========================================================

def is_group(update: Update) -> bool:
    chat = update.effective_chat

    if not chat:
        return False

    return chat.type in ["group", "supergroup"]


# =========================================================
# STATE KEY
# =========================================================

def get_key(update: Update):
    return (
        update.effective_chat.id,
        update.effective_user.id,
    )


# =========================================================
# YANGI TEST STATE
# =========================================================

def new_state():
    return {
        "index": 0,

        "score": 0,

        "combo": 0,

        "longest_combo": 0,

        "round_score": 0,

        "round_wrong": [],

        "rounds": 0,

        "expected": "",

        "direction": "",

        "waiting_next_round": False,

        "nickname": "",

        "waiting_nickname": False,

        "finished": False,
    }


# =========================================================
# /START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        "👋 Assalomu alaykum!\n\n"
        "🇬🇧 English — 🇺🇿 Uzbek test botiga xush kelibsiz.\n\n"
        "📚 Jami so‘zlar: 111 ta\n"
        "📝 Har bir bosqich: 10 ta savol\n\n"
        "Buyruqlar:\n"
        "/test — testni boshlash\n"
        "/restart — testni qayta boshlash\n"
        "/score — hozirgi natijani ko‘rish"
    )

    await update.message.reply_text(text)


# =========================================================
# /TEST
# =========================================================

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):

    key = get_key(update)

    # -----------------------------
    # GURUH
    # -----------------------------

    if is_group(update):

        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        session = group_sessions.get(chat_id)

        # Agar eski musobaqa tugagan bo'lsa,
        # yangi musobaqa boshlanadi
        if session is None or session["all_finished"]:

            session = {
                "players": {},
                "all_finished": False,
            }

            group_sessions[chat_id] = session

        # Agar foydalanuvchi allaqachon testda bo'lsa
        if user_id in session["players"]:

            player = session["players"][user_id]

            if not player["finished"]:
                await update.message.reply_text(
                    "⚠️ Siz allaqachon testdasiz."
                )
                return

        # Yangi state
        s = new_state()

        s["waiting_nickname"] = True

        state[key] = s

        await update.message.reply_text(
            "👤 Avval nickname kiriting.\n\n"
            "Masalan:\n"
            "@Ali"
        )

        return

    # -----------------------------
    # PRIVATE
    # -----------------------------

    s = new_state()

    state[key] = s

    await ask(update, context)


# =========================================================
# /RESTART
# =========================================================

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):

    key = get_key(update)

    # GURUH
    if is_group(update):

        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        session = group_sessions.get(chat_id)

        if session is None:
            session = {
                "players": {},
                "all_finished": False,
            }

            group_sessions[chat_id] = session

        s = new_state()

        s["waiting_nickname"] = True

        state[key] = s

        # Eski participantni olib tashlaymiz
        session["players"].pop(user_id, None)

        session["all_finished"] = False

        await update.message.reply_text(
            "🔄 Test qayta boshlandi
