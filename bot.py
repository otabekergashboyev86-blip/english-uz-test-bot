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

assert len(WORDS) == 150, f"WORDS 150 ta bo‘lishi kerak, hozir {len(WORDS)} ta"

FLAGS = {
    "Argentina": "🇦🇷", "Brazil": "🇧🇷", "Canada": "🇨🇦",
    "Italy": "🇮🇹", "Japan": "🇯🇵", "Mexico": "🇲🇽",
    "Poland": "🇵🇱", "Spain": "🇪🇸", "Thailand": "🇹🇭",
    "Great Britain": "🇬🇧", "The UK": "🇬🇧",
    "The USA (The US)": "🇺🇸", "Turkey": "🇹🇷",
    "British": "🇬🇧", "Polish": "🇵🇱", "Spanish": "🇪🇸",
    "Turkish": "🇹🇷", "Mexican": "🇲🇽", "Japanese": "🇯🇵",
    "Italian": "🇮🇹", "American": "🇺🇸", "Canadian": "🇨🇦",
    "Brazilian": "🇧🇷", "Argentinian": "🇦🇷", "Thai": "🇹🇭",
}

ROUND_SIZE = 10
state = {}
RNG = random.SystemRandom()


def get_flag(word):
    return FLAGS.get(word, "🇬🇧")


def norm(text):
    if text is None:
        return ""

    text = unicodedata.normalize("NFKC", str(text)).lower().strip()

    for ch in ("’", "‘", "ʻ", "ʼ", "`", "´", "′"):
        text = text.replace(ch, "'")

    text = re.sub(r"\s+", " ", text)
    text = text.strip(" .!?")

    return text


# Extra answers accepted by the bot.
# These do NOT change the 150-word dictionary.
EXTRA_ALIASES = {
    "work": ["ish", "ishlamoq", "mehnat qilmoq"],
    "help": ["yordam", "yordam bermoq"],
    "father": ["ota", "dada"],
    "mother": ["ona", "oyi"],
    "parents": ["ota-ona", "ota ona", "ota va ona"],
    "cousin(e)": [
        "amakivachcha", "xolavachcha", "tog'avachcha",
        "togavachcha", "ammavachcha",
    ],
    "nephew": [
        "jiyan", "jiyan o'g'il", "o'g'il jiyan",
        "jiyan o'g'il bola", "o'g'il bola",
    ],
    "niece": [
        "jiyan", "jiyan qiz", "qiz jiyan",
        "jiyan qiz bola", "qiz bola",
    ],
    "husband": ["eri", "er", "erim", "turmush o'rtog'i"],
    "wife": ["xotin", "rafiqa", "xotinim", "turmush o'rtog'i"],
    "nice to meet you": [
        "tanishganimdan xursandman",
        "tanishganimdan hursandman",
        "tanishganimdan mamnunman",
    ],
    "desk": ["parta"],
    "table": ["stol"],
    "school teacher": ["ustoz", "o'qituvchi", "oqituvchi"],
    "job": ["kasb", "ish"],
    "page": ["sahifa", "bet"],
    "correct": ["to'g'ri", "tog'ri", "to'g'rilamoq", "togrilamoq"],
    "some": ["ba'zi", "bazi", "bir nechta"],
    "make": ["qilmoq", "yasamoq"],
    "all": ["hamma", "barcha"],
    "photo": ["rasm", "surat"],
    "class": ["dars", "sinf"],
    "true": ["to'g'ri", "tog'ri"],
    "false": ["noto'g'ri", "notog'ri"],
    "what": ["nima", "qanday"],
    "how often": ["nechi marta", "qancha tez-tez", "qanchalik tez-tez"],
    "here you are": ["mana", "marhamat"],
    "cash or card?": [
        "naqd pulmi yoki karta",
        "naqd pul yoki karta",
        "naqdmi yoki karta",
    ],
}


def build_options(en, uz, direction):
    expected = uz if direction == "en_to_uz" else en
    options = [expected]

    # Vergul bilan ajratilgan javoblar.
    if direction == "en_to_uz" and "," in expected:
        options.extend(x.strip() for x in expected.split(",") if x.strip())

    # Slash bilan ajratilgan javoblar.
    if direction == "en_to_uz" and "/" in expected:
        options.extend(x.strip() for x in expected.split("/") if x.strip())

    # Qavsli variantlar: The USA (The US), jiyan (o'g'il), etc.
    if "(" in expected and ")" in expected:
        outside = re.sub(r"\s*\([^)]*\)", "", expected).strip()
        inside_match = re.search(r"\(([^)]*)\)", expected)

        if outside:
            options.append(outside)
        if inside_match:
            options.append(inside_match.group(1).strip())

    if direction == "en_to_uz":
        options.extend(EXTRA_ALIASES.get(en.lower(), []))

    # Inglizcha javobda qavsli yozuvning soddalashtirilgan shakllari.
    if direction == "uz_to_en" and "(" in en and ")" in en:
        options.append(re.sub(r"\s*\([^)]*\)", "", en).strip())
        m = re.search(r"\(([^)]*)\)", en)
        if m:
            options.append(m.group(1).strip())

    return list(dict.fromkeys(options))


def is_correct(user_answer, en, uz, direction):
    user = norm(user_answer)

    if not user:
        return False

    return user in {
        norm(x)
        for x in build_options(en, uz, direction)
        if norm(x)
    }


def new_state():
    # MUHIM: random.sample barcha 150 indexni bir marta aralashtiradi.
    # Bir test ichida takroriy so'z bo'lmaydi.
    order = RNG.sample(range(len(WORDS)), len(WORDS))

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


async def safe_delete(bot, chat_id, message_id):
    if not message_id:
        return
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass


async def ask(update, context):
    uid = update.effective_user.id
    s = state.get(uid)

    if not s:
        return

    index = s["index"]

    if index >= len(WORDS):
        await finish_test(update, context)
        return

    # RANDOM savol.
    # Masalan 1-savolda WORDS[73], 2-savolda WORDS[4] chiqishi mumkin.
    word_index = s["order"][index]
    en, uz = WORDS[word_index]

    # Har savolda yo'nalish ham RANDOM.
    direction = RNG.choice(("en_to_uz", "uz_to_en"))
    s["direction"] = direction
    s["answered"] = False

    flag = get_flag(en)

    if direction == "en_to_uz":
        text = (
            f"❓ {index + 1}/{len(WORDS)}\n\n"
            f"{flag} {en}\n\n"
            f"🇺🇿 O‘zbekchasini yozing:"
        )
    else:
        text = (
            f"❓ {index + 1}/{len(WORDS)}\n\n"
            f"🇺🇿 {uz}\n\n"
            f"{flag} Inglizchasini yozing:"
        )

    msg = await update.effective_message.reply_text(text)
    s["question_message_id"] = msg.message_id


async def start_test(update, context):
    uid = update.effective_user.id

    # Har /test bosilganda yangi random tartib yaratiladi.
    state[uid] = new_state()

    await update.message.reply_text(
        "🚀 Test boshlandi!\n\n"
        "📚 Jami: 150 ta so‘z\n"
        "📝 Har bosqich: 10 ta savol\n"
        "🎲 Savollar: RANDOM\n"
        "🔄 Yo‘nalish: RANDOM\n"
        "♻️ Takroriy savol: YO‘Q\n\n"
        "Omad! 🔥"
    )

    await ask(update, context)


async def restart_game(update, context):
    await start_test(update, context)


async def score_command(update, context):
    uid = update.effective_user.id
    s = state.get(uid)

    if not s:
        await update.message.reply_text(
            "Avval /test buyrug‘ini bosing."
        )
        return

    answered = s["index"]
    accuracy = (s["score"] / answered * 100) if answered else 0

    await update.message.reply_text(
        f"📊 Natija\n\n"
        f"🏆 {s['score']}/{answered}\n"
        f"📈 Aniqlik: {accuracy:.1f}%\n"
        f"🔥 Eng uzun combo: {s['max_combo']}"
    )


async def answer(update, context):
    uid = update.effective_user.id
    s = state.get(uid)

    if not s or s["answered"]:
        return

    index = s["index"]

    if index >= len(WORDS):
        return

    # MUHIM: aynan random order'dagi so'z olinadi.
    word_index = s["order"][index]
    en, uz = WORDS[word_index]
    direction = s["direction"]

    user_answer = update.message.text.strip()

    correct = is_correct(
        user_answer,
        en,
        uz,
        direction,
    )

    await safe_delete(
        context.bot,
        update.effective_chat.id,
        s.get("question_message_id"),
    )

    s["answered"] = True

    if correct:
        s["score"] += 1
        s["round_correct"] += 1
        s["combo"] += 1
        s["max_combo"] = max(s["max_combo"], s["combo"])

        if s["combo"] >= 3:
            await update.message.reply_text(
                f"✅ To‘g‘ri!\n🔥 COMBO x{s['combo']}!"
            )
        else:
            await update.message.reply_text("✅ To‘g‘ri!")

    else:
        s["combo"] = 0

        correct_answer = uz if direction == "en_to_uz" else en

        await update.message.reply_text(
            f"❌ Noto‘g‘ri.\n"
            f"To‘g‘ri javob: {correct_answer}"
        )

    s["index"] += 1

    # 150-savoldan keyin darhol final.
    if s["index"] >= len(WORDS):
        await finish_test(update, context)
        return

    # Har 10 savoldan keyin natija.
    if s["index"] % ROUND_SIZE == 0:
        await round_result(update, context)
        return

    await ask(update, context)


async def round_result(update, context):
    uid = update.effective_user.id
    s = state.get(uid)

    if not s:
        return

    end = s["index"]
    start = end - ROUND_SIZE + 1
    round_score = s["round_correct"]

    s["rounds"] += 1

    accuracy = s["score"] / end * 100

    text = (
        f"📊 {start}–{end}-savollar natijasi\n\n"
        f"🎯 Bosqich natijasi: {round_score}/{ROUND_SIZE}\n"
        f"🏆 Umumiy natija: {s['score']}/{end}\n"
        f"📈 Aniqlik: {accuracy:.1f}%\n"
        f"🔥 Eng uzun combo: {s['max_combo']}\n\n"
        f"➡️ Keyingi 10 ta savolga o'tish uchun tugmani bosing."
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "➡️ Keyingi 10 ta",
                callback_data="next_round",
            )
        ]
    ]

    await update.effective_message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    s["round_correct"] = 0


async def next_round(update, context):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id
    s = state.get(uid)

    if not s:
        await query.message.reply_text(
            "Avval /test buyrug‘ini bosing."
        )
        return

    await query.message.delete()

    # Muhim: order qayta aralashtirilmaydi.
    # Shuning uchun bir test ichida so'z takrorlanmaydi.
    fake_update = update

    await ask(fake_update, context)


async def finish_test(update, context):
    uid = update.effective_user.id
    s = state.get(uid)

    if not s:
        return

    total = len(WORDS)
    score = s["score"]
    accuracy = score / total * 100

    if accuracy >= 90:
        level = "🏆 A’lo!"
    elif accuracy >= 75:
        level = "🥇 Juda yaxshi!"
    elif accuracy >= 60:
        level = "🥈 Yaxshi!"
    elif accuracy >= 50:
        level = "🥉 Yomon emas!"
    else:
        level = "💪 Yana mashq qilamiz!"

    await update.effective_message.reply_text(
        "🎉 TEST TUGADI!\n\n"
        f"📚 Jami savollar: {total}\n"
        f"✅ To‘g‘ri javoblar: {score}\n"
        f"❌ Xato javoblar: {total - score}\n"
        f"📈 Aniqlik: {accuracy:.1f}%\n"
        f"🔥 Eng uzun combo: {s['max_combo']}\n\n"
        f"{level}\n\n"
        "🔄 Qaytadan ishlash uchun /test"
    )


async def start_command(update, context):
    await update.message.reply_text(
        "🇺🇿 English ↔ Uzbek test bot\n\n"
        "/test — testni boshlash\n"
        "/restart — testni qayta boshlash\n"
        "/score — natijani ko‘rish"
    )


# ============================================================
# RENDER UCHUN KEEP-AWAKE
# ============================================================

def keep_render_awake(url):
    def worker():
        while True:
            try:
                urllib.request.urlopen(url, timeout=15).read()
            except Exception:
                pass

            time.sleep(600)

    thread = threading.Thread(
        target=worker,
        daemon=True,
    )
    thread.start()


# ============================================================
# MAIN
# ============================================================

def main():
    token = os.getenv("BOT_TOKEN")
    hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME")
    port = int(os.getenv("PORT", "10000"))

    if not token:
        raise RuntimeError("BOT_TOKEN topilmadi.")

    if not hostname:
        raise RuntimeError(
            "RENDER_EXTERNAL_HOSTNAME topilmadi."
        )

    application = (
        Application.builder()
        .token(token)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start_command)
    )

    application.add_handler(
        CommandHandler("test", start_test)
    )

    application.add_handler(
        CommandHandler("restart", restart_game)
    )

    application.add_handler(
        CommandHandler("score", score_command)
    )

    application.add_handler(
        CallbackQueryHandler(
            next_round,
            pattern="^next_round$",
        )
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            answer,
        )
    )

    webhook_path = "telegram"
    webhook_url = f"https://{hostname}/{webhook_path}"

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
