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
# 111 TA SO'Z — O'ZGARTIRILMAGAN
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
# SOZLAMALAR
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

state = {}
group_sessions = {}


# =========================================================
# JAVOB TEKSHIRISH
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

    for part in re.split(r"\s*(?:,|/)\s*", expected):
        if part.strip():
            options.add(norm(part))

    match = re.search(r"\(([^()]*)\)", expected)

    if match:
        before = expected[:match.start()].strip()
        inside = match.group(1).strip()
        after = expected[match.end():].strip()

        if before or after:
            options.add(
                norm(f"{before} {after}".strip())
            )

            options.add(
                norm(f"{before} {inside} {after}".strip())
            )

        if inside:
            options.add(norm(inside))

    return options


def is_correct(user_answer: str, expected: str) -> bool:
    options = build_options(expected)

    if norm(expected) == "yordam bermoq":
        options.add("yordam")

    return norm(user_answer) in options


# =========================================================
# YORDAMCHI FUNKSIYALAR
# =========================================================

def is_group(update: Update) -> bool:
    chat = update.effective_chat

    return bool(
        chat and chat.type in ("group", "supergroup")
    )


def get_key(update: Update):
    return (
        update.effective_chat.id,
        update.effective_user.id
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


def new_group_session(chat_id, host_id):
    return {
        "chat_id": chat_id,
        "host_id": host_id,

        "players": {},

        "lobby": True,
        "running": False,
        "finished": False,
        "all_finished": False,

        "question_index": 0,
        "question_number": 0,

        "expected": "",
        "direction": "",

        "question_message_id": None,
        "question_started_at": 0.0,
        "question_deadline": 0.0,

        "answered": set(),

        "question_task": None,
        "lobby_message_id": None,
    }


async def safe_delete(bot, chat_id, message_id):
    if not message_id:
        return

    try:
        await bot.delete_message(
            chat_id=chat_id,
            message_id=message_id
        )
    except Exception:
        pass


# =========================================================
# RENDER KEEP-ALIVE
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

        "🇬🇧 English — 🇺🇿 Uzbek test botiga "
        "xush kelibsiz!\n\n"

        f"📚 Jami so‘zlar: {len(WORDS)} ta\n"
        f"📝 Har bosqich: {ROUND_SIZE} ta savol\n"
        f"⏱️ Turnir savoli: {QUESTION_TIME} soniya\n\n"

        "Buyruqlar:\n"
        "/test — testni boshlash / turnirga qo‘shilish\n"
        "/restart — testni qayta boshlash\n"
        "/score — natijani ko‘rish\n"
        "/stop — guruhdagi turnirni to‘xtatish"
    )


# =========================================================
# /TEST
# =========================================================

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):

    key = get_key(update)

    # SHAXSIY TEST
    if not is_group(update):

        state[key] = new_state()

        await ask_private(
            update,
            context
        )

        return

    # GURUH
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    session = group_sessions.get(chat_id)

    # Turnir allaqachon boshlangan
    if session and session.get("running"):

        await update.message.reply_text(
            "⚠️ Turnir allaqachon boshlangan.\n\n"
            "Keyingi turnirda qatnashing."
        )

        return

    # Lobby mavjud
    if (
        session
        and session.get("lobby")
        and not session.get("finished")
    ):

        if user_id in session["players"]:

            await update.message.reply_text(
                "⚠️ Siz allaqachon turnirga qo‘shilgansiz."
            )

            return

        state[key] = new_state()

        state[key]["waiting_nickname"] = True

        await update.message.reply_text(
            "👤 Turnirga qo‘shilish uchun "
            "ismingizni yozing.\n\n"
            "Masalan: Otabek yoki Kumush"
        )

        return

    # YANGI TURNIR
    session = new_group_session(
        chat_id,
        user_id
    )

    group_sessions[chat_id] = session

    state[key] = new_state()

    state[key]["waiting_nickname"] = True

    await update.message.reply_text(
        "🏆 ENGLISH 🇬🇧 — UZBEK 🇺🇿 TURNIR\n\n"

        "👤 Avval ismingizni yozing.\n\n"

        "Keyin boshqalar ham qo‘shilishi mumkin.\n"

        "Hamma tayyor bo‘lgach, mezbon "
        "🚀 TURNIRNI BOSHLASH tugmasini bosadi."
    )


# =========================================================
# /RESTART
# =========================================================

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):

    key = get_key(update)

    # SHAXSIY
    if not is_group(update):

        state[key] = new_state()

        await update.message.reply_text(
            "🔄 Test qayta boshlandi!"
        )

        await ask_private(
            update,
            context
        )

        return

    # GURUH
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    session = group_sessions.get(chat_id)

    if session and session.get("running"):

        await update.message.reply_text(
            "⚠️ Turnir davom etmoqda.\n\n"
            "Turnirni to‘xtatish uchun "
            "/stop buyrug‘idan foydalaning."
        )

        return

    if session and session.get("question_task"):

        task = session.get("question_task")

        if task and not task.done():
            task.cancel()

    # YANGI TURNIR OYNASI
    session = new_group_session(
        chat_id,
        user_id
    )

    group_sessions[chat_id] = session

    state[key] = new_state()

    state[key]["waiting_nickname"] = True

    await update.message.reply_text(
        "🔄 Yangi turnir ochildi!\n\n"

        "👤 Ismingizni yozing.\n\n"

        "Keyin boshqa ishtirokchilar ham "
        "qo‘shilishi mumkin."
    )


# =========================================================
# NICKNAME RO‘YXATDAN O‘TKAZISH
# =========================================================

async def register_nickname(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if (
        not is_group(update)
        or not update.message
        or not update.message.text
    ):
        return False

    key = get_key(update)

    s = state.get(key)

    if not s or not s.get("waiting_nickname"):
        return False

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    session = group_sessions.get(chat_id)

    if (
        not session
        or not session.get("lobby")
        or session.get("running")
    ):

        s["waiting_nickname"] = False

        return False

    nickname = update.message.text.strip()

    if not nickname:
        return True

    if len(nickname) > 50:

        await update.message.reply_text(
            "⚠️ Ism juda uzun. "
            "50 ta belgigacha kiriting."
        )

        return True

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

    # Nickname xabarini o‘chirish
    try:
        await update.message.delete()
    except Exception:
        pass

    await update.effective_chat.send_message(
        f"✅ {nickname} turnirga qo‘shildi!\n\n"
        f"👥 Ishtirokchilar: "
        f"{len(session['players'])} ta"
    )

    await send_lobby_message(
        context.bot,
        session
    )

    return True


# =========================================================
# LOBBY
# =========================================================

async def send_lobby_message(
    bot,
    session
):

    chat_id = session["chat_id"]

    players = session["players"]

    count = len(players)

    lines = [
        "🏆 ENGLISH 🇬🇧 — UZBEK 🇺🇿 TURNIR",
        "━━━━━━━━━━━━━━━━━━",
        "",
        "👥 ISHTIROKCHILAR",
        "━━━━━━━━━━━━━━━━━━",
        f"👤 Hozir: {count} ta",
        "",
        "🏁 Yana odamlar qo‘shilishi mumkin.",
        "",
        "🔘 TURNIRGA QO‘SHILISH — yangi ishtirokchi",
        "🚀 TURNIRNI BOSHLASH — faqat mezbon",
        "",
        "⚠️ Turnir boshlanganidan keyin "
        "yangi ishtirokchi qo‘shilmaydi.",
    ]

    if players:

        player_list = "\n".join(
            f"{i}. {p['nickname']}"
            for i, p in enumerate(
                players.values(),
                1
            )
        )

        lines.insert(
            6,
            player_list
        )

    keyboard = InlineKeyboardMarkup([
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

    old_id = session.get(
        "lobby_message_id"
    )

    # Eski xabarni yangilash
    if old_id:

        try:

            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=old_id,
                text="\n".join(lines),
                reply_markup=keyboard,
            )

            return

        except Exception:
            pass

    # Yangi lobby xabari
    msg = await bot.send_message(
        chat_id=chat_id,
        text="\n".join(lines),
        reply_markup=keyboard,
    )

    session["lobby_message_id"] = msg.message_id


# =========================================================
# TURNIRGA QO‘SHILISH TUGMASI
# =========================================================

async def join_tournament_button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    if not query:
        return

    chat_id = query.message.chat.id
    user_id = query.from_user.id

    key = (
        chat_id,
        user_id
    )

    session = group_sessions.get(
        chat_id
    )

    if (
        not session
        or not session.get("lobby")
        or session.get("running")
    ):

        await query.answer(
            "⚠️ Hozir qo‘shilish mumkin emas.",
            show_alert=True
        )

        return

    if user_id in session["players"]:

        await query.answer(
            "Siz allaqachon qo‘shilgansiz.",
            show_alert=True
        )

        return

    state[key] = new_state()

    state[key]["waiting_nickname"] = True

    await query.answer(
        "✅ Qo‘shilish boshlandi."
    )

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "👤 Ismingizni yozing.\n\n"
            "Masalan: Otabek yoki Kumush"
        )
    )


# =========================================================
# TURNIRNI BOSHLASH
# =========================================================

async def start_tournament_button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    if not query:
        return

    chat_id = query.message.chat.id
    user_id = query.from_user.id

    session = group_sessions.get(
        chat_id
    )

    if (
        not session
        or not session.get("lobby")
        or session.get("running")
    ):

        await query.answer(
            "⚠️ Turnir allaqachon boshlangan "
            "yoki mavjud emas.",
            show_alert=True
        )

        return

    # Faqat mezbon
    if user_id != session.get("host_id"):

        await query.answer(
            "❌ Turnirni faqat mezbon boshlaydi.",
            show_alert=True
        )

        return

    if not session["players"]:

        await query.answer(
            "Avval kamida 1 ta ishtirokchi qo‘shilsin.",
            show_alert=True
        )

        return

    await query.answer(
        "🚀 Turnir boshlanmoqda!"
    )

    session["lobby"] = False
    session["running"] = True
    session["finished"] = False
    session["all_finished"] = False

    session["question_index"] = 0
    session["question_number"] = 0

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

            f"👥 Ishtirokchilar: "
            f"{len(session['players'])} ta\n"

            "🎯 Hammaga bir xil savol\n"

            f"⏱️ Har savolga {QUESTION_TIME} soniya\n"

            "🗑️ Javoblar darhol o‘chiriladi\n\n"

            "🔥 Omad!"
        )
    )

    # BIRINCHI SAVOL
    await send_group_question(
        context.bot,
        session
    )


# =========================================================
# SHAXSIY TEST SAVOLI
# =========================================================

async def ask_private(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    key = get_key(update)

    s = state.get(key)

    if not s:
        return

    if s["index"] >= len(WORDS):

        await finish_private(
            update,
            context
        )

        return

    word, uzbek = WORDS[
        s["index"]
    ]

    direction = random.choice([
        "en_uz",
        "uz_en"
    ])

    s["direction"] = direction

    if direction == "en_uz":

        s["expected"] = uzbek

        flag = FLAGS.get(
            word,
            ""
        )

        word_text = (
            f"{flag} {word}"
            if flag
            else word
        )

        question = (
            f"❓ {s['index'] + 1}/{len(WORDS)}\n\n"
            f"🇬🇧 {word_text}\n\n"
            "🇺🇿 O‘zbekchasini yozing:"
        )

    else:

        s["expected"] = word

        question = (
            f"❓ {s['index'] + 1}/{len(WORDS)}\n\n"
            f"🇺🇿 {uzbek}\n\n"
            "🇬🇧 Inglizchasini yozing:"
        )

    sent = await update.effective_chat.send_message(
        question
    )

    s["question_message_id"] = (
        sent.message_id
    )


# =========================================================
# JAVOB HANDLER
# =========================================================

async def answer(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if (
        not update.message
        or not update.message.text
    ):
        return

    # Guruh bo‘lsa — turnir
    if is_group(update):

        await group_answer(
            update,
            context
        )

        return

    # Shaxsiy test
    key = get_key(update)

    s = state.get(key)

    if (
        not s
        or s.get("waiting_nickname")
        or s.get("finished")
    ):
        return

    if s.get("waiting_next_round"):
        return

    user_answer = update.message.text.strip()

    expected = s["expected"]

    correct = is_correct(
        user_answer,
        expected
    )

    if correct:

        s["score"] += 1
        s["round_score"] += 1
        s["combo"] += 1

        s["longest_combo"] = max(
            s["longest_combo"],
            s["combo"]
        )

        result = "✅ To‘g‘ri!"

        if s["combo"] == 3:

            result += "\n\n🔥 COMBO x3!"

        elif s["combo"] == 5:

            result += "\n\n⚡ COMBO x5 — zo‘r!"

        elif (
            s["combo"] > 5
            and s["combo"] % 5 == 0
        ):

            result += (
                f"\n\n🔥 COMBO x{s['combo']}!"
            )

    else:

        s["combo"] = 0

        word, uzbek = WORDS[
            s["index"]
        ]

        s["round_wrong"].append({
            "word": word,
            "uzbek": uzbek
        })

        result = (
            "❌ Noto‘g‘ri.\n"
            f"To‘g‘ri javob: {expected}"
        )

    await update.effective_chat.send_message(
        result
    )

    s["index"] += 1

    if (
        s["index"] % ROUND_SIZE == 0
        or s["index"] >= len(WORDS)
    ):

        await private_round_result(
            update,
            context
        )

    else:

        await ask_private(
            update,
            context
        )


# =========================================================
# GURUH JAVOBI
# =========================================================

async def group_answer(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    message = update.message

    session = group_sessions.get(
        chat_id
    )

    if (
        not session
        or not session.get("running")
    ):
        return

    # Turnirga kirmagan odam
    if user_id not in session["players"]:
        return

    # Bir savolga faqat bitta javob
    if user_id in session["answered"]:

        await safe_delete(
            context.bot,
            chat_id,
            message.message_id
        )

        return

    now = time.time()

    # Vaqt tugagan
    if now > session.get(
        "question_deadline",
        0
    ):

        await safe_delete(
            context.bot,
            chat_id,
            message.message_id
        )

        return

    # Eski xabarni yangi savolga hisoblamaslik
    if message.date:

        stamp = message.date.timestamp()

        started = session.get(
            "question_started_at",
            0
        )

        deadline = session.get(
            "question_deadline",
            0
        )

        if (
            stamp < started - 2
            or stamp > deadline + 1
        ):

            await safe_delete(
                context.bot,
                chat_id,
                message.message_id
            )

            return

    # Darhol "javob berdi" deb belgilaymiz
    session["answered"].add(
        user_id
    )

    player = session["players"][
        user_id
    ]

    key = player["state_key"]

    s = state.get(key)

    # JAVOBNI DARHOL O‘CHIRISH
    await safe_delete(
        context.bot,
        chat_id,
        message.message_id
    )

    correct = is_correct(
        message.text.strip(),
        session["expected"]
    )

    player["answered"] = True

    if correct:

        player["correct"] += 1
        player["combo"] += 1

        player["longest_combo"] = max(
            player["longest_combo"],
            player["combo"]
        )

        if s:

            s["score"] += 1
            s["round_score"] += 1
            s["combo"] = player["combo"]

            s["longest_combo"] = (
                player["longest_combo"]
            )

    else:

        player["combo"] = 0

        if s:

            s["combo"] = 0

            word, uzbek = WORDS[
                session["question_index"]
            ]

            s["round_wrong"].append({
                "word": word,
                "uzbek": uzbek
            })


# =========================================================
# 10 SONIYALIK TIMER
# =========================================================

async def group_question_timeout(
    bot,
    session,
    question_token
):

    try:

        await asyncio.sleep(
            QUESTION_TIME
        )

    except asyncio.CancelledError:

        return

    if not session.get("running"):
        return

    if (
        session.get("question_number")
        != question_token
    ):
        return

    chat_id = session["chat_id"]

    question_index = (
        session["question_index"]
    )

    # SAVOLNI O‘CHIRISH
    await safe_delete(
        bot,
        chat_id,
        session.get("question_message_id")
    )

    session["question_message_id"] = None

    # Javob bermaganlar = xato
    for user_id, player in session[
        "players"
    ].items():

        player["questions"] = (
            question_index + 1
        )

        if user_id not in session[
            "answered"
        ]:

            player["combo"] = 0

            key = player[
                "state_key"
            ]

            s = state.get(key)

            if s:

                s["combo"] = 0

                word, uzbek = WORDS[
                    question_index
                ]

                s["round_wrong"].append({
                    "word": word,
                    "uzbek": uzbek
                })

        key = player[
            "state_key"
        ]

        s = state.get(key)

        if s:

            s["index"] = (
                question_index + 1
            )

            s["rounds"] = (
                (question_index + 1)
                // ROUND_SIZE
            )

    completed = question_index + 1

    session["answered"] = set()

    # HAR 10 TA SAVOLDA NATIJA
    if (
        completed % ROUND_SIZE == 0
        or completed == len(WORDS)
    ):

        await send_tournament_leaderboard(
            bot,
            session,
            completed,
            final=(
                completed == len(WORDS)
            )
        )

    # 111 tugadi
    if completed >= len(WORDS):

        await finish_group_tournament(
            bot,
            session
        )

        return

    # Keyingi savol
    session["question_index"] += 1

    await send_group_question(
        bot,
        session
    )


# =========================================================
# GURUHGA SAVOL YUBORISH
# =========================================================

async def send_group_question(
    bot,
    session
):

    if not session.get("running"):
        return

    index = session[
        "question_index"
    ]

    if index >= len(WORDS):

        await finish_group_tournament(
            bot,
            session
        )

        return

    word, uzbek = WORDS[index]

    direction = random.choice([
        "en_uz",
        "uz_en"
    ])

    session["direction"] = direction

    if direction == "en_uz":

        session["expected"] = uzbek

        flag = FLAGS.get(
            word,
            ""
        )

        word_text = (
            f"{flag} {word}"
            if flag
            else word
        )

        question = (
            f"🏆 TURNIR — "
            f"{index + 1}/{len(WORDS)}\n"
            "━━━━━━━━━━━━━━━━━━\n\n"

            "🎯 HAMMA UCHUN BIR XIL SAVOL\n"

            f"⏱️ {QUESTION_TIME} soniya\n\n"

            f"🇬🇧 {word_text}\n\n"

            "🇺🇿 O‘zbekchasini yozing:"
        )

    else:

        session["expected"] = word

        question = (
            f"🏆 TURNIR — "
            f"{index + 1}/{len(WORDS)}\n"
            "━━━━━━━━━━━━━━━━━━\n\n"

            "🎯 HAMMA UCHUN BIR XIL SAVOL\n"

            f"⏱️ {QUESTION_TIME} soniya\n\n"

            f"🇺🇿 {uzbek}\n\n"

            "🇬🇧 Inglizchasini yozing:"
        )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🛑 TURNIRNI TO‘XTATISH",
                callback_data="stop_tournament"
            )
        ]
    ])

    sent = await bot.send_message(
        chat_id=session["chat_id"],
        text=question,
        reply_markup=keyboard
    )

    session[
        "question_message_id"
    ] = sent.message_id

    session[
        "question_number"
    ] += 1

    session[
        "question_started_at"
    ] = time.time()

    session[
        "question_deadline"
    ] = (
        session["question_started_at"]
        + QUESTION_TIME
    )

    session["answered"] = set()

    old_task = session.get(
        "question_task"
    )

    if (
        old_task
        and not old_task.done()
    ):

        old_task.cancel()

    token = session[
        "question_number"
    ]

    session[
        "question_task"
    ] = asyncio.create_task(
        group_question_timeout(
            bot,
            session,
            token
        )
    )


# =========================================================
# TURNIR LEADERBOARD
# =========================================================

async def send_tournament_leaderboard(
    bot,
    session,
    completed,
    final=False
):

    players = session.get(
        "players",
        {}
    )

    if not players:
        return

    results = []

    for player in players.values():

        correct = player[
            "correct"
        ]

        percentage = (
            correct / completed * 100
            if completed
            else 0
        )

        results.append({
            "nickname": player[
                "nickname"
            ],
            "correct": correct,
            "percentage": percentage,
            "longest_combo": player[
                "longest_combo"
            ],
        })

    # Foiz bo‘yicha tartib
    results.sort(
        key=lambda x: (
            x["percentage"],
            x["correct"],
            x["longest_combo"]
        ),
        reverse=True
    )

    if final:

        title = (
            f"🏆 TURNIR YAKUNI — "
            f"{completed}/{len(WORDS)}"
        )

    else:

        title = (
            f"📊 TURNIR NATIJALARI — "
            f"{completed}/{len(WORDS)}"
        )

    medals = [
        "🥇",
        "🥈",
        "🥉"
    ]

    lines = [
        title,
        "━━━━━━━━━━━━━━━━━━",
        ""
    ]

    for i, item in enumerate(
        results,
        1
    ):

        if i <= 3:

            place = medals[i - 1]

        else:

            place = f"{i}."

        lines.append(
            f"{place} "
            f"{item['nickname']} — "
            f"{item['percentage']:.1f}% aniqlik "
            f"({item['correct']}/{completed})"
        )

    if final and results:

        lines += [
            "",
            f"👑 G‘OLIB: "
            f"{results[0]['nickname']}"
        ]

    # Ko‘p odam bo‘lsa ham Telegram limitidan oshmasin
    chunks = []

    current = ""

    for line in lines:

        if (
            len(current)
            + len(line)
            + 1
            > 3800
        ):

            chunks.append(
                current.rstrip()
            )

            current = (
                line + "\n"
            )

        else:

            current += (
                line + "\n"
            )

    if current.strip():

        chunks.append(
            current.rstrip()
        )

    for chunk in chunks:

        await bot.send_message(
            session["chat_id"],
            chunk
        )


# =========================================================
# TURNIR TUGASHI
# =========================================================

async def finish_group_tournament(
    bot,
    session
):

    if session.get("finished"):
        return

    session["running"] = False
    session["lobby"] = False
    session["finished"] = True
    session["all_finished"] = True

    task = session.get(
        "question_task"
    )

    if (
        task
        and not task.done()
    ):

        task.cancel()

    await safe_delete(
        bot,
        session["chat_id"],
        session.get(
            "question_message_id"
        )
    )

    session[
        "question_message_id"
    ] = None

    for player in session[
        "players"
    ].values():

        player["finished"] = True

        key = player[
            "state_key"
        ]

        s = state.get(key)

        if s:

            s["finished"] = True

            s["index"] = len(WORDS)

            s["rounds"] = (
                (
                    len(WORDS)
                    + ROUND_SIZE
                    - 1
                )
                // ROUND_SIZE
            )


# =========================================================
# /STOP
# =========================================================

async def stop_tournament(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not is_group(update):

        await update.message.reply_text(
            "❌ Bu buyruq faqat guruhda ishlaydi."
        )

        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    session = group_sessions.get(
        chat_id
    )

    if (
        not session
        or not session.get("running")
    ):

        await update.message.reply_text(
            "ℹ️ Hozir faol turnir yo‘q."
        )

        return

    # Faqat mezbon
    if user_id != session.get(
        "host_id"
    ):

        await update.message.reply_text(
            "❌ Turnirni faqat uni "
            "boshlagan odam to‘xtata oladi."
        )

        return

    await stop_group_session(
        context.bot,
        session
    )


# =========================================================
# TURNIRNI TO‘XTATISH
# =========================================================

async def stop_group_session(
    bot,
    session
):

    session["running"] = False
    session["lobby"] = False
    session["finished"] = True
    session["all_finished"] = True

    task = session.get(
        "question_task"
    )

    if (
        task
        and not task.done()
    ):

        task.cancel()

    await safe_delete(
        bot,
        session["chat_id"],
        session.get(
            "question_message_id"
        )
    )

    await safe_delete(
        bot,
        session["chat_id"],
        session.get(
            "lobby_message_id"
        )
    )

    session[
        "question_message_id"
    ] = None

    session[
        "lobby_message_id"
    ] = None

    for player in session[
        "players"
    ].values():

        key = player[
            "state_key"
        ]

        s = state.get(key)

        if s:

            s["finished"] = True
            s["waiting_nickname"] = False

    await bot.send_message(
        session["chat_id"],
        "🛑 TURNIR TO‘XTATILDI!\n\n"

        "❌ Ushbu turnir bekor qilindi.\n\n"

        "🔄 Yangi turnir uchun "
        "/test ni bosing."
    )


# =========================================================
# STOP TUGMASI
# =========================================================

async def stop_tournament_button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    if not query:
        return

    chat_id = query.message.chat.id
    user_id = query.from_user.id

    session = group_sessions.get(
        chat_id
    )

    if (
        not session
        or not session.get("running")
    ):

        await query.answer(
            "ℹ️ Turnir faol emas.",
            show_alert=True
        )

        return

    if user_id != session.get(
        "host_id"
    ):

        await query.answer(
            "❌ Faqat turnirni boshlagan "
            "odam to‘xtata oladi.",
            show_alert=True
        )

        return

    await query.answer(
        "🛑 Turnir to‘xtatilmoqda..."
    )

    await stop_group_session(
        context.bot,
        session
    )


# =========================================================
# SHAXSIY 10 TALIK NATIJA
# =========================================================

async def private_round_result(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    key = get_key(update)

    s = state.get(key)

    if not s:
        return

    s["rounds"] += 1

    round_number = s[
        "rounds"
    ]

    start_number = (
        (round_number - 1)
        * ROUND_SIZE
        + 1
    )

    end_number = min(
        round_number * ROUND_SIZE,
        len(WORDS)
    )

    question_count = (
        end_number
        - start_number
        + 1
    )

    percentage = (
        s["score"]
        / end_number
        * 100
    )

    text = (
        f"🏁 {round_number}-round tugadi!\n\n"

        f"📊 Natija: "
        f"{s['round_score']}/"
        f"{question_count}\n"

        f"🏆 Umumiy: "
        f"{s['score']}/"
        f"{end_number}\n"

        f"📈 Foiz: "
        f"{percentage:.1f}%\n"

        f"🔥 Combo: "
        f"x{s['combo']}\n"

        f"⚡ Eng uzun combo: "
        f"x{s['longest_combo']}"
    )

    if s["round_wrong"]:

        text += (
            "\n\n"
            "❌ XATO QILINGAN SO‘ZLAR:"
        )

        for item in s[
            "round_wrong"
        ]:

            text += (
                f"\n\n"
                f"• 🇬🇧 {item['word']}\n"
                f"  🇺🇿 {item['uzbek']}"
            )

    else:

        text += (
            "\n\n"
            "🎉 Bu bosqichda xato yo‘q!"
        )

    # TEST TUGADI
    if s["index"] >= len(WORDS):

        await update.effective_chat.send_message(
            text
        )

        await finish_private(
            update,
            context,
            already_sent=True
        )

        return

    s["waiting_next_round"] = True

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "➡️ Keyingi 10 ta",
                callback_data="next_round"
            )
        ]
    ])

    text += (
        "\n\n"
        "👇 Davom etish uchun "
        "tugmani bosing."
    )

    await update.effective_chat.send_message(
        text,
        reply_markup=keyboard
    )


# =========================================================
# PRIVATE NEXT ROUND
# =========================================================

async def next_round(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    if not query:
        return

    await query.answer()

    key = get_key(update)

    s = state.get(key)

    if (
        not s
        or not s.get(
            "waiting_next_round"
        )
    ):
        return

    s["waiting_next_round"] = False
    s["round_score"] = 0
    s["round_wrong"] = []

    await ask_private(
        update,
        context
    )


# =========================================================
# PRIVATE FINISH
# =========================================================

async def finish_private(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    already_sent=False
):

    key = get_key(update)

    s = state.get(key)

    if (
        not s
        or s.get("finished")
    ):
        return

    s["finished"] = True

    percentage = (
        s["score"]
        / len(WORDS)
        * 100
    )

    text = (
        ""
        if already_sent
        else "🎉 TEST TUGADI!\n\n"
    )

    text += (
        f"🏆 Natija: "
        f"{s['score']}/{len(WORDS)}\n"

        f"📈 Foiz: "
        f"{percentage:.1f}%\n"

        f"🔥 Eng uzun combo: "
        f"x{s['longest_combo']}\n"

        f"📚 Bosqichlar: "
        f"{s['rounds']}"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🔄 Qayta boshlash",
                callback_data="restart_game"
            )
        ]
    ])

    await update.effective_chat.send_message(
        text,
        reply_markup=keyboard
    )


# =========================================================
# /SCORE
# =========================================================

async def score(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    key = get_key(update)

    s = state.get(key)

    if not s:

        await update.message.reply_text(
            "📊 Hozircha test boshlanmagan.\n\n"
            "/test — testni boshlash"
        )

        return

    done = s["index"]

    percentage = (
        s["score"]
        / done
        * 100
        if done
        else 0
    )

    if (
        is_group(update)
        and s.get("nickname")
    ):

        title = (
            f"📊 "
            f"{s['nickname'].upper()}"
            f"'NING NATIJASI\n\n"
        )

    else:

        title = (
            "📊 SIZNING NATIJANGIZ\n\n"
        )

    await update.message.reply_text(
        title

        + f"✅ To‘g‘ri: "
        f"{s['score']}\n"

        + f"❓ Tugagan savollar: "
        f"{done}\n"

        + f"📈 Aniqlik: "
        f"{percentage:.1f}%\n"

        + f"🔥 Hozirgi combo: "
        f"x{s['combo']}\n"

        + f"⚡ Eng uzun combo: "
        f"x{s['longest_combo']}\n"

        + f"📚 Bosqichlar: "
        f"{s['rounds']}"
    )


# =========================================================
# RESTART BUTTON
# =========================================================

async def restart_game(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    if not query:
        return

    await query.answer()

    # GURUH
    if is_group(update):

        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        session = group_sessions.get(
            chat_id
        )

        if (
            session
            and session.get("running")
        ):

            await update.effective_chat.send_message(
                "⚠️ Turnir davom etmoqda.\n\n"
                "/stop orqali to‘xtating."
            )

            return

        session = new_group_session(
            chat_id,
            user_id
        )

        group_sessions[
            chat_id
        ] = session

        key = get_key(update)

        state[key] = new_state()

        state[key][
            "waiting_nickname"
        ] = True

        await update.effective_chat.send_message(
            "🔄 Yangi turnir ochildi!\n\n"

            "👤 Ismingizni yozing.\n\n"

            "Keyin boshqa ishtirokchilar "
            "ham qo‘shilishi mumkin."
        )

        return

    # SHAXSIY
    key = get_key(update)

    state[key] = new_state()

    await update.effective_chat.send_message(
        "🔄 Test qayta boshlandi!"
    )

    await ask_private(
        update,
        context
    )


# =========================================================
# TEXT HANDLER
# =========================================================

async def handle_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if (
        not update.message
        or not update.message.text
    ):
        return

    if is_group(update):

        key = get_key(update)

        s = state.get(key)

        if (
            s
            and s.get("waiting_nickname")
        ):

            if await register_nickname(
                update,
                context
            ):

                return

    await answer(
        update,
        context
    )


# =========================================================
# MAIN
# =========================================================

def main():

    token = os.environ.get(
        "BOT_TOKEN"
    )

    hostname = os.environ.get(
        "RENDER_EXTERNAL_HOSTNAME"
    )

    port = int(
        os.environ.get(
            "PORT",
            "10000"
        )
    )

    if not token:

        raise RuntimeError(
            "BOT_TOKEN topilmadi!"
        )

    if not hostname:

        raise RuntimeError(
            "RENDER_EXTERNAL_HOSTNAME "
            "topilmadi!"
        )

    application = (
        Application
        .builder()
        .token(token)
        .build()
    )

    # COMMANDS
    application.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    application.add_handler(
        CommandHandler(
            "test",
            test
        )
    )

    application.add_handler(
        CommandHandler(
            "restart",
            restart
        )
    )

    application.add_handler(
        CommandHandler(
            "score",
            score
        )
    )

    application.add_handler(
        CommandHandler(
            "stop",
            stop_tournament
        )
    )

    # CALLBACKS
    application.add_handler(
        CallbackQueryHandler(
            next_round,
            pattern="^next_round$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            restart_game,
            pattern="^restart_game$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            join_tournament_button,
            pattern="^join_tournament$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            start_tournament_button,
            pattern="^start_tournament$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            stop_tournament_button,
            pattern="^stop_tournament$"
        )
    )

    # TEXT
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_text
        )
    )

    # RENDER WEBHOOK
    webhook_path = "telegram"

    webhook_url = (
        f"https://{hostname}/"
        f"{webhook_path}"
    )

    # Render keep-alive
    keep_render_awake(
        f"https://{hostname}/"
    )

    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=webhook_path,
        webhook_url=webhook_url,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
