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
# 150 TA SO'Z
# 111 TA ESKI + 39 TA YANGI
# =========================================================

WORDS = [

    # =====================================================
    # 1-111
    # =====================================================

    ("Argentina", "Argentina"),
    ("Brazil", "Braziliya"),
    ("Canada", "Kanada"),
    ("Italy", "Italiya"),
    ("Japan", "Yaponiya"),
    ("Mexico", "Meksika"),
    ("Poland", "Polsha"),
    ("Spain", "Ispaniya"),
    ("Thailand", "Tailand"),
    ("Great Britain", "Buyuk Britaniya"),
    ("The UK", "Birlashgan Qirollik"),
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
    ("What’s your family name (surname)?", "Familiyangiz nima?"),
    ("My family name (surname) is ...", "Mening familiyam ..."),
    ("Where are you from?", "Qayerdansiz?"),
    ("I’m from ...", "Men ...danman"),
    ("Football player", "futbolchi"),
    ("Doctor", "shifokor"),
    ("School teacher", "ustoz, o‘qituvchi"),
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
    ("British", "britaniyalik"),
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
    ("All over the world", "butun dunyo bo‘ylab"),
    ("And", "va"),
    ("But", "lekin"),
    ("Now", "hozir"),
    ("Hotel", "mehmonxona"),
    ("What’s your phone number?", "telefon raqamingiz qanday?"),
    ("What’s your email address?", "elektron pochta manzilingiz qanday?"),
    ("Sorry, can you say that again?", "Uzr, qaytadan ayta olasizmi?"),
    ("How do you spell (your name)?", "Ismingiz qanday harflanadi?"),
    ("@", "at"),
    ("Dot", "nuqta"),
    ("Class", "dars, sinf"),
    ("Late", "kech qolmoq"),
    ("Today", "bugun"),

    # =====================================================
    # 112-150
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
    ("Husband", "er"),
    ("Wife", "xotin"),
    ("Desk", "parta"),
    ("Table", "stol"),
    ("Chair", "stul"),
    ("Key", "kalit"),
    ("Clock", "soat"),
    ("Cup", "krujka, piyola"),
    ("Who", "kim"),
    ("Whose", "kimning"),
    ("What", "nima, qanday"),
    ("Where", "qayer"),
    ("When", "qachon"),
    ("Why", "nega, nima uchun"),
    ("How", "qanday, qanday qilib"),
    ("How often", "qanchalik tez-tez"),
    ("How many", "nechta"),
    ("How much", "qancha"),
    ("How much is this?", "Bu qancha turadi?"),
    ("How much are these?", "Bular qancha turadi?"),
    ("Can I pay by card?", "Kartadan to‘lasam bo‘ladimi?"),
    ("Here you are", "Mana, marhamat"),
    ("Here is your change", "Mana qaytimingiz"),
    ("Cash or card?", "Naqd pulmi yoki kartami?"),
]


# =========================================================
# TEKSHIRUV
# =========================================================

assert len(WORDS) == 150, f"WORDS soni 150 emas: {len(WORDS)}"


# =========================================================
# BAYROQLAR
# =========================================================

FLAGS = {
    "argentina": "🇦🇷",
    "brazil": "🇧🇷",
    "canada": "🇨🇦",
    "italy": "🇮🇹",
    "japan": "🇯🇵",
    "mexico": "🇲🇽",
    "poland": "🇵🇱",
    "spain": "🇪🇸",
    "thailand": "🇹🇭",
    "great britain": "🇬🇧",
    "the uk": "🇬🇧",
    "the usa (the us)": "🇺🇸",
    "turkey": "🇹🇷",
}


# =========================================================
# TEST SOZLAMALARI
# =========================================================

ROUND_SIZE = 10

# Har bir foydalanuvchining holati
state = {}


# =========================================================
# NORMALIZATSIYA
# =========================================================

def norm(text):
    if text is None:
        return ""

    text = unicodedata.normalize("NFKC", str(text))

    # Katta/kichik harf farq qilmaydi
    text = text.casefold()

    # Apostrof variantlarini bir xil qilamiz
    apostrophes = "’‘ʻʼ`´ʹ′"
    for ch in apostrophes:
        text = text.replace(ch, "'")

    # Belgilar
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = text.replace("_", " ")

    # Qavslarni olib tashlash
    text = re.sub(r"[()[\]{}]", " ", text)

    # Tinish belgilarini bo‘sh joyga aylantirish
    text = re.sub(r"[,;:!?]+", " ", text)

    # Chiziqchalarni bo‘sh joyga aylantirish
    text = re.sub(r"\s*-\s*", " ", text)

    # Ortiqcha bo‘sh joy
    text = re.sub(r"\s+", " ", text).strip()

    # Oxiridagi belgilar
    text = text.strip(" .,!?:;-")

    return text


# =========================================================
# JAVOB VARIANTLARINI AJRATISH
# =========================================================

def build_options(expected):
    expected = str(expected).strip()

    options = set()

    # Asosiy javob
    options.add(expected)

    # Vergul va slash orqali berilgan variantlar
    parts = re.split(r"\s*[,/]\s*", expected)

    for part in parts:
        part = part.strip()

        if part:
            options.add(part)

    # Qavs ichidagi variant
    matches = re.findall(r"(.*?)", expected)

    for inside in matches:
        inside = inside.strip()

        if inside:
            options.add(inside)

    # Qavssiz ko‘rinish
    without_parentheses = re.sub(
        r"\s*.*?",
        "",
        expected
    ).strip()

    if without_parentheses:
        options.add(without_parentheses)

    return {
        norm(x)
        for x in options
        if norm(x)
    }


# =========================================================
# MAXSUS JAVOB VARIANTLARI
# =========================================================

ANSWER_ALIASES = {

    "about": [
        "haqida",
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
        "ota ona",
        "ota-ona",
        "ota va ona",
    ],

    "grandfather": [
        "bobo",
        "katta ota",
    ],

    "grandmother": [
        "buvi",
        "katta ona",
    ],

    "son": [
        "o‘g‘il",
        "o'g'il",
        "oʻgʻil",
        "o‘g‘il bola",
        "o'g'il bola",
        "oʻgʻil bola",
    ],

    "daughter": [
        "qiz",
        "qiz farzand",
        "qiz bola",
        "qizbola",
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
        "tog‘a",
        "tog'a",
        "togʻa",
    ],

    "aunt": [
        "xola",
        "amma",
    ],

    "cousin(e)": [
        "amakivachcha",
        "xolavachcha",
        "tog‘avachcha",
        "tog'avachcha",
        "amakivatcha",
        "xolavatcha",
        "togavatcha",
        "amakivachcha xolavachcha",
        "amakivatcha xolavatcha",
    ],

    "nephew": [
        "jiyan",
        "jiyan o‘g‘il",
        "jiyan o'g'il",
        "jiyan oʻgʻil",
        "jiyan o‘g‘il bola",
        "jiyan o'g'il bola",
        "jiyan bola",
        "o‘g‘il jiyan",
        "o'g'il jiyan",
        "oʻgʻil jiyan",
        "o‘g‘il bola",
    ],

    "niece": [
        "jiyan",
        "jiyan qiz",
        "jiyan qi",
        "jiyan qiz bola",
        "qiz jiyan",
        "qiz bola",
        "qizbola",
        "qizjoyan",
    ],

    "husband": [
        "er",
        "eri",
        "turmush o‘rtog‘i",
        "turmush o'rtog'i",
    ],

    "wife": [
        "xotin",
        "hotin",
        "rafiqa",
        "turmush o‘rtog‘i",
        "turmush o'rtog'i",
    ],

    "desk": [
        "parta",
        "maktab partasi",
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

    "who": [
        "kim",
    ],

    "whose": [
        "kimning",
    ],

    "what": [
        "nima",
        "qanday",
    ],

    "where": [
        "qayer",
        "qayerda",
    ],

    "when": [
        "qachon",
    ],

    "why": [
        "nega",
        "nima uchun",
        "nimaga",
    ],

    "how": [
        "qanday",
        "qanday qilib",
    ],

    "how often": [
        "qanchalik tez-tez",
        "qanchalik tez tez",
        "necha marta",
        "qancha tez-tez",
        "qancha tez tez",
    ],

    "how many": [
        "nechta",
        "qancha",
    ],

    "how much": [
        "qancha",
    ],

    "how much is this?": [
        "bu qancha turadi",
        "bu necha pul",
        "bu nechi pul",
        "nechi pul bu",
        "qancha turadi",
    ],

    "how much are these?": [
        "bular qancha turadi",
        "bular necha pul",
        "bular nechi pul",
        "nechi pul bular",
        "qancha turadi",
    ],

    "can i pay by card?": [
        "kartadan to‘lasam bo‘ladimi",
        "kartadan to'lasam bo'ladimi",
        "karta bilan to‘lasam bo‘ladimi",
        "karta bilan to'lasam bo'ladimi",
    ],

    "here you are": [
        "mana",
        "marhamat",
        "mana marhamat",
    ],

    "here is your change": [
        "mana qaytimingiz",
        "mana qaytishingiz",
        "qaytimingiz",
        "qaytim",
    ],

    "cash or card?": [
        "naqd pulmi yoki kartami",
        "naqd pulmi yoki karta",
        "naqdmi yoki karta",
        "naqd yoki karta",
    ],

    # =====================================================
    # ESKI SO‘ZLAR UCHUN QO‘SHIMCHA VARIANTLAR
    # =====================================================

    "work": [
        "ishlamoq",
        "ishlash",
        "ish",
        "mehnat qilmoq",
        "mehnat",
    ],

    "job": [
        "kasb",
        "ish",
    ],

    "read": [
        "o‘qimoq",
        "o'qimoq",
        "oʻqimoq",
        "oqimoq",
    ],

    "help": [
        "yordam",
        "yordam bermoq",
    ],

    "correct": [
        "to‘g‘ri",
        "to'g'ri",
        "toʻgʻri",
        "togri",
        "to‘g‘rilamoq",
        "to'g'rilamoq",
        "togrilamoq",
    ],

    "make": [
        "qilmoq",
        "yasamoq",
        "yasash",
    ],

    "some": [
        "ba’zi",
        "ba'zi",
        "baʼzi",
        "bir nechta",
    ],

    "all": [
        "hamma",
        "barcha",
    ],

    "photo": [
        "rasm",
        "surat",
    ],

    "page": [
        "sahifa",
        "bet",
    ],

    "class": [
        "dars",
        "sinf",
    ],

    "nice to meet you": [
        "tanishganimdan xursandman",
        "tanishganimdan hursandman",
    ],

    "conference": [
        "konferensiya",
    ],

    "what’s your phone number?": [
        "telefon raqamingiz qanday",
        "telefon raqamingiz nima",
        "telefon raqamingiz",
    ],

    "what’s your email address?": [
        "elektron pochtangiz qanday",
        "elektron pochta manzilingiz qanday",
        "email manzilingiz qanday",
        "emailingiz qanday",
    ],

    "sorry, can you say that again?": [
        "uzr qaytadan ayta olasizmi",
        "uzr qayta ayta olasizmi",
        "qaytadan ayta olasizmi",
        "qayta ayta olasizmi",
    ],

    "how do you spell (your name)?": [
        "ismingiz qanday harflanadi",
        "ismingizni qanday harflaysiz",
        "ismingizni harflab ayting",
        "qanday harflanadi",
        "what spell",
    ],

    "dot": [
        "nuqta",
    ],

    "hotel": [
        "mehmonxona",
    ],

    "now": [
        "hozir",
    ],

    "today": [
        "bugun",
    ],

    "late": [
        "kech qolmoq",
        "kechikmoq",
        "kech qolish",
    ],

    "match": [
        "tanlamoq",
        "moslashtirmoq",
        "moslashtirish",
    ],

    "complete": [
        "tugatmoq",
        "to‘ldirmoq",
        "to'ldirmoq",
        "toʻldirmoq",
    ],

    "alternative": [
        "tanlov",
        "muqobil variant",
        "muqobil",
    ],

    "tell": [
        "aytmoq",
        "gapirib bermoq",
    ],

    "nice": [
        "yaxshi",
        "yoqimli",
    ],

    "short": [
        "kalta",
        "qisqa",
    ],

    "form": [
        "shakl",
        "forma",
    ],

    "use": [
        "ishlatmoq",
        "foydalanmoq",
    ],

    "here": [
        "bu yerda",
        "shu yerda",
    ],

    "flag": [
        "bayroq",
    ],

    "country": [
        "mamlakat",
        "davlat",
    ],

    "person": [
        "odam",
        "kishi",
    ],

    "people": [
        "odamlar",
        "kishilar",
    ],

    "repeat": [
        "qaytarmoq",
        "takrorlamoq",
    ],

    "conversation": [
        "muloqot",
        "suhbat",
    ],

    "sentence": [
        "gap",
    ],

    "exercise": [
        "mashq",
    ],

    "other": [
        "boshqa",
    ],

    "order": [
        "tartib",
    ],

    "partner": [
        "sherik",
    ],

    "friend": [
        "do‘st",
        "do'st",
        "dost",
    ],
}


# =========================================================
# JAVOBNI TEKSHIRISH
# =========================================================

def is_correct(user_answer, expected, english_word=None):

    user = norm(user_answer)

    if not user:
        return False

    # Asosiy WORDS ichidagi javoblar
    options = build_options(expected)

    # English so‘zga tegishli maxsus variantlar
    if english_word:
        key = norm(english_word)

        if key in ANSWER_ALIASES:
            for alias in ANSWER_ALIASES[key]:
                options.add(norm(alias))

    return user in options


# =========================================================
# FLAG
# =========================================================

def get_flag(word):
    key = norm(word)

    return FLAGS.get(key, "")


# =========================================================
# YANGI TEST HOLATI
# =========================================================

def new_state():

    # 0-149 indekslarni random aralashtiramiz
    order = list(range(len(WORDS)))
    random.shuffle(order)

    return {
        "index": 0,
        "score": 0,

        # RANDOM TARTIB
        "order": order,

        # Combo
        "combo": 0,
        "best_combo": 0,

        # 10 talik bosqich
        "round_score": 0,
        "round_start": 0,

        # Hozirgi savol
        "current_message_id": None,
    }


# =========================================================
# XAVFSIZ MESSAGE O‘CHIRISH
# =========================================================

async def safe_delete(message):

    if not message:
        return

    try:
        await message.delete()
    except Exception:
        pass


# =========================================================
# RENDER UYQUDA QOLMASLIGI UCHUN
# =========================================================

def keep_render_awake(url):

    def worker():

        while True:

            try:
                urllib.request.urlopen(
                    url,
                    timeout=10
                )

            except Exception:
                pass

            time.sleep(600)

    thread = threading.Thread(
        target=worker,
        daemon=True
    )

    thread.start()


# =========================================================
# START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        "🇺🇿 <b>English ↔ Uzbek TEST BOT</b>\n\n"
        "📚 150 ta so‘z\n"
        "🎲 Har safar RANDOM tartib\n"
        "🔄 English ↔ Uzbek aralash\n"
        "🧠 Aqlli javob tekshirish\n\n"
        "▶️ /test — testni boshlash\n"
        "🔄 /restart — boshidan boshlash\n"
        "📊 /score — natijani ko‘rish"
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML"
    )


# =========================================================
# TESTNI BOSHLASH
# =========================================================

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    state[uid] = new_state()

    await update.message.reply_text(
        "🎲 <b>150 ta so‘z aralashtirildi!</b>\n"
        "Har safar tartib boshqacha bo‘ladi.\n\n"
        "🚀 Test boshlandi!",
        parse_mode="HTML"
    )

    await ask(update, context)


# =========================================================
# RESTART
# =========================================================

async def restart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await test_command(update, context)


# =========================================================
# SCORE
# =========================================================

async def score_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    if uid not in state:

        await update.message.reply_text(
            "Avval /test buyrug‘ini bosing."
        )

        return

    s = state[uid]

    total = s["index"]

    if total == 0:
        accuracy = 0
    else:
        accuracy = s["score"] / total * 100

    await update.message.reply_text(
        f"📊 <b>Natija</b>\n\n"
        f"🏆 To‘g‘ri: {s['score']}/{total}\n"
        f"📈 Aniqlik: {accuracy:.1f}%\n"
        f"🔥 Eng uzun combo: {s['best_combo']}",
        parse_mode="HTML"
    )


# =========================================================
# SAVOLNI CHIQARISH
# =========================================================

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    if uid not in state:
        return

    s = state[uid]

    index = s["index"]

    # Test tugagan bo‘lsa
    if index >= len(WORDS):
        await finish_test(update, context)
        return

    # =====================================================
    # RANDOM INDEX
    # =====================================================

    real_index = s["order"][index]

    word, uzbek = WORDS[real_index]

    # Yo‘nalishni random tanlaymiz
    direction = random.choice([
        "en_to_uz",
        "uz_to_en"
    ])

    s["direction"] = direction
    s["real_index"] = real_index

    # =====================================================
    # ENGLISH -> UZBEK
    # =====================================================

    if direction == "en_to_uz":

        flag = get_flag(word)

        flag_text = f"{flag} " if flag else "🇬🇧 "

        question = (
            f"❓ <b>{index + 1}/150</b>\n\n"
            f"{flag_text}<b>{word}</b>\n\n"
            f"🇺🇿 O‘zbekchasini yozing:"
        )

    # =====================================================
    # UZBEK -> ENGLISH
    # =====================================================

    else:

        question = (
            f"❓ <b>{index + 1}/150</b>\n\n"
            f"🇺🇿 <b>{uzbek}</b>\n\n"
            f"🇬🇧 Inglizchasini yozing:"
        )

    msg = await update.effective_chat.send_message(
        question,
        parse_mode="HTML"
    )

    s["current_message_id"] = msg.message_id


# =========================================================
# JAVOB QABUL QILISH
# =========================================================

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    if uid not in state:
        return

    s = state[uid]

    user_answer = update.message.text.strip()

    index = s["index"]

    if index >= len(WORDS):
        return

    # RANDOM TANLANGAN SO‘Z
    real_index = s["order"][index]

    word, uzbek = WORDS[real_index]

    direction = s.get("direction", "en_to_uz")

    # =====================================================
    # EXPECTED JAVOB
    # =====================================================

    if direction == "en_to_uz":

        expected = uzbek

    else:

        expected = word

    # =====================================================
    # TEKSHIRISH
    # =====================================================

    correct = is_correct(
        user_answer,
        expected,
        english_word=word
    )

    # =====================================================
    # TO‘G‘RI
    # =====================================================

    if correct:

        s["score"] += 1
        s["round_score"] += 1

        s["combo"] += 1

        if s["combo"] > s["best_combo"]:
            s["best_combo"] = s["combo"]

        await update.message.reply_text(
            "✅ <b>To‘g‘ri!</b>",
            parse_mode="HTML"
        )

        # Combo
        if s["combo"] >= 3:

            await update.message.reply_text(
                f"🔥 <b>COMBO x{s['combo']}!</b>",
                parse_mode="HTML"
            )

    # =====================================================
    # XATO
    # =====================================================

    else:

        s["combo"] = 0

        await update.message.reply_text(
            f"❌ <b>Noto‘g‘ri.</b>\n"
            f"To‘g‘ri javob: <b>{expected}</b>",
            parse_mode="HTML"
        )

    # Keyingi savol
    s["index"] += 1

    # =====================================================
    # 150 TA SAVOL TUGADI
    # MUHIM: avval shuni tekshiramiz
    # =====================================================

    if s["index"] >= len(WORDS):

        await finish_test(update, context)

        return

    # =====================================================
    # HAR 10 TA SAVOLDAN KEYIN NATIJA
    # =====================================================

    if s["index"] % ROUND_SIZE == 0:

        await round_result(
            update,
            context
        )

        return

    # Keyingi savol
    await ask(update, context)


# =========================================================
# 10 TALIK NATIJA
# =========================================================

async def round_result(update: Update, context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    s = state[uid]

    end = s["index"]

    start = end - ROUND_SIZE + 1

    round_number = end // ROUND_SIZE

    total_score = s["score"]

    accuracy = total_score / end * 100

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "➡️ Keyingi 10 ta",
                callback_data="next_round"
            )
        ]
    ])

    text = (
        f"📊 <b>{start}–{end}-savollar natijasi</b>\n\n"
        f"🎯 Bosqich natijasi: "
        f"<b>{s['round_score']}/10</b>\n"
        f"🏆 Umumiy natija: "
        f"<b>{total_score}/{end}</b>\n"
        f"📈 Aniqlik: "
        f"<b>{accuracy:.1f}%</b>\n"
        f"🔥 Eng uzun combo: "
        f"<b>{s['best_combo']}</b>\n\n"
        f"➡️ Keyingi 10 ta savolga o‘tish uchun tugmani bosing."
    )

    # Bosqich score'ini keyingi bosqich uchun nol qilamiz
    s["round_score"] = 0

    await update.effective_chat.send_message(
        text,
        parse_mode="HTML",
        reply_markup=keyboard
    )


# =========================================================
# KEYINGI 10 TA
# =========================================================

async def next_round(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    uid = query.from_user.id

    if uid not in state:
        return

    # Tugmani olib tashlaymiz
    try:
        await query.edit_message_reply_markup(
            reply_markup=None
        )
    except Exception:
        pass

    await ask_from_callback(
        query,
        context
    )


# =========================================================
# CALLBACK ORQALI SAVOL
# =========================================================

async def ask_from_callback(query, context):

    uid = query.from_user.id

    if uid not in state:
        return

    s = state[uid]

    index = s["index"]

    if index >= len(WORDS):

        await finish_test_from_callback(
            query,
            context
        )

        return

    real_index = s["order"][index]

    word, uzbek = WORDS[real_index]

    direction = random.choice([
        "en_to_uz",
        "uz_to_en"
    ])

    s["direction"] = direction
    s["real_index"] = real_index

    if direction == "en_to_uz":

        flag = get_flag(word)

        flag_text = f"{flag} " if flag else "🇬🇧 "

        question = (
            f"❓ <b>{index + 1}/150</b>\n\n"
            f"{flag_text}<b>{word}</b>\n\n"
            f"🇺🇿 O‘zbekchasini yozing:"
        )

    else:

        question = (
            f"❓ <b>{index + 1}/150</b>\n\n"
            f"🇺🇿 <b>{uzbek}</b>\n\n"
            f"🇬🇧 Inglizchasini yozing:"
        )

    msg = await query.message.chat.send_message(
        question,
        parse_mode="HTML"
    )

    s["current_message_id"] = msg.message_id


# =========================================================
# TESTNI YAKUNLASH
# =========================================================

async def finish_test(update, context):

    uid = update.effective_user.id

    if uid not in state:
        return

    s = state[uid]

    score = s["score"]

    accuracy = score / len(WORDS) * 100

    if accuracy >= 90:
        level = "🏆 Ajoyib!"
    elif accuracy >= 75:
        level = "🔥 Juda yaxshi!"
    elif accuracy >= 60:
        level = "👍 Yaxshi!"
    else:
        level = "💪 Yana mashq qilish kerak!"

    text = (
        "🎉 <b>TEST TUGADI!</b>\n\n"
        f"🏆 Natijangiz: <b>{score}/150</b>\n"
        f"📈 Aniqlik: <b>{accuracy:.1f}%</b>\n"
        f"🔥 Eng uzun combo: <b>{s['best_combo']}</b>\n\n"
        f"{level}\n\n"
        "🔄 Yana random test boshlash uchun /test bosing."
    )

    await update.effective_chat.send_message(
        text,
        parse_mode="HTML"
    )


# =========================================================
# CALLBACK ORQALI YAKUNLASH
# =========================================================

async def finish_test_from_callback(query, context):

    uid = query.from_user.id

    if uid not in state:
        return

    s = state[uid]

    score = s["score"]

    accuracy = score / len(WORDS) * 100

    if accuracy >= 90:
        level = "🏆 Ajoyib
