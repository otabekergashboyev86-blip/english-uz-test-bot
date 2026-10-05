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
# 150 TA ASOSIY SO'Z
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

    # 112–150

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


# 150 ta ekanini tekshiradi
assert len(WORDS) == 150, (
    f"XATO: WORDS 150 ta bo‘lishi kerak, hozir {len(WORDS)} ta."
)


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
# NORMALIZATSIYA
# ============================================================

def norm(text):
    """
    Oddiy va kuchli normalizatsiya:

    - katta/kichik harf farqini yo'q qiladi
    - Unicode belgilarni bir xil qiladi
    - turli apostroflarni bir xil qiladi
    - ortiqcha bo'shliqlarni yo'q qiladi
    - oxiridagi . ! ? belgilarini yo'q qiladi
    - h/x farqini keyinchalik Uzbek javoblarda alohida hisobga olish mumkin
    """

    if text is None:
        return ""

    text = str(text)

    # Unicode
    text = unicodedata.normalize("NFKC", text)

    # lowercase
    text = text.lower().strip()

    # Barcha apostrof variantlarini oddiy apostrofga o'tkazish
    apostrophes = (
        "’",
        "‘",
        "ʻ",
        "ʼ",
        "`",
        "´",
        "′",
        "ʹ",
    )

    for ch in apostrophes:
        text = text.replace(ch, "'")

    # Uch nuqtani oddiy uch nuqtaga
    text = text.replace("…", "...")

    # Ortiqcha bo'shliqlar
    text = re.sub(r"\s+", " ", text)

    # Vergul va slash atrofidagi ortiqcha bo'shliq
    text = re.sub(r"\s*,\s*", ",", text)
    text = re.sub(r"\s*/\s*", "/", text)

    # Qavs atrofidagi bo'shliq
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)

    # Nuqta, !, ? faqat oxirida bo'lsa olib tashlanadi
    text = text.strip(" .!?")

    return text


def uzbek_norm(text):
    """
    O'zbekcha javob uchun yanada kuchli tekshiruv.

    h/x farqi:
        mashhur = mashxur

    Bu faqat O'ZBEKCHA javoblarda ishlatiladi.
    Inglizcha so'zlarda h/x ni almashtirmaydi.
    """

    text = norm(text)

    # h va x ni bir xil deb hisoblaymiz
    text = text.replace("x", "h")

    return text


def is_uzbek_text(text):
    """
    Javobni Uzbek variantlari bilan solishtirish uchun.
    """

    return uzbek_norm(text)


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
        "bola farzand",
    ],

    "children": [
        "bolalar",
        "farzandlar",
    ],

    "uncle": [
        "amaki",
        "tog'a",
        "togavachcha",
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
        "amakivachcha bola",
        "xolavachcha bola",
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
        "jiyan qiz bola",
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

    # MUHIM:
    # Men ...daman / Men ... danman / Men ...danman
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
# BAYROQ OLISH
# ============================================================

def get_flag(word):
    return FLAGS.get(word, "🇬🇧")


# ============================================================
# JAVOB VARIANTLARINI YARATISH
# ============================================================

def build_options(en, uz, direction):

    expected = uz if direction == "en_to_uz" else en

    options = [expected]

    # Uzbek javoblar
    if direction == "en_to_uz":

        # Vergul bilan ajratilgan javoblar
        if "," in expected:
            parts = expected.split(",")

            for part in parts:
                part = part.strip()

                if part:
                    options.append(part)

        # Slash bilan ajratilgan javoblar
        if "/" in expected:
            parts = expected.split("/")

            for part in parts:
                part = part.strip()

                if part:
                    options.append(part)

        # Qavs ichidagi variantlar
        if "(" in expected and ")" in expected:

            outside = re.sub(
                r"\s*\([^)]*\)",
                "",
                expected
            ).strip()

            match = re.search(
                r"\(([^)]*)\)",
                expected
            )

            if outside:
                options.append(outside)

            if match:
                inside = match.group(1).strip()

                if inside:
                    options.append(inside)

        # Maxsus aliaslar
        options.extend(
            EXTRA_ALIASES.get(
                en.lower(),
                []
            )
        )

    # English javob
    else:

        # The USA (The US)
        if "(" in en and ")" in en:

            outside = re.sub(
                r"\s*\([^)]*\)",
                "",
                en
            ).strip()

            match = re.search(
                r"\(([^)]*)\)",
                en
            )

            if outside:
                options.append(outside)

            if match:
                inside = match.group(1).strip()

                if inside:
                    options.append(inside)

        # Cousin(e)
        if en.lower() == "cousin(e)":
            options.extend([
                "cousin",
            ])

    # Takrorlarni olib tashlash
    unique = []

    seen = set()

    for option in options:

        if not option:
            continue

        key = norm(option)

        if key not in seen:
            seen.add(key)
            unique.append(option)

    return unique


# ============================================================
# JAVOBNI TEKSHIRISH
# ============================================================

def is_correct(user_answer, en, uz, direction):

    if not user_answer:
        return False

    user_answer = str(user_answer).strip()

    options = build_options(
        en,
        uz,
        direction
    )

    # --------------------------------------------------------
    # ENGLISH -> UZBEK
    # h/x farqi ham hisobga olinadi
    # --------------------------------------------------------

    if direction == "en_to_uz":

        user = is_uzbek_text(user_answer)

        valid_answers = {
            is_uzbek_text(option)
            for option in options
            if option
        }

        return user in valid_answers

    # --------------------------------------------------------
    # UZBEK -> ENGLISH
    # Bu yerda h/x almashtirilmaydi.
    # --------------------------------------------------------

    user = norm(user_answer)

    valid_answers = {
        norm(option)
        for option in options
        if option
    }

    return user in valid_answers


# ============================================================
# YANGI TEST HOLATI
# ============================================================

def new_state():

    # 150 ta indeksni to'liq RANDOM qiladi
    order = RNG.sample(
        range(len(WORDS)),
        len(WORDS)
    )

    return {
        "index": 0,
        "score": 0,

        # RANDOM tartib shu yerda saqlanadi
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

    # Test tugagan bo'lsa
    if index >= len(WORDS):

        await finish_test(
            update,
            context
        )

        return

    # RANDOM WORD
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

    flag = get_flag(en)

    # --------------------------------------------------------
    # English -> Uzbek
    # --------------------------------------------------------

    if direction == "en_to_uz":

        text = (
            f"❓ {index + 1}/{len(WORDS)}\n\n"
            f"{flag} {en}\n\n"
            f"🇺🇿 O‘zbekchasini yozing:"
        )

    # --------------------------------------------------------
    # Uzbek -> English
    # --------------------------------------------------------

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

    s["question_message_id"] = message.message_id


# ============================================================
# /TEST
# ============================================================

async def start_test(
    update,
    context
):

    uid = update.effective_user.id

    # Yangi RANDOM test
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
        f"📚 Joriy savol: {answered}/150"
    )


# ============================================================
# /WORDS
# Barcha 150 ta so'zni Telegramda ko'rsatadi
# ============================================================

async def words_command(
    update,
    cont
