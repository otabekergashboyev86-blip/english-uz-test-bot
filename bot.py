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
# OLDINGI 111 TA + YANGI 39 TA
# =========================================================

WORDS = [
    # =========================
    # 1–111 — OLDINGI SO'ZLAR
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
    # 112–150 — YANGI SO'ZLAR
    # =========================

    ("About", "haqida"),
    ("Father", "ota, dada"),
    ("Mother", "ona"),
    ("Parents", "ota-ona"),
    ("Grandfather", "bobo"),
    ("Grandmother", "buvi"),
    ("Son", "o‘g‘il"),
    ("Daughter", "qiz"),
    ("Child", "bola, farzand"),
    ("Children", "bolalar, farzandlar"),
    ("Uncle", "amaki, tog‘a"),
    ("Aunt", "xola, amma"),
    ("Cousin(e)", "amakivachcha, xolavachcha"),
    ("Nephew", "jiyan (o‘g‘il bola)"),
    ("Niece", "jiyan (qiz bola)"),
    ("Husband", "eri"),
    ("Wife", "xotin"),
    ("Desk", "parta"),
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
    ("How many", "nechta"),
    ("How much", "qancha"),
    ("How much is this?", "nechi pul bu?"),
    ("How much are these?", "nechi pul bo‘ladi?"),
    ("Can I pay by card?", "kartadan to‘lasam bo‘ladimi?"),
    ("Here you are", "mana, marhamat"),
    ("Here is your change", "mana, qaytimingiz"),
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
TOURNAMENT_SECONDS = 10

# Private test
state = {}

# Guruh turnirlari
group_sessions = {}


# =========================================================
# JAVOBNI TEKSHIRISH
# =========================================================

def norm(s: str) -> str:
    """
    Javoblarni juda yumshoq tekshiradi.

    1. Katta/kichik harf farqi yo‘q.
    2. x va h bir xil hisoblanadi.
    3. o‘ / o' / ʻ / ʼ va boshqa apostroflar bir xil.
    4. Ortiqcha bo‘sh joylar farq qilmaydi.
    5. Oxiridagi . ! ? farq qilmaydi.
    """

    s = unicodedata.normalize(
        "NFKC",
        str(s)
    ).casefold().strip()

    # Apostrof variantlari
    for ch in [
        "’", "‘", "ʻ", "ʼ",
        "`", "´", "′", "＇"
    ]:
        s = s.replace(ch, "'")

    # X va H bir xil
    s = s.replace("x", "h")

    # Har xil tirelar
    for ch in [
        "–", "—", "−", "-"
    ]:
        s = s.replace(ch, "-")

    # Ortiqcha bo‘sh joy
    s = re.sub(
        r"\s+",
        " ",
        s
    )

    # Vergul/slash atrofidagi bo‘sh joy
    s = re.sub(
        r"\s*,\s*",
        ",",
        s
    )

    s = re.sub(
        r"\s*/\s*",
        "/",
        s
    )

    return s.strip(" .!?")


def build_options(expected: str):
    expected = str(expected).strip()

    options = {
        norm(expected)
    }

    # Vergul va / orqali berilgan variantlar
    for part in re.split(
        r"\s*(?:,|/)\s*",
        expected
    ):
        part = part.strip()

        if part:
            options.add(
                norm(part)
            )

    # Qavs ichidagi variantlar
    while True:

        match = re.search(
            r"([^()]*)",
            expected
        )

        if not match:
            break

        before = expected[
            :match.start()
        ].strip()

        inside = match.group(1).strip()

        after = expected[
            match.end():
        ].strip()

        if before or after:

            options.add(
                norm(
                    f"{before} {after}".strip()
                )
            )

            options.add(
                norm(
                    f"{before} {inside} {after}".strip()
                )
            )

        if inside:
            options.add(
                norm(inside)
            )

        expected = (
            f"{before} {after}"
        ).strip()

    # Maxsus variant
    if norm(expected) == "yordam bermoq":
        options.add("yordam")

    return options


def is_correct(
    user_answer: str,
    expected: str
) -> bool:

    return (
        norm(user_answer)
        in build_options(expected)
    )


# =========================================================
# YORDAMCHI FUNKSIYALAR
# =========================================================

def is_group(update: Update) -> bool:

    chat = update.effective_chat

    return bool(
        chat
        and chat.type in (
            "group",
            "supergroup"
        )
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


def new_group_session():

    return {
        "players": {},

        "running": False,
        "all_finished": False,

        "question_index": 0,

        "question_message_id": None,

        "expected": "",
        "direction": "",

        "answered": set(),

        "question_started_at": 0.0,
        "question_deadline": 0.0,

        "question_task": None,

        "lobby_message_id": None,
    }


async def safe_delete(
    bot,
    chat_id,
    message_id
):

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
# RENDER UYQUG‘ON
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

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(

        "👋 Assalomu alaykum!\n\n"

        "🇬🇧 English — 🇺🇿 Uzbek test botiga xush kelibsiz!\n\n"

        f"📚 Jami so‘zlar: {len(WORDS)} ta\n"
        f"📝 Har bosqich: {ROUND_SIZE} ta savol\n\n"

        "Buyruqlar:\n"

        "/test — testni boshlash\n"
        "/restart — testni qayta boshlash\n"
        "/score — natijani ko‘rish\n"
        "/stop_tournament — guruh turnirini to‘xtatish"
    )


# =========================================================
# TURNIR LOBBYSI
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
        ]

    ])


def lobby_text(session):

    players = session["players"]

    names = [
        p["nickname"]
        for p in players.values()
    ]

    text = (

        "🏆 ENGLISH 🇬🇧 — UZBEK 🇺🇿 TURNIR\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        f"👥 ISHTIROKCHILAR: {len(names)} ta\n\n"
    )

    if names:

        text += "\n".join(
            f"• {name}"
            for name in names
        )

    else:

        text += (
            "Hozircha hech kim qo‘shilmagan."
        )

    text += (

        "\n\n━━━━━━━━━━━━━━━━━━\n"

        "🏁 Istagancha odam turnirga qo‘shilishi mumkin.\n"

        "Har bir ishtirokchi o‘z ismini yozadi.\n\n"

        "🚀 Hamma tayyor bo‘lgach, "
        "TURNIRNI BOSHLASH tugmasini bosing."
    )

    return text


async def refresh_lobby(
    update,
    context,
    session
):

    chat_id = update.effective_chat.id

    message_id = (
        session.get(
            "lobby_message_id"
        )
    )

    if message_id:

        try:

            await context.bot.edit_message_text(

                chat_id=chat_id,

                message_id=message_id,

                text=lobby_text(
                    session
                ),

                reply_markup=lobby_keyboard()
            )

            return

        except Exception:

            session[
                "lobby_message_id"
            ] = None

    msg = await update.effective_chat.send_message(

        lobby_text(session),

        reply_markup=lobby_keyboard()
    )

    session[
        "lobby_message_id"
    ] = msg.message_id


# =========================================================
# /TEST
# =========================================================

async def test(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    key = get_key(update)

    # =========================
    # GURUH
    # =========================

    if is_group(update):

        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        session = group_sessions.get(
            chat_id
        )

        # Turnir davom etayotgan bo‘lsa
        if session and session["running"]:

            await update.message.reply_text(

                "⚠️ Turnir allaqachon boshlangan.\n\n"
                "Keyingi turnirda qatnashing."
            )

            return

        # Eski turnir tugagan bo‘lsa
        if session and session["all_finished"]:

            session = new_group_session()

            group_sessions[
                chat_id
            ] = session

        # Yangi session
        if session is None:

            session = new_group_session()

            group_sessions[
                chat_id
            ] = session

        # Allaqachon qo‘shilgan
        if user_id in session["players"]:

            await refresh_lobby(
                update,
                context,
                session
            )

            return

        # Ism kutish
        state[key] = new_state()

        state[key][
            "waiting_nickname"
        ] = True

        await update.message.reply_text(

            "👤 Ismingizni yozing.\n\n"
            "Masalan: Otabek yoki Kumush"
        )

        return

    # =========================
    # PRIVATE
    # =========================

    state[key] = new_state()

    await ask_private(
        update,
        context
    )


# =========================================================
# /RESTART
# =========================================================

async def restart(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    key = get_key(update)

    if is_group(update):

        session = group_sessions.get(
            update.effective_chat.id
        )

        if session and session["running"]:

            await update.message.reply_text(

                "⚠️ Turnir davom etmoqda.\n\n"
                "To‘xtatish uchun:\n"
                "/stop_tournament"
            )

            return

        if session:

            session[
                "players"
            ].pop(
                update.effective_user.id,
                None
            )

        state[key] = new_state()

        state[key][
            "waiting_nickname"
        ] = True

        await update.message.reply_text(

            "🔄 Qayta qo‘shilish uchun "
            "ismingizni yozing.\n\n"

            "Masalan: Otabek yoki Kumush"
        )

        return

    state[key] = new_state()

    await update.message.reply_text(
        "🔄 Test qayta boshlandi!"
    )

    await ask_private(
        update,
        context
    )


# =========================================================
# TURNIRNI TO‘XTATISH
# =========================================================

async def stop_tournament(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not is_group(update):

        await update.message.reply_text(
            "ℹ️ Bu buyruq faqat guruh turniri uchun."
        )

        return

    chat_id = update.effective_chat.id

    session = group_sessions.get(
        chat_id
    )

    if not session or not session["running"]:

        await update.message.reply_text(
            "ℹ️ Hozir faol turnir yo‘q."
        )

        return

    task = session.get(
        "question_task"
    )

    if task and not task.done():

        task.cancel()

    await safe_delete(

        context.bot,

        chat_id,

        session.get(
            "question_message_id"
        )
    )

    session["running"] = False

    session["all_finished"] = True

    session[
        "question_message_id"
    ] = None

    for player in session[
        "players"
    ].values():

        player["finished"] = True

    await update.message.reply_text(

        "🛑 TURNIR TO‘XTATILDI!\n\n"

        "Yangi turnir boshlash uchun "
        "/test buyrug‘ini bosing."
    )


# =========================================================
# ISMNI RO‘YXATDAN O‘TKAZISH
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

    if not s or not s[
        "waiting_nickname"
    ]:

        return False

    nickname = (
        update.message.text
        .strip()
    )

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

    session = group_sessions.get(
        chat_id
    )

    if not session or session["running"]:

        await safe_delete(

            context.bot,
            chat_id,
            update.message.message_id
        )

        return True

    s["nickname"] = nickname

    s[
        "waiting_nickname"
    ] = False

    s["finished"] = False

    session[
        "players"
    ][user_id] = {

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

    # Ism yozilgan xabarni o‘chirish
    await safe_delete(

        context.bot,

        chat_id,

        update.message.message_id
    )

    await update.effective_chat.send_message(

        f"✅ {nickname} turnirga qo‘shildi!\n"

        f"👥 Jami ishtirokchilar: "
        f"{len(session['players'])} ta"
    )

    await refresh_lobby(
        update,
        context,
        session
    )

    return True


# =========================================================
# TURNIRGA QO‘SHILISH TUGMASI
# =========================================================

async def join_tournament(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    if not query:
        return

    await query.answer()

    if not is_group(update):
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    key = get_key(update)

    session = group_sessions.get(
        chat_id
    )

    if not session:

        await query.message.reply_text(
            "⚠️ Avval /test buyrug‘ini bosing."
        )

        return

    if session["running"]:

        await query.message.reply_text(
            "⚠️ Turnir allaqachon boshlangan."
        )

        return

    if session["all_finished"]:

        await query.message.reply_text(

            "ℹ️ Bu turnir tugagan.\n"
            "Yangi turnir uchun /test bosing."
        )

        return

    if user_id in session["players"]:

        await query.message.reply_text(
            "✅ Siz allaqachon turnirdasiz."
        )

        return

    state[key] = new_state()

    state[key][
        "waiting_nickname"
    ] = True

    await query.message.reply_text(

        "👤 Ismingizni yozing.\n\n"

        "Masalan: Otabek yoki Kumush"
    )


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

    if not is_group(update):
        return

    chat_id = update.effective_chat.id

    session = group_sessions.get(
        chat_id
    )

    if not session or not session[
        "players"
    ]:

        await query.message.reply_text(

            "⚠️ Avval kamida 1 ta "
            "ishtirokchi qo‘shilsin."
        )

        return

    if session["running"]:

        await query.message.reply_text(
            "⚠️ Turnir allaqachon boshlangan."
        )

        return

    session["running"] = True

    session["all_finished"] = False

    session["question_index"] = 0

    await safe_delete(

        context.bot,

        chat_id,

        session.get(
            "lobby_message_id"
        )
    )

    session[
        "lobby_message_id"
    ] = None

    await update.effective_chat.send_message(

        "🚀 TURNIR BOSHLANDI!\n\n"

        f"👥 Ishtirokchilar: "
        f"{len(session['players'])} ta\n"

        "🎯 Hamma uchun BIR XIL savol.\n"

        "⏱️ Har savolga 10 soniya.\n"

        "🗑️ Javoblar darhol o‘chiriladi.\n"

        "🏆 Har 10 savolda reyting chiqadi."
    )

    await send_group_question(
        update.effective_chat,
        context,
        session
    )


# =========================================================
# PRIVATE SAVOL
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

    s[
        "direction"
    ] = direction

    if direction == "en_uz":

        s[
            "expected"
        ] = uzbek

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

            f"❓ "
            f"{s['index'] + 1}/"
            f"{len(WORDS)}\n\n"

            f"🇬🇧 {word_text}\n\n"

            "🇺🇿 O‘zbekchasini yozing:"
        )

    else:

        s[
            "expected"
        ] = word

        question = (

            f"❓ "
            f"{s['index'] + 1}/"
            f"{len(WORDS)}\n\n"

            f"🇺🇿 {uzbek}\n\n"

            "🇬🇧 Inglizchasini yozing:"
        )

    sent = await update.effective_chat.send_message(
        question
    )

    s[
        "question_message_id"
    ] = sent.message_id


# =========================================================
# PRIVATE JAVOB
# =========================================================

async def answer_private(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if (
        not update.message
        or not update.message.text
    ):
        return

    key = get_key(update)

    s = state.get(key)

    if (
        not s
        or s["waiting_nickname"]
        or s["finished"]
    ):
        return

    if s["waiting_next_round"]:
        return

    user_answer = (
        update.message.text.strip()
    )

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

            result += (
                "\n\n🔥 COMBO x3!"
            )

        elif s["combo"] == 5:

            result += (
                "\n\n⚡ COMBO x5 — zo‘r!"
            )

        elif (
