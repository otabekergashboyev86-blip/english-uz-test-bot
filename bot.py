import os
import re
import random
import unicodedata

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

state = {}
group_sessions = {}


# =========================================================
# NORMALIZATSIYA
# =========================================================

def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", str(s))
    s = s.lower().strip()

    for ch in ["’", "‘", "ʻ", "ʼ", "`", "´"]:
        s = s.replace(ch, "'")

    s = re.sub(r"\s+", " ", s)

    return s.strip(" .!?")


# =========================================================
# JAVOBNI TEKSHIRISH
# =========================================================

def is_correct(user_answer: str, expected: str) -> bool:
    user = norm(user_answer)
    expected = str(expected).strip()

    options = set()

    # To'liq javob
    options.add(norm(expected))

    # Vergul yoki / bilan ajratilgan variantlar
    for part in re.split(r"\s*(?:,|/)\s*", expected):
        if part.strip():
            options.add(norm(part))

    # Qavs ichidagi variantlar
    match = re.search(r"\(([^()]*)\)", expected)

    if match:
        before = expected[:match.start()].strip()
        inside = match.group(1).strip()
        after = expected[match.end():].strip()

        if before or after:
            without_parentheses = f"{before} {after}".strip()
            options.add(norm(without_parentheses))

            with_inside = f"{before} {inside} {after}".strip()
            options.add(norm(with_inside))

        if inside:
            options.add(norm(inside))

    return user in options


# =========================================================
# GURUHMI?
# =========================================================

def is_group(update: Update) -> bool:
    if not update.effective_chat:
        return False

    return update.effective_chat.type in [
        "group",
        "supergroup",
    ]


# =========================================================
# USER KEY
# =========================================================

def get_key(update: Update):
    return (
        update.effective_chat.id,
        update.effective_user.id,
    )


# =========================================================
# YANGI STATE
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
        "waiting_nickname": False,

        "nickname": "",
        "finished": False,
    }


# =========================================================
# START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "👋 Assalomu alaykum!\n\n"
        "🇬🇧 English — 🇺🇿 Uzbek test botiga xush kelibsiz!\n\n"
        "📚 Jami so‘zlar: 111 ta\n"
        "📝 Har bosqich: 10 ta savol\n\n"
        "Buyruqlar:\n"
        "/test — testni boshlash\n"
        "/restart — testni qayta boshlash\n"
        "/score — natijani ko‘rish"
    )


# =========================================================
# TEST
# =========================================================

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):

    key = get_key(update)

    # =====================================================
    # GURUH
    # =====================================================

    if is_group(update):

        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        session = group_sessions.get(chat_id)

        # Yangi guruh testi
        if session is None or session["all_finished"]:

            session = {
                "players": {},
                "all_finished": False,
            }

            group_sessions[chat_id] = session

        # Agar shu odam allaqachon testda bo'lsa
        if user_id in session["players"]:

            player = session["players"][user_id]

            if not player["finished"]:

                await update.message.reply_text(
                    "⚠️ Siz allaqachon testdasiz."
                )

                return

            # Eski tugagan ishtirokchini yangi testga qayta qo'shamiz
            session["players"].pop(user_id, None)

        s = new_state()

        s["waiting_nickname"] = True

        state[key] = s

        await update.message.reply_text(
            "👤 Ismingizni yozing.\n\n"
            "Masalan: Otabek yoki Kumush"
        )

        return

    # =====================================================
    # PRIVATE
    # =====================================================

    state[key] = new_state()

    await ask(update, context)


# =========================================================
# RESTART
# =========================================================

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):

    key = get_key(update)

    # =====================================================
    # GURUH
    # =====================================================

    if is_group(update):

        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        session = group_sessions.get(chat_id)

        if session is None:

            session = {
                "players": {},
                "all_finished": False,
            }

            group_sessions[chat_id] = session

        session["players"].pop(user_id, None)
        session["all_finished"] = False

        s = new_state()
        s["waiting_nickname"] = True

        state[key] = s

        await update.message.reply_text(
            "🔄 Test qayta boshlandi!\n\n"
            "👤 Ismingizni yozing.\n\n"
            "Masalan: Otabek yoki Kumush"
        )

        return

    # =====================================================
    # PRIVATE
    # =====================================================

    state[key] = new_state()

    await update.message.reply_text(
        "🔄 Test qayta boshlandi!"
    )

    await ask(update, context)


# =========================================================
# NICKNAME
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

    if key not in state:
        return False

    s = state[key]

    if not s["waiting_nickname"]:
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

    if session is None:

        session = {
            "players": {},
            "all_finished": False,
        }

        group_sessions[chat_id] = session

    s["nickname"] = nickname
    s["waiting_nickname"] = False
    s["finished"] = False

    session["players"][user_id] = {
        "nickname": nickname,
        "state_key": key,
        "finished": False,
    }

    # Faqat nickname xabarini o'chiramiz
    try:
        await update.message.delete()
    except Exception:
        pass

    await update.effective_chat.send_message(
        f"✅ {nickname} ro‘yxatdan o‘tdi!\n\n"
        "🚀 Test boshlandi!"
    )

    # Savolni yuborish
    await ask(update, context)

    return True


# =========================================================
# SAVOL
# =========================================================

async def ask(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    key = get_key(update)

    if key not in state:
        return

    s = state[key]

    index = s["index"]

    if index >= len(WORDS):

        await finish_test(
            update,
            context
        )

        return

    word, uzbek = WORDS[index]

    # Har savolda yo'nalish tasodifiy
    direction = random.choice([
        "en_uz",
        "uz_en",
    ])

    s["direction"] = direction

    # =====================================================
    # ENGLISH -> UZBEK
    # =====================================================

    if direction == "en_uz":

        s["expected"] = uzbek

        flag = FLAGS.get(word, "")

        if flag:
            word_text = f"{flag} {word}"
        else:
            word_text = word

        question = (
            f"❓ {index + 1}/{len(WORDS)}\n\n"
            f"🇬🇧 {word_text}\n\n"
            "🇺🇿 O‘zbekchasini yozing:"
        )

    # =====================================================
    # UZBEK -> ENGLISH
    # =====================================================

    else:

        s["expected"] = word

        question = (
            f"❓ {index + 1}/{len(WORDS)}\n\n"
            f"🇺🇿 {uzbek}\n\n"
            "🇬🇧 Inglizchasini yozing:"
        )

    # =====================================================
    # GURUHDA
    # =====================================================

    if is_group(update):

        # MUHIM:
        # Savol alohida yuboriladi.
        # Keyinchalik answer() faqat foydalanuvchi
        # javobini o'chiradi.
        # Savolga tegilmaydi.

        await update.effective_chat.send_message(
            question
        )

    # =====================================================
    # PRIVATE
    # =====================================================

    else:

        await update.effective_chat.send_message(
            question
        )


# =========================================================
# JAVOB
# =========================================================

async def answer(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    if not update.message.text:
        return

    key = get_key(update)

    if key not in state:
        return

    s = state[key]

    # Nickname kutilayotgan bo'lsa
    if s["waiting_nickname"]:
        return

    # Keyingi 10 ta tugmasi kutilayotgan bo'lsa
    if s["waiting_next_round"]:

        if is_group(update):

            try:
                await update.message.delete()
            except Exception:
                pass

        return

    # Test tugagan
    if s["finished"]:
        return

    user_answer = update.message.text.strip()

    expected = s["expected"]

    correct = is_correct(
        user_answer,
        expected
    )

    # =====================================================
    # GURUHDA FAQAT FOYDALANUVCHI JAVOBINI O'CHIRAMIZ
    # =====================================================

    if is_group(update):

        try:
            await update.message.delete()
        except Exception:
            pass

    # =====================================================
    # TO'G'RI
    # =====================================================

    if correct:

        s["score"] += 1
        s["round_score"] += 1
        s["combo"] += 1

        if s["combo"] > s["longest_combo"]:
            s["longest_combo"] = s["combo"]

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
            s["combo"] > 5
            and s["combo"] % 5 == 0
        ):

            result += (
                f"\n\n🔥 COMBO x{s['combo']}!"
            )

    # =====================================================
    # XATO
    # =====================================================

    else:

        s["combo"] = 0

        s["round_wrong"].append({
            "word": WORDS[s["index"]][0],
            "uzbek": WORDS[s["index"]][1],
        })

        # Guruhda to'g'ri javobni ko'rsatmaymiz
        result = "❌ Noto‘g‘ri."

    # =====================================================
    # NATIJANI YUBORISH
    # =====================================================

    if is_group(update):

        await update.effective_chat.send_message(
            result
        )

    else:

        await update.effective_chat.send_message(
            result
        )

    # =====================================================
    # KEYINGI SAVOL
    # =====================================================

    s["index"] += 1

    if (
        s["index"] % ROUND_SIZE == 0
        or s["index"] >= len(WORDS)
    ):

        await round_result(
            update,
            context
        )

    else:

        await ask(
            update,
            context
        )


# =========================================================
# 10 TALIK NATIJA
# =========================================================

async def round_result(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    key = get_key(update)

    if key not in state:
        return

    s = state[key]

    s["rounds"] += 1

    round_number = s["rounds"]

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
        end_number - start_number + 1
    )

    percentage = (
        s["score"]
        / end_number
        * 100
    )

    text = (
        f"📊 {round_number}-BOSQICH NATIJASI\n\n"
        f"📝 Savollar: "
        f"{start_number}–{end_number}\n"
        f"✅ To‘g‘ri: "
        f"{s['round_score']}/{question_count}\n"
        f"🏆 Umumiy ochko: "
        f"{s['score']}/{end_number}\n"
        f"📈 Foiz: "
        f"{percentage:.1f}%\n"
        f"🔥 Combo: x{s['combo']}\n"
        f"⚡ Eng uzun combo: "
        f"x{s['longest_combo']}"
    )

    # =====================================================
    # XATO SO'ZLAR
    # =====================================================

    if s["round_wrong"]:

        text += (
            "\n\n❌ XATO QILINGAN SO‘ZLAR:"
        )

        for item in s["round_wrong"]:

            text += (
                f"\n\n"
                f"• 🇬🇧 {item['word']}\n"
                f"  🇺🇿 {item['uzbek']}"
            )

    else:

        text += (
            "\n\n🎉 Bu bosqichda xato yo‘q!"
        )

    # =====================================================
    # 111 TA TUGAGAN
    # =====================================================

    if s["index"] >= len(WORDS):

        await send_message(
            update,
            text
        )

        await finish_test(
            update,
            context,
            already_sent=True
        )

        return

    # =====================================================
    # KEYINGI 10 TA
    # =====================================================

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
        "\n\n👇 Davom etish uchun tugmani bosing."
    )

    await send_message(
        update,
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

    key = get_key(update)

    if key not in state:
        return

    s = state[key]

    if not s["waiting_next_round"]:
        return

    s["waiting_next_round"] = False
    s["round_score"] = 0
    s["round_wrong"] = []

    await ask(
        update,
        context
    )


# =========================================================
# XABAR YUBORISH
# =========================================================

async def send_message(
    update: Update,
    text: str,
    reply_markup=None
):

    if is_group(update):

        await update.effective_chat.send_message(
            text,
            reply_markup=reply_markup
        )

    else:

        await update.effective_chat.send_message(
            text,
            reply_markup=reply_markup
        )


# =========================================================
# TEST YAKUNI
# =========================================================

async def finish_test(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    already_sent=False
):

    key = get_key(update)

    if key not in state:
        return

    s = state[key]

    if s["finished"]:
        return

    s["finished"] = True

    # =====================================================
    # GURUH
    # =====================================================

    if is_group(update):

        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        session = group_sessions.get(chat_id)

        if session and user_id in session["players"]:

            session["players"][user_id]["finished"] = True

        await show_group_leaderboard(
            update,
            context
        )

        return

    # =====================================================
    # PRIVATE
    # =====================================================

    percentage = (
        s["score"]
        / len(WORDS)
        * 100
    )

    if already_sent:
        text = ""
    else:
        text = "🎉 TEST TUGADI!\n\n"

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

    await send_message(
        update,
        text,
        reply_markup=keyboard
    )


# =========================================================
# GURUH LEADERBOARD
# =========================================================

async def show_group_leaderboard(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not is_group(update):
        return

    chat_id = update.effective_chat.id

    session = group_sessions.get(chat_id)

    if not session:
        return

    players = session["players"]

    if not players:
        return

    finished_count = sum(
        1
        for player in players.values()
        if player["finished"]
    )

    total_count = len(players)

    # =====================================================
    # HAMMA TUGATMAGAN
    # =====================================================

    if finished_count < total_count:

        await update.effective_chat.send_message(
            f"🏁 Siz testni tugatdingiz!\n\n"
            f"👥 Tugatganlar: "
            f"{finished_count}/{total_count}\n\n"
            "⏳ Qolgan ishtirokchilarni kutamiz..."
        )

        return

    # =====================================================
    # NATIJALAR
    # =====================================================

    results = []

    for user_id, player in players.items():

        key = player["state_key"]

        if key not in state:
            continue

        s = state[key]

        results.append({
            "nickname": player["nickname"],
            "score": s["score"],
            "longest_combo": s["longest_combo"],
        })

    # Ochko bo'yicha.
    # Ochko teng bo'lsa combo bo'yicha.
    results.sort(
        key=lambda x: (
            x["score"],
            x["longest_combo"]
        ),
        reverse=True
    )

    text = (
        "🏆 TEST YAKUNIY NATIJALARI!\n\n"
    )

    medals = [
        "🥇",
        "🥈",
        "🥉",
    ]

    for i, result in enumerate(results):

        if i < 3:
            medal = medals[i]
        else:
            medal = f"{i + 1}."

        percentage = (
            result["score"]
            / len(WORDS)
            * 100
        )

        text += (
            f"{medal} {result['nickname']}\n"
            f"   📊 {result['score']}/"
            f"{len(WORDS)} "
            f"({percentage:.1f}%)\n"
            f"   🔥 Combo: "
            f"x{result['longest_combo']}\n\n"
        )

    # =====================================================
    # G'OLIB
    # =====================================================

    if results:

        winner = results[0]

        winner_percentage = (
            winner["score"]
            / len(WORDS)
            * 100
        )

        text += (
            "🎉🎉🎉 G‘OLIB 🎉🎉🎉\n\n"
            f"🏆 {winner['nickname']}\n"
            f"📊 {winner['score']}/"
            f"{len(WORDS)} "
            f"({winner_percentage:.1f}%)\n"
            f"🔥 Eng uzun combo: "
            f"x{winner['longest_combo']}"
        )

    await update.effective_chat.send_message(
        text
    )

    session["all_finished"] = True


# =========================================================
# SCORE
# =========================================================

async def score(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    key = get_key(update)

    if key not in state:

        await update.message.reply_text(
            "📊 Hozircha test boshlanmagan.\n\n"
            "/test — testni boshlash"
        )

        return

    s = state[key]

    if s["index"] > 0:

        percentage = (
            s["score"]
            / s["index"]
            * 100
        )

    else:

        percentage = 0

    await update.message.reply_text(
        "📊 SIZNING NATIJANGIZ\n\n"
        f"✅ To‘g‘ri: {s['score']}\n"
        f"❓ Javob berilgan: {s['index']}\n"
        f"📈 Foiz: {percentage:.1f}%\n"
        f"🔥 Hozirgi combo: x{s['combo']}\n"
        f"⚡ Eng uzun combo: x{s['longest_combo']}\n"
        f"📚 Bosqichlar: {s['rounds']}"
    )


# =========================================================
# RESTART TUGMASI
# =========================================================

async def restart_game(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    if not query:
        return

    await query.answer()

    key = get_key(update)

    state[key] = new_state()

    # =====================================================
    # GURUH
    # =====================================================

    if is_group(update):

        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        session = group_sessions.get(chat_id)

        if session:

            session["players"].pop(
                user_id,
                None
            )

            session["all_finished"] = False

        state[key]["waiting_nickname"] = True

        await update.effective_chat.send_message(
            "🔄 Test qayta boshlandi!\n\n"
            "👤 Ismingizni yozing.\n\n"
            "Masalan: Otabek yoki Kumush"
        )

        return

    # =====================================================
    # PRIVATE
    # =====================================================

    await update.effective_chat.send_message(
        "🔄 Test qayta boshlandi!"
    )

    await ask(
        update,
        context
    )


# =========================================================
# TEXT XABARLAR
# =========================================================

async def handle_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    if not update.message.text:
        return

    # =====================================================
    # NICKNAME
    # =====================================================

    if is_group(update):

        key = get_key(update)

        if key in state:

            s = state[key]

            if s["waiting_nickname"]:

                handled = await register_nickname(
                    update,
                    context
                )

                if handled:
                    return

    # =====================================================
    # JAVOB
    # =====================================================

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
            "RENDER_EXTERNAL_HOSTNAME topilmadi!"
        )

    application = (
        Application.builder()
        .token(token)
        .build()
    )

    # =====================================================
    # COMMANDS
    # =====================================================

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

    # =====================================================
    # BUTTONS
    # =====================================================

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

    # =====================================================
    # TEXT
    # =====================================================

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_text
        )
    )

    # =====================================================
    # WEBHOOK
    # =====================================================

    webhook_path = "telegram"

    webhook_url = (
        f"https://{hostname}/{webhook_path}"
    )

    # MUHIM:
    # webhook_path EMAS
    # url_path ishlatiladi.
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=webhook_path,
        webhook_url=webhook_url,
        drop_pending_updates=True,
    )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":
    main()
