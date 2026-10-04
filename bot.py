import os
import re
import random
import unicodedata
import threading
import time
import urllib.request
import asyncio

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
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
QUESTION_TIME = 10

state = {}
group_sessions = {}


# =========================================================
# NORMALIZATION
# =========================================================

def norm(s: str) -> str:
    s = unicodedata.normalize(
        "NFKC",
        str(s)
    ).lower().strip()

    for ch in [
        "’",
        "‘",
        "ʻ",
        "ʼ",
        "`",
        "´",
    ]:
        s = s.replace(ch, "'")

    s = re.sub(
        r"\s+",
        " ",
        s
    )

    return s.strip(" .!?")


def build_options(expected: str):

    expected = str(expected).strip()

    options = {
        norm(expected)
    }

    # Vergul / orqali berilgan variantlar
    for part in re.split(
        r"\s*(?:,|/)\s*",
        expected
    ):
        if part.strip():
            options.add(
                norm(part)
            )

    # Qavs ichidagi variantlar
    match = re.search(
        r"\(([^()]*)\)",
        expected
    )

    if match:

        before = expected[
            :match.start()
        ].strip()

        inside = match.group(
            1
        ).strip()

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

    return options


def is_correct(
    user_answer: str,
    expected: str
) -> bool:

    options = build_options(
        expected
    )

    # "yordam" ham to'g'ri
    if norm(expected) == "yordam bermoq":
        options.add("yordam")

    return norm(
        user_answer
    ) in options


# =========================================================
# GENERAL
# =========================================================

def is_group(update: Update) -> bool:

    chat = update.effective_chat

    return bool(
        chat
        and chat.type in (
            "group",
            "supergroup",
        )
    )


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
            message_id=message_id,
        )

    except Exception:
        pass


async def cancel_task(task):

    if task is None:
        return

    if task.done():
        return

    try:

        task.cancel()

        await asyncio.gather(
            task,
            return_exceptions=True
        )

    except Exception:
        pass


# =========================================================
# GROUP SESSION
# =========================================================

def create_group_session(
    chat_id,
    host_id
):

    return {
        "chat_id": chat_id,

        # Turnirni boshlagan odam
        "host_id": host_id,

        # user_id -> player
        "players": {},

        # Lobby
        "lobby": True,
        "running": False,
        "finished": False,

        # Savol
        "question_index": 0,
        "question_message_id": None,
        "expected": "",
        "direction": "",
        "question_started": 0,
        "question_deadline": 0,

        # Javob berganlar
        "answered": set(),

        # Timer
        "question_task": None,

        # Har savol uchun unique token
        "question_token": 0,
    }


# =========================================================
# START
# =========================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "👋 Assalomu alaykum!\n\n"
        "🇬🇧 English 🇺🇿 Uzbek test botiga "
        "xush kelibsiz!\n\n"
        f"📚 Jami so‘zlar: {len(WORDS)} ta\n"
        "🎮 Guruhda turnir ham mavjud.\n\n"
        "Buyruqlar:\n"
        "/test — testni boshlash\n"
        "/restart — qayta boshlash\n"
        "/score — natijani ko‘rish"
    )


# =========================================================
# GROUP LOBBY MESSAGE
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


async def send_lobby(
    bot,
    chat_id
):

    session = group_sessions.get(
        chat_id
    )

    if not session:
        return

    count = len(
        session["players"]
    )

    text = (
        "🏆 ENGLISH 🇬🇧 — UZBEK 🇺🇿\n"
        "       TURNIR\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "👥 ISHTIROKCHILAR\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 Hozir: {count} ta\n\n"
        "🏁 Turnirga qo‘shilish uchun "
        "pastdagi tugmani bosing.\n\n"
        "Har bir ishtirokchi o‘z ismini "
        "yozadi.\n\n"
        "🚀 Hamma tayyor bo‘lgach, "
        "TURNIRNI BOSHLASH tugmasini bosing."
    )

    await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=lobby_keyboard()
    )


# =========================================================
# /TEST
# =========================================================

async def test(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    # -----------------------------------------------------
    # GROUP
    # -----------------------------------------------------

    if is_group(update):

        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        session = group_sessions.get(
            chat_id
        )

        # Yangi turnir
        if (
            session is None
            or session.get("finished")
        ):

            session = create_group_session(
                chat_id,
                user_id
            )

            group_sessions[
                chat_id
            ] = session

            await update.message.reply_text(
                "🏆 Yangi turnir yaratildi!"
            )

            await ask_group_nickname(
                update,
                context
            )

            return

        # Turnir davom etmoqda
        if session["running"]:

            await update.message.reply_text(
                "⚠️ Turnir allaqachon boshlangan.\n\n"
                "Keyingi turnirda qatnashing."
            )

            return

        # Lobbyda
        if user_id in session["players"]:

            await update.message.reply_text(
                "✅ Siz allaqachon "
                "turnirga qo‘shilgansiz."
            )

            return

        await ask_group_nickname(
            update,
            context
        )

        return

    # -----------------------------------------------------
    # PRIVATE
    # -----------------------------------------------------

    key = get_key(update)

    state[key] = new_state()

    await update.message.reply_text(
        "🚀 Test boshlandi!\n\n"
        f"📚 Jami: {len(WORDS)} ta so‘z"
    )

    await ask(
        update,
        context
    )


# =========================================================
# ASK GROUP NICKNAME
# =========================================================

async def ask_group_nickname(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    key = get_key(update)

    if key not in state:
        state[key] = new_state()

    state[key][
        "waiting_nickname"
    ] = True

    await update.effective_chat.send_message(
        "👤 Turnirga qo‘shilish uchun "
        "ismingizni yozing.\n\n"
        "Masalan: Otabek"
    )


# =========================================================
# REGISTER GROUP PLAYER
# =========================================================

async def register_group_player(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    key = get_key(update)

    nickname = (
        update.message.text or ""
    ).strip()

    if not nickname:
        return

    if len(nickname) > 40:

        await update.message.reply_text(
            "❌ Ism 40 ta belgidan oshmasin."
        )

        return

    session = group_sessions.get(
        chat_id
    )

    if not session:
        return

    if session["running"]:

        try:
            await update.message.delete()
        except Exception:
            pass

        return

    if user_id in session["players"]:

        try:
            await update.message.delete()
        except Exception:
            pass

        return

    # User state
    if key not in state:
        state[key] = new_state()

    state[key][
        "waiting_nickname"
    ] = False

    state[key][
        "nickname"
    ] = nickname

    session["players"][
        user_id
    ] = {
        "user_id": user_id,
        "nickname": nickname,

        "state_key": key,

        "correct": 0,
        "questions": 0,
        "score": 0,

        "combo": 0,
        "longest_combo": 0,

        "round_score": 0,
        "round_wrong": [],

        "answered": False,
        "finished": False,
    }

    # Nickname xabarini o'chirish
    try:
        await update.message.delete()
    except Exception:
        pass

    count = len(
        session["players"]
    )

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            f"✅ {nickname} turnirga qo‘shildi!\n\n"
            f"👥 Ishtirokchilar: {count} ta\n\n"
            "🏁 Yana odamlar qo‘shilishi mumkin."
        )
    )

    # Lobby tugmasini yangilash
    await send_lobby(
        context.bot,
        chat_id
    )


# =========================================================
# JOIN BUTTON
# =========================================================

async def join_tournament(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    chat_id = query.message.chat.id
    user_id = query.from_user.id

    session = group_sessions.get(
        chat_id
    )

    if not session:
        return

    if session["running"]:

        await query.answer(
            "Turnir allaqachon boshlandi!",
            show_alert=True
        )

        return

    if session["finished"]:

        await query.answer(
            "Bu turnir tugagan.",
            show_alert=True
        )

        return

    if user_id in session["players"]:

        await query.answer(
            "Siz allaqachon qo‘shilgansiz.",
            show_alert=True
        )

        return

    key = (
        chat_id,
        user_id
    )

    if key not in state:
        state[key] = new_state()

    state[key][
        "waiting_nickname"
    ] = True

    await query.message.reply_text(
        f"👤 {query.from_user.first_name}, "
        "turnirga qo‘shilish uchun "
        "ismingizni yozing."
    )


# =========================================================
# START TOURNAMENT BUTTON
# =========================================================

async def start_tournament(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    chat_id = query.message.chat.id
    user_id = query.from_user.id

    session = group_sessions.get(
        chat_id
    )

    if not session:
        return

    # Faqat turnirni ochgan odam boshlaydi
    if user_id != session["host_id"]:

        await query.answer(
            "❌ Turnirni faqat uni ochgan odam boshlashi mumkin.",
            show_alert=True
        )

        return

    if session["running"]:

        await query.answer(
            "Turnir allaqachon boshlangan.",
            show_alert=True
        )

        return

    if session["finished"]:

        await query.answer(
            "Bu turnir tugagan.",
            show_alert=True
        )

        return

    count = len(
        session["players"]
    )

    if count == 0:

        await query.answer(
            "Avval kamida 1 ta ishtirokchi qo‘shilsin.",
            show_alert=True
        )

        return

    session["lobby"] = False
    session["running"] = True

    await query.message.reply_text(
        "🚀 TURNIR BOSHLANDI!\n\n"
        f"👥 Ishtirokchilar: {count} ta\n\n"
        "🎯 Hamma uchun bir xil savol.\n"
        "⏱️ Har savolga 10 soniya.\n"
        "🗑️ Javoblar darhol o‘chiriladi.\n\n"
        "🔥 Omad!"
    )

    await asyncio.sleep(1)

    await send_group_question(
        context.application,
        chat_id
    )


# =========================================================
# GROUP QUESTION
# =========================================================

async def send_group_question(
    application,
    chat_id
):

    session = group_sessions.get(
        chat_id
    )

    if not session:
        return

    if not session["running"]:
        return

    index = session[
        "question_index"
    ]

    if index >= len(WORDS):

        await finish_group(
            application,
            chat_id
        )

        return

    # Eski timer
    await cancel_task(
        session.get(
            "question_task"
        )
    )

    # Bir xil yo'nalish — hamma uchun
    direction = random.choice([
        "en_to_uz",
        "uz_to_en",
    ])

    word, uzbek = WORDS[index]

    session[
        "direction"
    ] = direction

    if direction == "en_to_uz":

        expected = uzbek
        flag = FLAGS.get(
            word,
            ""
        )

        question = (
            "🏆 ENGLISH 🇬🇧 — UZBEK 🇺🇿\n"
            "        TURNIR\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"🎯 SAVOL {index + 1}/{len(WORDS)}\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"🇬🇧 {flag} {word}\n\n"
            "🇺🇿 O‘zbekchasini yozing\n\n"
            "⏱️ 10 soniya"
        )

    else:

        expected = word

        question = (
            "🏆 ENGLISH 🇬🇧 — UZBEK 🇺🇿\n"
            "        TURNIR\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"🎯 SAVOL {index + 1}/{len(WORDS)}\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"🇺🇿 {uzbek}\n\n"
            "🇬🇧 Inglizchasini yozing\n\n"
            "⏱️ 10 soniya"
        )

    session[
        "expected"
    ] = expected

    session[
        "answered"
    ] = set()

    # Har bir odamni yangi savolga tayyorlash
    for player in session[
        "players"
    ].values():

        player[
            "answered"
        ] = False

    # Token
    session[
        "question_token"
    ] += 1

    token = session[
        "question_token"
    ]

    message = await application.bot.send_message(
        chat_id=chat_id,
        text=question
    )

    session[
        "question_message_id"
    ] = message.message_id

    started = time.time()

    session[
        "question_started"
    ] = started

    session[
        "question_deadline"
    ] = started + QUESTION_TIME

    session[
        "question_task"
    ] = asyncio.create_task(
        question_timeout(
            application,
            chat_id,
            token
        )
    )


# =========================================================
# QUESTION TIMEOUT
# =========================================================

async def question_timeout(
    application,
    chat_id,
    token
):

    try:

        await asyncio.sleep(
            QUESTION_TIME
        )

        session = group_sessions.get(
            chat_id
        )

        if not session:
            return

        if not session["running"]:
            return

        if session[
            "question_token"
        ] != token:
            return

        # Savolni o'chirish
        await safe_delete(
            application.bot,
            chat_id,
            session[
                "question_message_id"
            ]
        )

        session[
            "question_message_id"
        ] = None

        completed = (
            session["question_index"]
            + 1
        )

        # Javob bermaganlar — xato
        for player in session[
            "players"
        ].values():

            if not player[
                "answered"
            ]:

                player[
                    "combo"
                ] = 0

                player[
                    "round_wrong"
                ].append(
                    WORDS[
                        session[
                            "question_index"
                        ]
                    ][0]
                )

            player[
                "questions"
            ] = completed

            key = player[
                "state_key"
            ]

            if key in state:

                s = state[key]

                s[
                    "index"
                ] = completed

                s[
                    "score"
                ] = player[
                    "score"
                ]

                s[
                    "combo"
                ] = player[
                    "combo"
                ]

                s[
                    "longest_combo"
                ] = player[
                    "longest_combo"
                ]

        # Savol raqamini oshirish
        session[
            "question_index"
        ] += 1

        # Har 10 ta savolda natija
        if completed % ROUND_SIZE == 0:

            await send_leaderboard(
                application,
                chat_id,
                completed,
                final=False
            )

            await asyncio.sleep(1)

        # 111 tugadi
        if completed >= len(WORDS):

            await finish_group(
                application,
                chat_id
            )

            return

        # Keyingi savol
        await send_group_question(
            application,
            chat_id
        )

    except asyncio.CancelledError:
        pass

    except Exception:
        pass


# =========================================================
# GROUP ANSWER
# =========================================================

async def group_answer(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    session = group_sessions.get(
        chat_id
    )

    if not session:
        return

    if not session["running"]:
        return

    player = session[
        "players"
    ].get(user_id)

    # Turnir qatnashchisi emas
    if not player:
        return

    # Javob xabarini DARHOL o'chirish
    try:

        await update.message.delete()

    except Exception:
        pass

    # Vaqt tugagan bo'lsa
    if time.time() > session[
        "question_deadline"
    ]:

        return

    # Bir savolga bir marta
    if user_id in session[
        "answered"
    ]:

        return

    # Xabar vaqtini tekshirish
    try:

        message_time = (
            update.message.date.timestamp()
        )

        started = session[
            "question_started"
        ]

        deadline = session[
            "question_deadline"
        ]

        if message_time < started - 2:
            return

        if message_time > deadline + 1:
            return

    except Exception:
        pass

    # Javob berilgan
    session[
        "answered"
    ].add(user_id)

    player[
        "answered"
    ] = True

    user_answer = (
        update.message.text or ""
    )

    expected = session[
        "expected"
    ]

    correct = is_correct(
        user_answer,
        expected
    )

    key = player[
        "state_key"
    ]

    if correct:

        player[
            "correct"
        ] += 1

        player[
            "score"
        ] += 1

        player[
            "combo"
        ] += 1

        player[
            "round_score"
        ] += 1

        if player[
            "combo"
        ] > player[
            "longest_combo"
        ]:

            player[
                "longest_combo"
            ] = player[
                "combo"
            ]

        if key in state:

            s = state[key]

            s[
                "score"
            ] = player[
                "score"
            ]

            s[
                "combo"
            ] = player[
                "combo"
            ]

            s[
                "longest_combo"
            ] = player[
                "longest_combo"
            ]

    else:

        player[
            "combo"
        ] = 0

        player[
            "round_wrong"
        ].append(
            WORDS[
                session[
                    "question_index"
                ]
            ][0]
        )

        if key in state:

            state[key][
                "combo"
            ] = 0

    # Guruhga to'g'ri/noto'g'ri javob yuborilmaydi.
    # Shuning uchun javoblar oshkor qilinmaydi.


# =========================================================
# LEADERBOARD
# =========================================================

def accuracy(
    player,
    total_questions
):

    if total_questions <= 0:
        return 0

    return (
        player["correct"]
        / total_questions
    ) * 100


def leaderboard_players(
    session,
    total_questions
):

    players = list(
        session[
            "players"
        ].values()
    )

    players.sort(
        key=lambda p: (
            accuracy(
                p,
                total_questions
            ),
            p["correct"],
            p["longest_combo"],
        ),
        reverse=True
    )

    return players


def position_icon(position):

    if position == 1:
        return "🥇"

    if position == 2:
        return "🥈"

    if position == 3:
        return "🥉"

    return f"{position}️⃣"


async def send_leaderboard(
    application,
    chat_id,
    total_questions,
    final=False
):

    session = group_sessions.get(
        chat_id
    )

    if not session:
        return

    players = leaderboard_players(
        session,
        total_questions
    )

    if final:

        title = (
            "🏆🏆🏆 TURNIR YAKUNI 🏆🏆🏆"
        )

    else:

        title = (
            "📊 TURNIR NATIJALARI"
        )

    lines = [
        title,
        "",
        "━━━━━━━━━━━━━━━━━━",
        f"🎯 {total_questions}/{len(WORDS)}",
        f"👥 {len(players)} ta ishtirokchi",
        "━━━━━━━━━━━━━━━━━━",
        "",
    ]

    for position, player in enumerate(
        players,
        start=1
    ):

        percent = accuracy(
            player,
            total_questions
        )

        if percent.is_integer():

            percent_text = str(
                int(percent)
            )

        else:

            percent_text = (
                f"{percent:.1f}"
            )

        icon = position_icon(
            position
        )

        lines.append(
            f"{icon} {player['nickname']} — "
            f"{player['correct']}/{total_questions} "
            f"• {percent_text}%"
        )

    # Telegram limit
    chunks = []
    current = ""

    for line in lines:

        if (
            current
            and len(current) + len(line) + 1
            > 3800
        ):

            chunks.append(
                current
            )

            current = line

        else:

            if current:
                current += "\n"

            current += line

    if current:
        chunks.append(
            current
        )

    for chunk in chunks:

        await application.bot.send_message(
            chat_id=chat_id,
            text=chunk
        )


# =========================================================
# FINISH GROUP
# =========================================================

async def finish_group(
    application,
    chat_id
):

    session = group_sessions.get(
        chat_id
    )

    if not session:
        return

    if session["finished"]:
        return

    session[
        "running"
    ] = False

    session[
        "lobby"
    ] = False

    session[
        "finished"
    ] = True

    await cancel_task(
        session.get(
            "question_task"
        )
    )

    # Savolni o'chirish
    await safe_delete(
        application.bot,
        chat_id,
        session[
            "question_message_id"
        ]
    )

    session[
        "question_message_id"
    ] = None

    # Hamma player tugadi
    for player in session[
        "players"
    ].values():

        player[
            "finished"
        ] = True

        key = player[
            "state_key"
        ]

        if key in state:

            state[key][
                "finished"
            ] = True

            state[key][
                "index"
            ] = len(WORDS)

            state[key][
                "score"
            ] = player[
                "score"
            ]

    await asyncio.sleep(1)

    # FINAL REYTING
    await send_leaderboard(
        application,
        chat_id,
        len(WORDS),
        final=True
    )

    await application.bot.send_message(
        chat_id=chat_id,
        text=(
            "🎉 TURNIR YAKUNLANDI!\n\n"
            "🔄 Yangi turnir ochish uchun "
            "/test ni bosing."
        )
    )


# =========================================================
# PRIVATE ASK
# =========================================================

async def ask(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    key = get_key(update)

    if key not in state:
        state[key] = new_state()

    s = state[key]

    if s["finished"]:
        return

    index = s["index"]

    if index >= len(WORDS):

        await finish_private(
            update,
            context
        )

        return

    word, uzbek = WORDS[index]

    direction = random.choice([
        "en_to_uz",
        "uz_to_en",
    ])

    s[
        "direction"
    ] = direction

    flag = FLAGS.get(
        word,
        ""
    )

    if direction == "en_to_uz":

        expected = uzbek

        text = (
            f"❓ {index + 1}/{len(WORDS)}\n\n"
            f"🇬🇧 {flag} {word}\n\n"
            "🇺🇿 O‘zbekchasini yozing:"
        )

    else:

        expected = word

        text = (
            f"❓ {index + 1}/{len(WORDS)}\n\n"
            f"🇺🇿 {uzbek}\n\n"
            "🇬🇧 Inglizchasini yozing:"
        )

    s[
        "expected"
    ] = expected

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text
    )

    s[
        "question_message_id"
    ] = message.message_id


# =========================================================
# PRIVATE ANSWER
# =========================================================

async def private_answer(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    key = get_key(update)

    if key not in state:
        return

    s = state[key]

    if s["waiting_nickname"]:
        return

    if s["finished"]:
        return

    if s["waiting_next_round"]:
        return

    user_answer = (
        update.message.text or ""
    )

    expected = s[
        "expected"
    ]

    correct = is_correct(
        user_answer,
        expected
    )

    if correct:

        s[
            "score"
        ] += 1

        s[
            "round_score"
        ] += 1

        s[
            "combo"
        ] += 1

        if s[
            "combo"
        ] > s[
            "longest_combo"
        ]:

            s[
                "longest_combo"
            ] = s[
                "combo"
            ]

        result = "✅ To‘g‘ri!"

        if s["combo"] >= 3:

            if s["combo"] == 3:

                result += (
                    "\n🔥 COMBO x3!"
                )

            elif s["combo"] == 5:

                result += (
                    "\n⚡ COMBO x5 — zo‘r!"
                )

            elif s["combo"] % 5 == 0:

                result += (
                    f"\n🔥 COMBO x{s['combo']}!"
                )

    else:

        s[
            "combo"
        ] = 0

        s[
            "round_wrong"
        ].append(
            WORDS[
                s["index"]
            ][0]
        )

        result = (
            "❌ Noto‘g‘ri!\n\n"
            f"✅ To‘g‘ri javob: {expected}"
        )

    await update.message.reply_text(
        result
    )

    await safe_delete(
        context.bot,
        update.effective_chat.id,
        s[
            "question_message_id"
        ]
    )

    s[
        "question_message_id"
    ] = None

    s[
        "index"
    ] += 1

    if s["index"] >= len(WORDS):

        await finish_private(
            update,
            context
        )

        return

    if (
        s["index"] % ROUND_SIZE == 0
    ):

        await private_round_result(
            update,
            context
        )

        return

    await ask(
        update,
        context
    )


# =========================================================
# ANSWER ROUTER
# =========================================================

async def answer(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if is_group(update):

        await group_answer(
            update,
            context
        )

    else:

        await private_answer(
            update,
            context
        )


# =========================================================
# PRIVATE ROUND RESULT
# =========================================================

async def private_round_result(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    key = get_key(update)

    s = state[key]

    s[
        "rounds"
    ] += 1

    s[
        "waiting_next_round"
    ] = True

    text = (
        f"🏁 {s['rounds']}-bosqich tugadi!\n\n"
        f"🎯 Natija: "
        f"{s['round_score']}/{ROUND_SIZE}\n"
        f"📊 Umumiy: "
        f"{s['score']}/{s['index']}\n"
    )

    if s[
        "round_wrong"
    ]:

        text += (
            "\n❌ Xato javoblar:\n"
        )

        for word in s[
            "round_wrong"
        ]:

            text += (
                f"• {word}\n"
            )

    else:

        text += (
            "\n🔥 Xato yo‘q!"
        )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "▶️ Keyingi 10 ta",
                callback_data="next_round"
            )
        ]
    ])

    await update.effective_chat.send_message(
        text,
        reply_markup=keyboard
    )


# =========================================================
# NEXT PRIVATE ROUND
# =========================================================

async def next_round(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    key = (
        query.message.chat.id,
        query.from_user.id,
    )

    if key not in state:
        return

    s = state[key]

    if not s[
        "waiting_next_round"
    ]:

        return

    s[
        "waiting_next_round"
    ] = False

    s[
        "round_score"
    ] = 0

    s[
        "round_wrong"
    ] = []

    try:
        await query.message.delete()
    except Exception:
        pass

    # Fake update orqali keyingi savol
    await ask(
        update,
        context
    )


# =========================================================
# PRIVATE FINISH
# =========================================================

async def finish_private(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    key = get_key(update)

    if key not in state:
        return

    s = state[key]

    s[
        "finished"
    ] = True

    score_value = s[
        "score"
    ]

    total = len(WORDS)

    percent = (
        score_value / total * 100
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🔄 Qaytadan boshlash",
                callback_data="restart_game"
            )
        ]
    ])

    await update.effective_chat.send_message(
        "🎉 TEST TUGADI!\n\n"
        f"🎯 Natijangiz: "
        f"{score_value}/{total}\n"
        f"📊 Foiz: {percent:.1f}%\n"
        f"🔥 Eng uzun combo: "
        f"{s['longest_combo']}\n\n"
        "👏 Barakalla!",
        reply_markup=keyboard
    )


# =========================================================
# /RESTART
# =========================================================

async def restart(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if is_group(update):

        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        session = group_sessions.get(
            chat_id
        )

        if session and session[
            "running"
        ]:

            await update.message.reply_text(
                "⚠️ Turnir davom etmoqda."
            )

            return

        # Yangi lobby
        session = create_group_session(
            chat_id,
            user_id
        )

        group_sessions[
            chat_id
        ] = session

        await update.message.reply_text(
            "🔄 Yangi turnir yaratildi!"
        )

        await ask_group_nickname(
            update,
            context
        )

        return

    # PRIVATE
    key = get_key(update)

    state[key] = new_state()

    await update.message.reply_text(
        "🔄 Test qayta boshlandi!"
    )

    await ask(
        update,
        context
    )


# =========================================================
# /SCORE
# =========================================================

async def score(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    key = get_key(update)

    # GROUP
    if is_group(update):

        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        session = group_sessions.get(
            chat_id
        )

        if not session:

            await update.message.reply_text(
                "Avval /test bosing."
            )

            return

        player = session[
            "players"
        ].get(user_id)

        if not player:

            await update.message.reply_text(
                "Siz turnirga qo‘shilmagansiz."
            )

            return

        questions = max(
            0,
            session[
                "question_index"
            ]
        )

        percent = accuracy(
            player,
            questions
        )

        await update.message.reply_text(
            "📊 SIZNING NATIJANGIZ\n\n"
            f"👤 {player['nickname']}\n"
            f"🎯 {player['correct']}/{questions}\n"
            f"📈 Aniqlik: {percent:.1f}%\n"
            f"🔥 Eng uzun combo: "
            f"{player['longest_combo']}"
        )

        return

    # PRIVATE
    if key not in state:

        await update.message.reply_text(
            "Avval /test bosing."
        )

        return

    s = state[key]

    current = min(
        s["index"],
        len(WORDS)
    )

    percent = (
        s["score"] / current * 100
        if current
        else 0
    )

    await update.message.reply_text(
        "📊 NATIJA\n\n"
        f"🎯 {s['score']}/{current}\n"
        f"📈 Foiz: {percent:.1f}%\n"
        f"🔥 Eng uzun combo: "
        f"{s['longest_combo']}"
    )


# =========================================================
# RESTART CALLBACK
# =========================================================

async def restart_game(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    chat_id = query.message.chat.id

    # PRIVATE
    if query.message.chat.type not in (
        "group",
        "supergroup"
    ):

        key = (
            chat_id,
            query.from_user.id
        )

        state[key] = new_state()

        await query.message.reply_text(
            "🔄 Test qayta boshlandi!"
        )

        await ask(
            update,
            context
        )

        return

    # GROUP
    session = group_sessions.get(
        chat_id
    )

    if session and session[
        "running"
    ]:

        await query.message.reply_text(
            "⚠️ Turnir davom etmoqda."
        )

        return

    await query.message.reply_text(
        "🏆 Yangi turnir uchun /test ni bosing."
    )


# =========================================================
# TEXT HANDLER
# =========================================================

async def handle_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    # GROUP
    if is_group(update):

        key = get_key(update)

        if key in state:

            s = state[key]

            if s.get(
                "waiting_nickname"
            ):

                await register_group_player(
                    update,
                    context
                )

                return

        # Faqat turnir qatnashchilarining
        # javoblarini tekshirish
        session = group_sessions.get(
            update.effective_chat.id
        )

        if session and session[
            "running"
        ]:

            user_id = (
                update.effective_user.id
            )

            if user_id in session[
                "players"
            ]:

                await group_answer(
                    update,
                    context
                )

            return

        return

    # PRIVATE
    await private_answer(
        update,
        context
    )


# =========================================================
# KEEP RENDER AWAKE
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
            "BOT_TOKEN topilmadi."
        )

    if not hostname:
        raise RuntimeError(
            "RENDER_EXTERNAL_HOSTNAME topilmadi."
        )

    application = (
        Application.builder()
        .token(token)
        .build()
    )

    # Commands
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

    # Group tournament buttons
    application.add_handler(
        CallbackQueryHandler(
            join_tournament,
            pattern="^join_tournament$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            start_tournament,
            pattern="^start_tournament$"
        )
    )

    # Private buttons
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

    # Text
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_text
        )
    )

    # Render webhook
    webhook_path = "telegram"

    webhook_url = (
        f"https://{hostname}/{webhook_path}"
    )

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
