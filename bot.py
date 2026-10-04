import os
import re
import random
import unicodedata
import threading
import time
import urllib.request

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
# 150 TA ENGLISH ↔ UZBEK SO'ZLAR
# Eski 111 ta so'z saqlangan.
# =========================================================

WORDS = [
    # 1-13
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

    # 14-30
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

    # 31-50
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

    # 51-70
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

    # 71-90
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

    # 91-111
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

    # =====================================================
    # YANGI 112-150
    # =====================================================

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
    ("Nephew", "jiyan (o‘g‘il)"),
    ("Niece", "jiyan (qiz)"),
    ("Husband", "eri"),
    ("Wife", "xotin"),
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
    ("How many", "nechta"),
    ("How much", "qancha"),
    ("How much is this?", "nechi pul bu?"),
    ("How much are these?", "nechi pul bular?"),
    ("Can I pay by card?", "kartadan to‘lasam bo‘ladimi?"),
    ("Here you are", "mana, marhamat"),
    ("Here is your change", "o‘tman, qaytirmanga"),
    ("Cash or card?", "naqd pulmi, yoki karta?"),
]

assert len(WORDS) == 150, f"WORDS 150 ta emas: {len(WORDS)} ta"


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

# Har bir foydalanuvchi uchun alohida holat
state = {}


# =========================================================
# JAVOBNI NORMALIZATSIYA QILISH
# =========================================================

def norm(s: str) -> str:
    """
    Javoblarni juda qulay tekshiradi.

    Masalan:
    o‘qimoq
    oʻqimoq
    o'qimoq
    O‘QIMOQ

    hammasi bir xil deb olinadi.
    """

    s = unicodedata.normalize("NFKC", str(s))
    s = s.lower().strip()

    # Turli apostroflarni bir xil qilish
    for ch in [
        "’", "‘", "ʻ", "ʼ", "`", "´",
        "′", "＇", "ʹ", "ˈ"
    ]:
        s = s.replace(ch, "'")

    # "hursand" va "xursand"ni bir xil qabul qilish
    s = s.replace("hursand", "xursand")

    # Ortiqcha bo'shliqlar
    s = re.sub(r"\s+", " ", s)

    # Oxiridagi belgilarni olib tashlash
    s = s.strip(" .!?,'\"")

    return s


def build_options(expected: str):
    """
    Kutilgan javobdan barcha mumkin bo'lgan variantlarni chiqaradi.
    """

    expected = str(expected).strip()

    options = set()

    # Asosiy javob
    options.add(norm(expected))

    # Vergul yoki / bilan ajratilgan javoblar
    parts = re.split(r"\s*(?:,|/)\s*", expected)

    for part in parts:
        part = part.strip()

        if part:
            options.add(norm(part))

    # Qavs ichidagi variantlarni ham qabul qilish
    # Masalan:
    # The USA (The US)
    # My family name (surname) is ...
    match = re.search(r"\(([^()]*)\)", expected)

    if match:
        before = expected[:match.start()].strip()
        inside = match.group(1).strip()
        after = expected[match.end():].strip()

        if before or after:
            options.add(
                norm(f"{before} {after}".strip())
            )

            if inside:
                options.add(
                    norm(f"{before} {inside} {after}".strip())
                )

        if inside:
            options.add(norm(inside))

    return options


def is_correct(user_answer: str, expected: str) -> bool:
    """
    Aqlli javob tekshirish.
    """

    user = norm(user_answer)
    options = build_options(expected)

    # -----------------------------------------------------
    # Maxsus sinonimlar / qo'shimcha qabul qilinadigan javoblar
    # -----------------------------------------------------

    EXTRA = {

        # Oldingi so'zlar
        "yordam bermoq": {
            "yordam",
            "yordam bermoq",
        },

        "tanishganimdan xursandman": {
            "tanishganimdan xursandman",
            "tanishganimdan hursandman",
        },

        "konferensiya": {
            "konferensiya",
        },

        # Yangi so'zlar
        "ota, dada": {
            "ota",
            "dada",
        },

        "ota": {
            "ota",
            "dada",
        },

        "eri": {
            "eri",
            "er",
        },

        "xotin": {
            "xotin",
            "rafiqa",
        },

        "bobo": {
            "bobo",
        },

        "buvi": {
            "buvi",
        },

        "ona": {
            "ona",
        },

        "ota-ona": {
            "ota-ona",
            "ota ona",
        },

        "amaki, tog‘a": {
            "amaki",
            "toga",
            "tog'a",
            "tog‘a",
        },

        "xola, amma": {
            "xola",
            "amma",
        },

        "amakivachcha, xolavachcha": {
            "amakivachcha",
            "xolavachcha",
        },

        "nechi marta, qancha tez-tez": {
            "nechi marta",
            "qancha tez-tez",
            "qancha tez tez",
        },

        "kartadan to‘lasam bo‘ladimi?": {
            "kartadan to‘lasam bo‘ladimi",
            "kartadan to'lasam bo'ladimi",
            "kartadan tolasam boladimi",
        },

        "naqd pulmi, yoki karta?": {
            "naqd pulmi",
            "yoki karta",
            "naqd pulmi yoki karta",
            "naqd pulmi, yoki karta",
        },
    }

    expected_norm = norm(expected)

    if expected_norm in EXTRA:
        options.update(
            norm(x) for x in EXTRA[expected_norm]
        )

    return user in options


# =========================================================
# BAYROQNI ANIQLASH
# =========================================================

def get_flag(word: str) -> str:
    return FLAGS.get(word, "")


# =========================================================
# YANGI USER STATE
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
        "finished": False,

        "question_message_id": None,
    }


# =========================================================
# XAVFSIZ O'CHIRISH
# =========================================================

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
# RENDER UYQUMASLIGINI KAMAYTIRISH
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
# /START
# =========================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

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
# SAVOLNI BERISH
# =========================================================

async def ask(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    key = (
        update.effective_chat.id,
        update.effective_user.id,
    )

    s = state.get(key)

    if not s:
        return

    if s["finished"]:
        return

    index = s["index"]

    if index >= len(WORDS):
        await finish_test(
            update,
            context,
            key
        )
        return

    english, uzbek = WORDS[index]

    # Har savolda yo'nalish tasodifiy
    direction = random.choice([
        "en_to_uz",
        "uz_to_en"
    ])

    s["direction"] = direction

    if direction == "en_to_uz":

        expected = uzbek

        flag = get_flag(english)

        question = (
            f"❓ {index + 1}/{len(WORDS)}\n\n"
            f"{flag} {english}\n\n"
            "🇺🇿 O‘zbekchasini yozing:"
        )

    else:

        expected = english

        flag = get_flag(english)

        question = (
            f"❓ {index + 1}/{len(WORDS)}\n\n"
            f"🇺🇿 {uzbek}\n\n"
            f"{flag or '🇬🇧'} Inglizchasini yozing:"
        )

    s["expected"] = expected

    msg = await update.effective_message.reply_text(
        question
    )

    s["question_message_id"] = msg.message_id


# =========================================================
# /TEST
# =========================================================

async def test(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    key = (
        update.effective_chat.id,
        update.effective_user.id,
    )

    state[key] = new_state()

    await update.message.reply_text(
        "🚀 Test boshlandi!\n\n"
        f"📚 Jami: {len(WORDS)} ta so‘z\n"
        f"📝 Har bosqich: {ROUND_SIZE} ta savol\n\n"
        "Omad! 🔥"
    )

    await ask(update, context)


# =========================================================
# /RESTART
# =========================================================

async def restart(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    key = (
        update.effective_chat.id,
        update.effective_user.id,
    )

    state[key] = new_state()

    await update.message.reply_text(
        "🔄 Test qayta boshlandi!\n\n"
        f"📚 {len(WORDS)} ta so‘z bor.\n"
        "🚀 Omad!"
    )

    await ask(update, context)


# =========================================================
# JAVOB
# =========================================================

async def answer(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    key = (
        update.effective_chat.id,
        update.effective_user.id,
    )

    s = state.get(key)

    if not s:
        return

    if s["finished"]:
        return

    if s["waiting_next_round"]:
        return

    expected = s.get("expected", "")

    if not expected:
        return

    user_answer = update.message.text.strip()

    correct = is_correct(
        user_answer,
        expected
    )

    # Savolni o'chirish
    await safe_delete(
        context.bot,
        update.effective_chat.id,
        s.get("question_message_id")
    )

    # Javobni o'chirmaymiz.
    # Private chatda foydalanuvchi o'z javobini ko'rishi kerak.

    if correct:

        s["score"] += 1

        s["round_score"] += 1

        s["combo"] += 1

        if s["combo"] > s["longest_combo"]:
            s["longest_combo"] = s["combo"]

        if s["combo"] >= 3:

            if s["combo"] == 3:
                combo_text = "🔥 COMBO x3!"

            elif s["combo"] == 5:
                combo_text = "⚡ COMBO x5 — zo‘r!"

            elif s["combo"] % 5 == 0:
                combo_text = (
                    f"🔥 COMBO x{s['combo']}!"
                )

            else:
                combo_text = ""

        else:
            combo_text = ""

        if combo_text:

            await update.message.reply_text(
                f"✅ To‘g‘ri!\n{combo_text}"
            )

        else:

            await update.message.reply_text(
                "✅ To‘g‘ri!"
            )

    else:

        s["combo"] = 0

        s["round_wrong"].append({
            "question": (
                WORDS[s["index"]][0]
                if s["index"] < len(WORDS)
                else ""
            ),
            "answer": expected,
        })

        await update.message.reply_text(
            "❌ Noto‘g‘ri.\n"
            f"To‘g‘ri javob: {expected}"
        )

    # Keyingi savol
    s["index"] += 1

    # Har 10 ta savolda
    if (
        s["index"] % ROUND_SIZE == 0
        and s["index"] < len(WORDS)
    ):

        await round_result(
            update,
            context,
            key
        )

        return

    # Oxirgi savol
    if s["index"] >= len(WORDS):

        await finish_test(
            update,
            context,
            key
        )

        return

    await ask(update, context)


# =========================================================
# BOSQICH NATIJASI
# =========================================================

async def round_result(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    key
):

    s = state[key]

    s["rounds"] += 1
    s["waiting_next_round"] = True

    start = s["index"] - ROUND_SIZE + 1
    end = s["index"]

    wrong_text = ""

    if s["round_wrong"]:

        wrong_text = "\n\n❌ Shu bosqichdagi xatolar:\n"

        for item in s["round_wrong"]:

            wrong_text += (
                f"• {item['question']} → "
                f"{item['answer']}\n"
            )

    text = (
        f"📊 {start}–{end}-savollar natijasi\n\n"

        f"🎯 Bosqich natijasi: "
        f"{s['round_score']}/{ROUND_SIZE}\n"

        f"🏆 Umumiy natija: "
        f"{s['score']}/{s['index']}\n"

        f"📈 Aniqlik: "
        f"{(s['score'] / s['index'] * 100):.1f}%\n"

        f"🔥 Eng uzun combo: "
        f"{s['longest_combo']}\n"

        f"{wrong_text}\n"

        "➡️ Keyingi 10 ta savolga o'tish uchun tugmani bosing."
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "➡️ Keyingi 10 ta",
                callback_data="next_round"
            )
        ]
    ])

    await update.effective_message.reply_text(
        text,
        reply_markup=keyboard
    )


# =========================================================
# KEYINGI 10 TA
# =========================================================

async def next_round(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    if not query:
        return

    await query.answer()

    key = (
        query.message.chat.id,
        query.from_user.id,
    )

    s = state.get(key)

    if not s:
        return

    if not s["waiting_next_round"]:
        return

    s["waiting_next_round"] = False

    s["round_score"] = 0
    s["round_wrong"] = []

    s["question_message_id"] = None

    await query.message.edit_reply_markup(
        reply_markup=None
    )

    await ask_from_callback(
        query,
        context,
        key
    )


async def ask_from_callback(
    query,
    context,
    key
):

    s = state.get(key)

    if not s:
        return

    if s["finished"]:
        return

    index = s["index"]

    if index >= len(WORDS):
        return

    english, uzbek = WORDS[index]

    direction = random.choice([
        "en_to_uz",
        "uz_to_en"
    ])

    s["direction"] = direction

    flag = get_flag(english)

    if direction == "en_to_uz":

        expected = uzbek

        question = (
            f"❓ {index + 1}/{len(WORDS)}\n\n"
            f"{flag} {english}\n\n"
            "🇺🇿 O‘zbekchasini yozing:"
        )

    else:

        expected = english

        question = (
            f"❓ {index + 1}/{len(WORDS)}\n\n"
            f"🇺🇿 {uzbek}\n\n"
            f"{flag or '🇬🇧'} Inglizchasini yozing:"
        )

    s["expected"] = expected

    msg = await query.message.reply_text(
        question
    )

    s["question_message_id"] = msg.message_id


# =========================================================
# YAKUNIY NATIJA
# =========================================================

async def finish_test(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    key
):

    s = state.get(key)

    if not s:
        return

    if s["finished"]:
        return

    s["finished"] = True

    total = len(WORDS)

    score = s["score"]

    percentage = (
        score / total * 100
        if total
        else 0
    )

    text = (
        "🎉 TEST TUGADI!\n\n"

        f"🏆 Natijangiz: {score}/{total}\n"

        f"📊 Aniqlik: {percentage:.1f}%\n"

        f"🔥 Eng uzun combo: "
        f"{s['longest_combo']}\n"

        f"📚 Bosqichlar: "
        f"{s['rounds']}\n\n"

        "👏 Barakalla!"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🔄 Qaytadan boshlash",
                callback_data="restart_game"
            )
        ]
    ])

    await update.effective_message.reply_text(
        text,
        reply_markup=keyboard
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

    key = (
        query.message.chat.id,
        query.from_user.id,
    )

    state[key] = new_state()

    await query.message.reply_text(
        "🔄 Test qayta boshlandi!\n\n"
        f"📚 Jami: {len(WORDS)} ta so‘z"
    )

    # Callback'dan savol berish
    await ask_from_callback(
        query,
        context,
        key
    )


# =========================================================
# /SCORE
# =========================================================

async def score(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    key = (
        update.effective_chat.id,
        update.effective_user.id,
    )

    s = state.get(key)

    if not s:
        await update.message.reply_text(
            "Avval /test buyrug‘ini bosing."
        )
        return

    total_answered = s["index"]

    if total_answered == 0:

        percentage = 0

    else:

        percentage = (
            s["score"] /
            total_answered *
            100
        )

    await update.message.reply_text(

        "📊 SIZNING NATIJANGIZ\n\n"

        f"👤 {update.effective_user.first_name}\n"

        f"🎯 {s['score']}/{total_answered}\n"

        f"📈 Aniqlik: {percentage:.1f}%\n"

        f"🔥 Eng uzun combo: "
        f"{s['longest_combo']}\n"

        f"📚 Bosqichlar: "
        f"{s['rounds']}"

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

    key = (
        update.effective_chat.id,
        update.effective_user.id,
    )

    s = state.get(key)

    if not s:
        await update.message.reply_text(
            "Avval /test buyrug‘ini bosing."
        )
        return

    await answer(
        update,
        context
    )


# =========================================================
# MAIN
# =========================================================

def main():

    token = os.getenv("BOT_TOKEN")

    if not token:
        raise RuntimeError(
            "BOT_TOKEN topilmadi."
        )

    hostname = os.getenv(
        "RENDER_EXTERNAL_HOSTNAME"
    )

    port = int(
        os.getenv(
            "PORT",
            "10000"
        )
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

    # Buyruqlar
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

    # Tugmalar
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

    # Oddiy matn javoblari
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

    # Render'ni uyg'oq ushlab turishga harakat
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
