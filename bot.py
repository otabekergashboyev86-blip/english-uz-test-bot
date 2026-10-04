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

assert len(WORDS) == 111


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
TOURNAMENT_TIME = 10

state = {}
group_sessions = {}


# =========================================================
# YORDAMCHI FUNKSIYALAR
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

    # Vergul yoki / orqali berilgan variantlar
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

    # "yordam" ham "yordam bermoq" uchun to'g'ri
    if norm(expected) == "yordam bermoq":
        options.add("yordam")

    return norm(user_answer) in options


def is_group(update: Update) -> bool:
    chat = update.effective_chat
    return bool(chat and chat.type in ("group", "supergroup"))


def get_key(update: Update):
    return (update.effective_chat.id, update.effective_user.id)


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


# =========================================================
# RENDER KEEP ALIVE
# =========================================================

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
        f"📝 Har bosqich: {ROUND_SIZE} ta savol\n\n"
        "Buyruqlar:\n"
        "/test — testni boshlash\n"
        "/restart — testni qayta boshlash\n"
        "/score — natijani ko‘rish"
    )


# =========================================================
# GROUP SESSION YARATISH
# =========================================================

def create_group_session(chat_id):

    session = {
        "players": {},

        "all_finished": False,

        # Turnir holati
        "running": False,
        "question_index": 0,
        "question_message_id": None,
        "expected": "",
        "direction": "",
        "answered": set(),

        # Savol vaqti
        "question_started": 0,
        "question_deadline": 0,

        # Tasklar
        "timer_task": None,
        "lobby_task": None,

        # Himoya
        "question_token": 0,

        # Ro'yxatdan o'tish
        "lobby_started": False,
    }

    group_sessions[chat_id] = session

    return session


async def cancel_task(task):
    if task:
        try:
            task.cancel()
            await asyncio.gather(
                task,
                return_exceptions=True
            )
        except Exception:
            pass


# =========================================================
# TEST
# =========================================================

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    # -----------------------------------------------------
    # GROUP
    # -----------------------------------------------------

    if is_group(update):

        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        session = group_sessions.get(chat_id)

        # Oldingi turnir tugagan bo'lsa yangi turnir
        if session and session.get("all_finished"):
            await cancel_task(session.get("timer_task"))
            await cancel_task(session.get("lobby_task"))

            group_sessions.pop(chat_id, None)
            session = None

        # Turnir allaqachon boshlangan
        if session and session.get("running"):
            await update.message.reply_text(
                "⚠️ Turnir allaqachon boshlangan.\n\n"
                "Keyingi turnirda qatnashish uchun kuting."
            )
            return

        if session is None:
            session = create_group_session(chat_id)

        # Shu odam allaqachon ro'yxatda
        if user_id in session["players"]:
            nickname = session["players"][user_id]["nickname"]

            await update.message.reply_text(
                f"✅ {nickname}, siz allaqachon ro‘yxatdan o‘tgansiz."
            )
            return

        key = get_key(update)

        state[key] = new_state()
        state[key]["waiting_nickname"] = True

        await update.message.reply_text(
            "👤 Ismingizni yozing.\n\n"
            "Masalan: Otabek yoki Kumush"
        )

        return

    # -----------------------------------------------------
    # PRIVATE
    # -----------------------------------------------------

    key = get_key(update)

    state[key] = new_state()

    await update.message.reply_text(
        "🚀 Test boshlandi!\n\n"
        f"📚 Jami: {len(WORDS)} ta so‘z\n"
        f"📝 Har bosqich: {ROUND_SIZE} ta savol"
    )

    await ask(update, context)


# =========================================================
# RESTART
# =========================================================

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    if is_group(update):

        chat_id = update.effective_chat.id

        session = group_sessions.get(chat_id)

        if session and session.get("running"):
            await update.message.reply_text(
                "⚠️ Turnir davom etmoqda.\n\n"
                "Turnir tugagach yangi turnir boshlashingiz mumkin."
            )
            return

        key = get_key(update)

        state[key] = new_state()
        state[key]["waiting_nickname"] = True

        await update.message.reply_text(
            "🔄 Test qayta boshlandi!\n\n"
            "👤 Ismingizni yozing.\n\n"
            "Masalan: Otabek yoki Kumush"
        )

        return

    key = get_key(update)

    state[key] = new_state()

    await update.message.reply_text(
        "🔄 Test qayta boshlandi!\n\n"
        "🚀 Yangi test boshlanmoqda..."
    )

    await ask(update, context)


# =========================================================
# NICKNAME
# =========================================================

async def register_nickname(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    nickname: str
):

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    key = get_key(update)

    nickname = nickname.strip()

    if not nickname:
        return

    if len(nickname) > 50:
        await update.message.reply_text(
            "❌ Ism juda uzun.\n"
            "50 ta belgidan oshmasin."
        )
        return

    session = group_sessions.get(chat_id)

    if session is None:
        session = create_group_session(chat_id)

    if session.get("running"):
        await update.message.reply_text(
            "⚠️ Turnir allaqachon boshlangan."
        )
        return

    # Takroriy user
    if user_id in session["players"]:
        await update.message.reply_text(
            "✅ Siz allaqachon ro‘yxatdan o‘tgansiz."
        )
        return

    # User state
    if key not in state:
        state[key] = new_state()

    state[key]["waiting_nickname"] = False
    state[key]["nickname"] = nickname

    # Player
    session["players"][user_id] = {
        "nickname": nickname,
        "state_key": key,
        "finished": False,

        "score": 0,
        "correct": 0,
        "questions": 0,

        "combo": 0,
        "longest_combo": 0,

        "round_score": 0,
        "round_wrong": [],

        "answered": False,
    }

    try:
        await update.message.delete()
    except Exception:
        pass

    count = len(session["players"])

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            f"✅ {nickname} ro‘yxatdan o‘tdi!\n\n"
            f"👥 Ishtirokchilar: {count} ta\n\n"
            "🏆 TURNIR\n"
            "Hamma uchun bir xil savol beriladi.\n"
            "Har savolga 10 soniya vaqt beriladi.\n\n"
            "⏳ Ishtirokchilar qo‘shilmoqda..."
        )
    )

    # Birinchi odam ro'yxatdan o'tganda lobby timer boshlanadi
    if not session.get("lobby_started"):

        session["lobby_started"] = True

        session["lobby_task"] = asyncio.create_task(
            group_lobby_timer(
                context.application,
                chat_id
            )
        )


# =========================================================
# LOBBY TIMER
# =========================================================

async def group_lobby_timer(
    application: Application,
    chat_id: int
):

    try:

        await asyncio.sleep(10)

        session = group_sessions.get(chat_id)

        if not session:
            return

        if session.get("running"):
            return

        if session.get("all_finished"):
            return

        if not session["players"]:
            return

        session["running"] = True
        session["question_index"] = 0
        session["all_finished"] = False

        await application.bot.send_message(
            chat_id=chat_id,
            text=(
                "🏆 TURNIR BOSHLANDI!\n\n"
                f"👥 Ishtirokchilar: {len(session['players'])} ta\n"
                "🎯 Hammaga bitta xil savol beriladi.\n"
                "⏱️ Har savol: 10 soniya."
            )
        )

        await asyncio.sleep(1)

        await send_group_question(
            application,
            chat_id
        )

    except asyncio.CancelledError:
        pass

    except Exception:
        pass


# =========================================================
# GROUP QUESTION
# =========================================================

def build_group_question(
    index: int,
    direction: str
):

    word, uzbek = WORDS[index]

    flag = FLAGS.get(word, "")

    if direction == "en_to_uz":

        question = (
            f"🏆 TURNIR — {index + 1}/{len(WORDS)}\n\n"
            f"⏱️ {TOURNAMENT_TIME} soniya\n\n"
            f"🇬🇧 {flag} {word}\n\n"
            "🇺🇿 O‘zbekchasini yozing:"
        )

    else:

        question = (
            f"🏆 TURNIR — {index + 1}/{len(WORDS)}\n\n"
            f"⏱️ {TOURNAMENT_TIME} soniya\n\n"
            f"🇺🇿 {uzbek}\n\n"
            f"🇬🇧 Inglizchasini yozing:"
        )

    return question


async def send_group_question(
    application: Application,
    chat_id: int
):

    session = group_sessions.get(chat_id)

    if not session:
        return

    if not session.get("running"):
        return

    index = session["question_index"]

    if index >= len(WORDS):
        await finish_group_tournament(
            application,
            chat_id
        )
        return

    # Old timer
    await cancel_task(session.get("timer_task"))

    direction = random.choice([
        "en_to_uz",
        "uz_to_en"
    ])

    word, uzbek = WORDS[index]

    if direction == "en_to_uz":
        expected = uzbek
    else:
        expected = word

    session["direction"] = direction
    session["expected"] = expected

    session["answered"] = set()

    session["question_token"] += 1
    token = session["question_token"]

    # Har bir player uchun yangi savol
    for player in session["players"].values():
        player["answered"] = False

    question_text = build_group_question(
        index,
        direction
    )

    message = await application.bot.send_message(
        chat_id=chat_id,
        text=question_text
    )

    session["question_message_id"] = message.message_id

    session["question_started"] = time.time()
    session["question_deadline"] = (
        session["question_started"] + TOURNAMENT_TIME
    )

    session["timer_task"] = asyncio.create_task(
        group_question_timer(
            application,
            chat_id,
            token
        )
    )


# =========================================================
# GROUP QUESTION TIMER
# =========================================================

async def group_question_timer(
    application: Application,
    chat_id: int,
    token: int
):

    try:

        await asyncio.sleep(TOURNAMENT_TIME)

        session = group_sessions.get
