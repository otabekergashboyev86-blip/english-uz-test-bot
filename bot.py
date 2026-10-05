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


# ============================================================
# 150 TA SO'Z
# ============================================================

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
    ("How much are these?", "nechi pul bular?"),
    ("Can I pay by card?", "kartadan to‘lasam bo‘ladimi?"),
    ("Here you are", "mana, marhamat"),
    ("Here is your change", "qaytimingiz, marhamat"),
    ("Cash or card?", "naqd pulmi yoki karta?"),
]


assert len(WORDS) == 150, f"XATO: WORDS 150 ta emas: {len(WORDS)} ta"


# ============================================================
# BAYROQLAR
# ============================================================

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
    "British": "🇬🇧",
    "Polish": "🇵🇱",
    "Spanish": "🇪🇸",
    "Turkish": "🇹🇷",
    "Mexican": "🇲🇽",
    "Japanese": "🇯🇵",
    "Italian": "🇮🇹",
    "American": "🇺🇸",
    "Canadian": "🇨🇦",
    "Brazilian": "🇧🇷",
    "Argentinian": "🇦🇷",
    "Thai": "🇹🇭",
}


# ============================================================
# SOZLAMALAR
# ============================================================

ROUND_SIZE = 10

state = {}

RNG = random.SystemRandom()


# ============================================================
# JAVOBNI NORMALIZATSIYA QILISH
# ============================================================

def normalize_answer(text):
    """
    Javoblarni juda yumshoq tekshiradi.

    1. Katta-kichik harf farqi yo'q
    2. h/x farqi yo'q
    3. o‘ / oʻ / o' farqi yo'q
    4. Ortiqcha bo'shliq farqi yo'q
    5. Oxiridagi . ! ? , farqi yo'q
    """

    if text is None:
        return ""

    text = str(text)

    # Unicode
    text = unicodedata.normalize(
        "NFKC",
        text
    )

    # Kichik harf
    text = text.lower().strip()

    # Har xil apostroflarni bir xil qilish
    apostrophes = (
        "’",
        "‘",
        "ʻ",
        "ʼ",
        "`",
        "´",
        "′",
        "ʹ",
        "ʽ",
    )

    for ch in apostrophes:
        text = text.replace(ch, "'")

    # MUHIM:
    # H va X farq qilmaydi
    #
    # mashhur = mashxur
    # xotin = hotin
    # xursand = hursand

    text = text.replace("x", "h")

    # Ortiqcha bo'shliqlar
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    # Vergul va slash atrofidagi bo'shliqlar
    text = re.sub(
        r"\s*,\s*",
        ",",
        text
    )

    text = re.sub(
        r"\s*/\s*",
        "/",
        text
    )

    # Qavslar
    text = re.sub(
        r"\s+",
        "(",
        text
    )

    text = re.sub(
        r"\s+",
        ")",
        text
    )

    # Oxiridagi belgilar
    text = text.strip(
        " .!?,"
    )

    return text


# ============================================================
# QO'SHIMCHA QABUL QILINADIGAN JAVOBLAR
# ============================================================

EXTRA_ALIASES = {

    "work": [
        "ish",
        "ishlamoq",
        "mehnat qilmoq",
    ],

    "help": [
        "yordam",
        "yordam bermoq",
    ],

    "father": [
        "ota",
        "dada",
    ],

    "mother": [
        "ona",
        "oyi",
    ],

    "parents": [
        "ota-ona",
        "ota ona",
        "ota va ona",
    ],

    "grandfather": [
        "bobo",
    ],

    "grandmother": [
        "buvi",
    ],

    "son": [
        "o'g'il",
        "o'g'lim",
        "o'g'il bola",
    ],

    "daughter": [
        "qiz",
        "qiz bola",
        "qizim",
    ],

    "child": [
        "bola",
        "farzand",
    ],

    "children": [
        "bolalar",
        "farzandlar",
    ],

    "uncle": [
        "amaki",
        "tog'a",
    ],

    "aunt": [
        "xola",
        "amma",
    ],

    "cousin(e)": [
        "amakivachcha",
        "xolavachcha",
        "tog'avachcha",
        "togavachcha",
        "ammavachcha",
    ],

    "nephew": [
        "jiyan",
        "jiyan o'g'il",
        "o'g'il jiyan",
        "jiyan o'g'il bola",
        "o'g'il bola",
        "jiyan bola",
    ],

    "niece": [
        "jiyan",
        "jiyan qiz",
        "qiz jiyan",
        "jiyan qiz bola",
        "qiz bola",
        "jiyan bola",
    ],

    "husband": [
        "eri",
        "er",
        "erim",
        "turmush o'rtog'i",
    ],

    "wife": [
        "xotin",
        "hotin",
        "rafiqa",
        "xotinim",
        "rafiqam",
        "turmush o'rtog'i",
    ],

    "desk": [
        "parta",
    ],

    "table": [
        "stol",
    ],

    "chair": [
        "stul",
        "kursi",
    ],

    "key": [
        "kalit",
    ],

    "clock": [
        "soat",
    ],

    "cup": [
        "krujka",
        "piyola",
    ],

    "job": [
        "kasb",
        "ish",
    ],

    "page": [
        "sahifa",
        "bet",
    ],

    "correct": [
        "to'g'ri",
        "tog'ri",
        "to'g'rilamoq",
        "togrilamoq",
    ],

    "some": [
        "ba'zi",
        "bazi",
        "bir nechta",
    ],

    "make": [
        "qilmoq",
        "yasamoq",
    ],

    "all": [
        "hamma",
        "barcha",
    ],

    "photo": [
        "rasm",
        "surat",
    ],

    "class": [
        "dars",
        "sinf",
    ],

    "true": [
        "to'g'ri",
        "tog'ri",
    ],

    "false": [
        "noto'g'ri",
        "notog'ri",
    ],

    "what": [
        "nima",
        "qanday",
    ],

    "how often": [
        "nechi marta",
        "qancha tez-tez",
        "qanchalik tez-tez",
    ],

    "here you are": [
        "mana",
        "marhamat",
    ],

    "cash or card?": [
        "naqd pulmi yoki karta",
        "naqd pul yoki karta",
        "naqdmi yoki karta",
    ],

    "i’m from ...": [
        "men ...daman",
        "men ... danman",
        "men ...danman",
        "men ... daman",
    ],

    "nice to meet you": [
        "tanishganimdan xursandman",
        "tanishganimdan hursandman",
        "tanishganimdan mamnunman",
    ],
}


# ============================================================
# JAVOB VARIANTLARINI YIG'ISH
# ============================================================

def answer_variants(text):

    if not text:
        return set()

    variants = set()

    # Asosiy javob
    variants.add(
        normalize_answer(text)
    )

    # Vergul
    if "," in text:

        for part in text.split(","):

            part = part.strip()

            if part:
                variants.add(
                    normalize_answer(part)
                )

    # Slash
    if "/" in text:

        for part in text.split("/"):

            part = part.strip()

            if part:
                variants.add(
                    normalize_answer(part)
                )

    # Qavs
    if "(" in text and ")" in text:

        outside = re.sub(
            r"\s*[^)]*",
            "",
            text
        ).strip()

        if outside:
            variants.add(
                normalize_answer(outside)
            )

        match = re.search(
            r"([^)]*)",
            text
        )

        if match:

            inside = match.group(1).strip()

            if inside:
                variants.add(
                    normalize_answer(inside)
                )

    return {
        x
        for x in variants
        if x
    }


# ============================================================
# JAVOBNI TEKSHIRISH
# ============================================================

def is_correct(
    user_answer,
    en,
    uz,
    direction
):

    user = normalize_answer(
        user_answer
    )

    if not user:
        return False

    # ========================================================
    # ENGLISH -> UZBEK
    # ========================================================

    if direction == "en_to_uz":

        valid = set()

        # Asosiy javob
        valid.update(
            answer_variants(uz)
        )

        # Qo'shimcha javoblar
        for alias in EXTRA_ALIASES.get(
            en.lower(),
            []
        ):

            valid.add(
                normalize_answer(alias)
            )

        return user in valid

    # ========================================================
    # UZBEK -> ENGLISH
    # ========================================================

    valid = set()

    # Asosiy English
    valid.add(
        normalize_answer(en)
    )

    # Qavsli English
    if "(" in en and ")" in en:

        outside = re.sub(
            r"\s*[^)]*",
            "",
            en
        ).strip()

        if outside:
            valid.add(
                normalize_answer(outside)
            )

        match = re.search(
            r"([^)]*)",
            en
        )

        if match:

            inside = match.group(1).strip()

            if inside:
                valid.add(
                    normalize_answer(inside)
                )

    return user in valid


# ============================================================
# RANDOM TEST HOLATI
# ============================================================

def new_state():

    # 150 ta so'zning random tartibi
    order = RNG.sample(
        range(len(WORDS)),
        len(WORDS)
    )

    return {
        "index": 0,
        "score": 0,
        "order": order,

        "round_correct": 0,
        "rounds": 0,

        "combo": 0,
        "max_combo": 0,

        "question_message_id": None,

        "direction": None,

        "answered": False,
    }


# ============================================================
# SAVOLNI O'CHIRISH
# ============================================================

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


# ============================================================
# SAVOL BERISH
# ============================================================

async def ask(
    update,
    context
):

    uid = update.effective_user.id

    s = state.get(uid)

    if not s:
        return

    index = s["index"]

    if index >= len(WORDS):

        await finish_test(
            update,
            context
        )

        return

    # RANDOM SO'Z
    word_index = s["order"][index]

    en, uz = WORDS[word_index]

    # RANDOM YO'NALISH
    direction = RNG.choice(
        (
            "en_to_uz",
            "uz_to_en",
        )
    )

    s["direction"] = direction
    s["answered"] = False

    flag = FLAGS.get(
        en,
        "🇬🇧"
    )

    if direction == "en_to_uz":

        text = (
            f"❓ {index + 1}/{len(WORDS)}\n\n"
            f"{flag} {en}\n\n"
            "🇺🇿 O‘zbekchasini yozing:"
        )

    else:

        text = (
            f"❓ {index + 1}/{len(WORDS)}\n\n"
            f"🇺🇿 {uz}\n\n"
            f"{flag} Inglizchasini yozing:"
        )

    # Callback orqali kelgan bo'lsa
    if update.callback_query:

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text
        )

    else:

        message = await update.effective_message.reply_text(
            text
        )

    s["question_message_id"] = (
        message.message_id
    )


# ============================================================
# /TEST
# ============================================================

async def start_test(
    update,
    context
):

    uid = update.effective_user.id

    # Har safar yangi random
    state[uid] = new_state()

    await update.message.reply_text(
        "🚀 TEST BOSHLANDI!\n\n"
        "📚 Jami: 150 ta so‘z\n"
        "📝 Har bosqich: 10 ta savol\n"
        "🎲 So‘zlar: RANDOM\n"
        "🔄 Yo‘nalish: RANDOM\n"
        "♻️ Takroriy so‘z: YO‘Q\n\n"
        "🔥 Omad!"
    )

    await ask(
        update,
        context
    )


# ============================================================
# /RESTART
# ============================================================

async def restart_game(
    update,
    context
):

    await start_test(
        update,
        context
    )


# ============================================================
# /SCORE
# ============================================================

async def score_command(
    update,
    context
):

    uid = update.effective_user.id

    s = state.get(uid)

    if not s:

        await update.message.reply_text(
            "Avval /test buyrug‘ini bosing."
        )

        return

    answered = s["index"]

    accuracy = (
        s["score"] / answered * 100
        if answered
        else 0
    )

    await update.message.reply_text(
        "📊 NATIJA\n\n"
        f"🏆 To‘g‘ri: {s['score']}/{answered}\n"
        f"📈 Aniqlik: {accuracy:.1f}%\n"
        f"🔥 Eng uzun combo: {s['max_combo']}\n"
        f"📚 Joriy: {answered}/150"
    )


# ============================================================
# /WORDS
# ============================================================

async def words_command(
    update,
    context
):

    text = "📚 150 TA SO‘Z\n\n"

    for i, (english, uzbek) in enumerate(
        WORDS,
        start=1
    ):

        text += (
            f"{i}. {english} — {uzbek}\n"
        )

    # Telegram xabar limiti
    chunk_size = 3500

    for start in range(
        0,
       
