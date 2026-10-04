import os
import re
import random
import unicodedata
import threading
import time
import urllib.request
import asyncio

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
# 150 TA SO'Z
# OLDINGI 111 TA O'ZGARTIRILMAGAN
# + 112-150 YANGI SO'ZLAR
# =========================================================

WORDS = [
    # =========================
    # OLDINGI 111 TA
    # =========================

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

    # =========================
    # 112-150 YANGI SO'ZLAR
    # =========================

    ("About", "haqida"),
    ("Father", "ota, dada"),
    ("Mother", "ona, oyi"),
    ("Parents", "ota-ona"),
    ("Grandfather", "bobo"),
    ("Grandmother", "buvi"),
    ("Son", "o‘g‘il, o‘g‘il farzand"),
    ("Daughter", "qiz, qiz farzand"),
    ("Child", "bola, farzand"),
    ("Children", "bolalar, farzandlar"),
    ("Uncle", "amaki, tog‘a"),
    ("Aunt", "xola, amma"),
    ("Cousin(e)", "amakivachcha, xolavachcha"),
    ("Nephew", "jiyan, o‘g‘il jiyan"),
    ("Niece", "jiyan, qiz jiyan"),
    ("Husband", "er, eri"),
    ("Wife", "xotin, rafiqa"),
    ("Deck", "parrak"),
    ("Table", "stol"),
    ("Chair", "stul"),
    ("Key", "kalit"),
    ("Clock", "soat"),
    ("Cup", "krujka"),
    ("Who", "kim"),
    ("Whose", "kimning"),
    ("What", "nima, qanday"),
    ("Where", "qayer"),
    ("When", "qachon"),
    ("Why", "nimaga"),
    ("How", "qanday qilib"),
    ("How often", "nechi marta, qancha tez-tez"),
    ("How many", "nechta, qancha"),
    ("How much", "qancha"),
    ("How much is this?", "nechi pul bu?"),
    ("How much are these?", "nechi pul?"),
    ("Can I pay by card?", "kartadan to‘lasam bo‘ladimi?"),
    ("Here you are", "mana, marhamat"),
    ("Here is your change", "mana, qaytim"),
    ("Cash or card?", "naqd pulmi yoki karta?"),
]

assert len(WORDS) == 150


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
QUESTION_TIME = 10

# Shaxsiy testlar
state = {}

# Guruh turnirlari
group_sessions = {}


# =========================================================
# NORMALIZATSIYA
# =========================================================

def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", str(s)).lower().strip()

    for ch in ["’", "‘", "ʻ", "ʼ", "`", "´"]:
        s = s.replace(ch, "'")

    s = re.sub(r"\s+", " ", s)

    return s.strip(" .!?")


def build_options(expected: str):
    expected = str(expected).strip()

    options = {norm(expected)}

    # Vergul yoki / bilan ajratilgan javoblar
    for part in re.split(r"\s*(?:,|/)\s*", expected):
        if part.strip():
            options.add(norm(part))

    # Qavs ichidagi variantlarni ham qabul qilish
    match = re.search(r"([^()]*)", expected)

    if match:
        before = expected[:match.start()].strip()
        inside = match.group(1).strip()
        after = expected[match.end():].strip()

        if before or after:
            options.add(norm(f"{before} {after}".strip()))
            options.add(norm(f"{before} {inside} {after}".strip()))

        if inside:
            options.add(norm(inside))

    return options


def is_correct(user_answer: str, expected: str) -> bool:
    options = build_options(expected)

    # Eski maxsus qoida
    if norm(expected) == "yordam bermoq":
        options.add("yordam")

    return norm(user_answer) in options


# =========================================================
# YORDAMCHI FUNKSIYALAR
# =========================================================

def is_group(update: Update) -> bool:
    chat = update.effective_chat
    return bool(chat and chat.type in ("group", "supergroup"))


def get_key(update: Update):
    return (
        update.effective_chat.id,
        update.effective_user.id,
    )


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
        "waiting_nickname": False,
        "nickname": "",
        "finished": False,
        "question_message_id": None,
    }


def new_group_session():
    return {
        "players": {},

        "running": False,
        "all_finished": False,

        "lobby_message_id": None,

        "question_index": 0,
        "question_message_id": None,
        "question_expected": "",
        "question_direction": "",

        "answered": set(),

        "question_started": 0.0,
        "question_deadline": 0.0,

        "timer_task": None,
    }


async def safe_delete(bot, chat_id, message_id):
    if not message_id:
        return

    try:
        await bot.delete_message(
            chat_id=chat_id,
            message_id=message_id,
        )
    except Exception:
        pass


def keep_render_awake(url: str):
    def ping_loop():
        while True:
            try:
                urllib.request.urlopen(
                    url,
                    timeout=20
                ).close()
            except Exception:
                pass

            time.sleep(600)

    threading.Thread(
        target=ping_loop,
        daemon=True
    ).start()


# =========================================================
# START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "👋 Assalomu alaykum!\n\n"
        "🇬🇧 English — 🇺🇿 Uzbek test botiga xush kelibsiz!\n\n"
        f"📚 Jami so‘zlar: {len(WORDS)} ta\n"
        f"📝 Har bosqich: {ROUND_SIZE} ta savol\n"
        "⏱️ Turnir savoli: 10 soniya\n\n"
        "Buyruqlar:\n"
        "/test — testni boshlash\n"
        "/restart — qayta boshlash\n"
        "/score — natijani ko‘rish\n"
        "/stop — guruh turnirini to‘xtatish"
    )


# =========================================================
# GURUH LOBBYSI
# =========================================================

def lobby_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🏁 TURNIRGA QO‘SHILISH",
                callback_data="join_tournament"
            )
        ],
        [
            InlineKeyboardButton(
                "🚀 TURNIRNI BOSHLASH",
                callback_data="start_tournament"
            )
        ],
    ])


async def create_lobby(chat_id, context):

    session = group_sessions.get(chat_id)

    if not session:
        session = new_group_session()
        group_sessions[chat_id] = session

    text = (
        "🏆 ENGLISH 🇬🇧 — UZBEK 🇺🇿\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "👥 ISHTIROKCHILAR\n\n"
        f"👤 Hozir: {len(session['players'])} ta\n\n"
        "🏁 Turnirga qo‘shilish uchun pastdagi tugmani bosing.\n"
        "Har bir ishtirokchi o‘z ismini yozadi.\n\n"
        "🚀 Hamma tayyor bo‘lgach,\n"
        "TURNIRNI BOSHLASH tugmasini bosing.\n\n"
        "♾️ Istalgancha odam qatnashishi mumkin!"
    )

    sent = await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=lobby_keyboard(),
    )

    session["lobby_message_id"] = sent.message_id


async def update_lobby(chat_id, context):

    session = group_sessions.get(chat_id)

    if not session:
        return

    message_id = session.get("lobby_message_id")

    if not message_id:
        return

    text = (
        "🏆 ENGLISH 🇬🇧 — UZBEK 🇺🇿\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "👥 ISHTIROKCHILAR\n\n"
        f"👤 Hozir: {len(session['players'])} ta\n\n"
        "🏁 Turnirga qo‘shilish uchun pastdagi tugmani bosing.\n"
        "Har bir ishtirokchi o‘z ismini yozadi.\n\n"
        "🚀 Hamma tayyor bo‘lgach,\n"
        "TURNIRNI BOSHLASH tugmasini bosing.\n\n"
        "♾️ Istalgancha odam qatnashishi mumkin!"
    )

    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=lobby_keyboard(),
        )
    except Exception:
        pass


# =========================================================
# /TEST
# =========================================================

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):

    key = get_key(update)

    # =========================
    # GURUH
    # =========================

    if is_group(update):

        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        session = group_sessions.get(chat_id)

        if session and session["running"]:
            await update.message.reply_text(
                "⚠️ Turnir allaqachon boshlangan.\n\n"
                "Keyingi turnirda qatnashing."
            )
            return

        if session and session["all_finished"]:
            session = new_group_session()
            group_sessions[chat_id] = session

        if not session:
            session = new_group_session()
            group_sessions[chat_id] = session

        if user_id in session["players"]:
            await update.message.reply_text(
                "⚠️ Siz allaqachon turnirga qo‘shilgansiz."
            )
            return

        state[key] = new_state()
        state[key]["waiting_nickname"] = True

        if not session.get("lobby_message_id"):
            await create_lobby(chat_id, context)

        await update.message.reply_text(
            "👤 Ismingizni yozing.\n\n"
            "Masalan: Otabek yoki Kumush"
        )

        return

    # =========================
    # SHAXSIY TEST
    # =========================

    state[key] = new_state()

    await ask(update, context)


# =========================================================
# TURNIRGA QO‘SHILISH
# =========================================================

async def join_tournament(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    if not query:
        return

    await query.answer()

    chat = update.effective_chat
    user = update.effective_user

    if not chat or chat.type not in ("group", "supergroup"):
        return

    chat_id = chat.id
    user_id = user.id

    session = group_sessions.get(chat_id)

    if not session:
        session = new_group_session()
        group_sessions[chat_id] = session

    if session["running"]:
        await query.message.reply_text(
            "⚠️ Turnir allaqachon boshlangan."
        )
        return

    if user_id in session["players"]:
        await query.message.reply_text(
            "⚠️ Siz allaqachon turnirga qo‘shilgansiz."
        )
        return

    key = (chat_id, user_id)

    state[key] = new_state()
    state[key]["waiting_nickname"] = True

    await query.message.reply_text(
        "👤 Ismingizni yozing.\n\n"
        "Masalan: Otabek yoki Kumush"
    )


# =========================================================
# ISMNI RO‘YXATDAN O‘TKAZISH
# =========================================================

async def register_nickname(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not is_group(update):
        return False

    if not update.message or not update.message.text:
        return False

    key = get_key(update)

    s = state.get(key)

    if not s or not s["waiting_nickname"]:
        return False

    nickname = update.message.text.strip()

    if not nickname:
        return True

    if len(nickname) > 50:
        await update.message.reply_text(
            "⚠️ Ism juda uzun.\n"
            "50 ta belgigacha kiriting."
        )
        return True

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    session = group_sessions.get(chat_id)

    if not session:
        session = new_group_session()
        group_sessions[chat_id] = session

    if session["running"]:
        s["waiting_nickname"] = False

        await update.message.reply_text(
            "⚠️ Turnir allaqachon boshlangan."
        )
        return True

    # Ismni saqlash
    s["nickname"] = nickname
    s["waiting_nickname"] = False
    s["finished"] = False

    session["players"][user_id] = {
        "nickname": nickname,
        "state_key": key,
        "finished": False,
        "correct": 0,
        "questions": 0,
        "combo": 0,
        "longest_combo": 0,
        "answered": False,
    }

    # Ism xabarini o‘chirish
    try:
        await update.message.delete()
    except Exception:
        pass

    await update.effective_chat.send_message(
        f"✅ {nickname} turnirga qo‘shildi!\n\n"
        f"👥 Ishtirokchilar: {len(session['players'])} ta"
    )

    await update_lobby(chat_id, context)

    return True


# =========================================================
# TURNIRNI BOSHLASH
# =========================================================

async def start_tournament(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    if not query:
        return

    await query.answer()

    chat = update.effective_chat

    if not chat or chat.type not in ("group", "supergroup"):
        return

    chat_id = chat.id

    session = group_sessions.get(chat_id)

    if not session:
        return

    if session["running"]:
        await query.message.reply_text(
            "⚠️ Turnir allaqachon boshlangan."
        )
        return

    if not session["players"]:
        await query.message.reply_text(
            "⚠️ Avval kamida 1 ta ishtirokchi qo‘shilishi kerak."
        )
        return

    session["running"] = True
    session["all_finished"] = False

    # Lobby xabarini o‘chirish
    await safe_delete(
        context.bot,
        chat_id,
        session.get("lobby_message_id")
    )

    session["lobby_message_id"] = None

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "🚀 TURNIR BOSHLANDI!\n\n"
            f"👥 Ishtirokchilar: {len(session['players'])} ta\n\n"
            "🎯 Hamma uchun bir xil savol.\n"
            "⏱️ Har savolga 10 soniya.\n"
            "🗑 Javoblar darhol o‘chiriladi.\n\n"
            "🔥 Omad!"
        )
    )

    await send_group_question(chat_id, context)


# =========================================================
# GURUH SAVOLI
# =========================================================

async def send_group_question(
    chat_id,
    context: ContextTypes.DEFAULT_TYPE
):

    session = group_sessions.get(chat_id)

    if not session or not session["running"]:
        return

    index = session["question_index"]

    if index >= len(WORDS):
        await finish_group_tournament(
            chat_id,
            context
        )
        return

    word, uzbek = WORDS[index]

    direction = random.choice([
        "en_uz",
        "uz_en",
    ])

    session["question_direction"] = direction

    if direction == "en_uz":

        session["question_expected"] = uzbek

        flag = FLAGS.get(word, "")

        if flag:
            word_text = f"{flag} {word}"
        else:
            word_text = word

        question = (
            f"❓ SAVOL {index + 1}/{len(WORDS)}\n\n"
            f"🇬🇧 {word_text}\n\n"
            "🇺🇿 O‘zbekchasini yozing:"
        )

    else:

        session["question_expected"] = word

        question = (
            f"❓ SAVOL {index + 1}/{len(WORDS)}\n\n"
            f"🇺🇿 {uzbek}\n\n"
            "🇬🇧 Inglizchasini yozing:"
        )

    # Oldingi javoblar ro‘yxatini tozalash
    session["answered"] = set()

    # Vaqt
    session["question_started"] = time.time()
    session["question_deadline"] = (
        session["question_started"] + QUESTION_TIME
    )

    sent = await context.bot.send_message(
        chat_id=chat_id,
        text=question,
    )

    session["question_message_id"] = sent.message_id

    # Eski timer bo‘lsa bekor qilamiz
    old_task = session.get("timer_task")

    if old_task and not old_task.done():
        old_task.cancel()

    # Yangi 10 soniyalik timer
    session["timer_task"] = asyncio.create_task(
        group_question_timer(
            chat_id,
            index,
            context,
        )
    )


# =========================================================
# 10 SONIYALIK TIMER
# =========================================================

async def group_question_timer(
    chat_id,
    question_index,
    context
):

    try:
        await asyncio.sleep(QUESTION_TIME)

        session = group_sessions.get(chat_id)

        if not session:
            return

        if not session["running"]:
            return

        # Eski timer bo‘lsa ishlamasin
        if session["question_index"] != question_index:
            return

        # Savolni o‘chirish
        await safe_delete(
            context.bot,
            chat_id,
            session.get("question_message_id")
        )

        session["question_message_id"] = None

        # Shu savol raqami
        completed = question_index + 1

        # Javob bermaganlarni noto‘g‘ri hisoblaymiz
        for user_id, player in session["players"].items():

            key = player["state_key"]

            s = state.get(key)

            if not s:
                continue

            player["questions"] = completed

            # Javob bermagan bo‘lsa combo buziladi
            if user_id not in session["answered"]:

                player["combo"] = 0

                s["combo"] = 0

                word, uzbek = WORDS[question_index]

                s["round_wrong"].append({
                    "word": word,
                    "uzbek": uzbek,
                })

            s["index"] = completed

            s["rounds"] = completed // ROUND_SIZE

        # Har 10 ta savolda reyting
        if completed % ROUND_SIZE == 0:

            await send_group_leaderboard(
                chat_id,
                completed,
                context,
                final=False,
            )

            # Yangi bosqich uchun round ma'lumotlarini tozalash
            for player in session["players"].values():

                key = player["state_key"]

                s = state.get(key)

                if s:
                    s["round_score"] = 0
                    s["round_wrong"] = []

        # 150-savol tugagan bo‘lsa
        if completed >= len(WORDS):

            await finish_group_tournament(
                chat_id,
                context
            )

            return

        # Keyingi savol
        session["question_index"] += 1

        await send_group_question(
            chat_id,
            context
        )

    except asyncio.CancelledError:
        return

    except Exception:
        return


# =========================================================
# GURUH JAVOBI
# =========================================================

async def group_answer(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    session = group_sessions.get(chat_id)

    if not session or not session["running"]:
        return

    player = session["players"].get(user_id)

    # Turnir ishtirokchisi bo‘lmasa
    if not player:
        return

    # Javob xabarini darhol o‘chirish
    message_id = update.message.message_id

    await safe_delete(
        context.bot,
        chat_id,
        message_id
    )

    # Bir savolga faqat 1 marta javob
    if user_id in session["answered"]:
        return

    # Savol vaqti tugagan bo‘lsa
    now = time.time()

    if now > session["question_deadline"]:
        return

    # Telegram xabar vaqti bilan ham tekshirish
    if update.message.date:

        try:
            message_timestamp = update.message.date.timestamp()

            if message_timestamp < (
                session["question_started"] - 2
            ):
                return

            if message_timestamp > (
                session["question_deadline"] + 1
            ):
                return

        except Exception:
            pass

    # Javob berilgan deb belgilaymiz
    session["answered"].add(user_id)

    s = state.get(player["state_key"])

    if not s:
        return

    expected = session["question_expected"]

    user_answer = update.message.text.strip()

    correct = is_correct(
        user_answer,
        expected
    )

    completed = session["question_index"] + 1

    player["questions"] = completed

    s["index"] = completed

    if correct:

        player["correct"] += 1

        player["combo"] += 1

        player["longest_combo"] = max(
            player["longest_combo"],
            player["combo"]
        )

        s["score"] += 1
        s["round_score"] += 1
        s["combo"] = player["combo"]
        s["longest_combo"] = max(
            s["longest_combo"],
            player["combo"]
        )

    else:

        player["combo"] = 0
        s["combo"] = 
