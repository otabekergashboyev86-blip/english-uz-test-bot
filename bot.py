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

FLAGS = {
    "Argentina": "🇦🇷", "Brazil": "🇧🇷", "Canada": "🇨🇦",
    "Italy": "🇮🇹", "Japan": "🇯🇵", "Mexico": "🇲🇽",
    "Poland": "🇵🇱", "Spain": "🇪🇸", "Thailand": "🇹🇭",
    "Great Britain": "🇬🇧", "The UK": "🇬🇧",
    "The USA (The US)": "🇺🇸", "Turkey": "🇹🇷",
}

ROUND_SIZE = 10
state = {}
group_sessions = {}


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
            options.add(norm(f"{before} {after}".strip()))
            options.add(norm(f"{before} {inside} {after}".strip()))
        if inside:
            options.add(norm(inside))
    return options


def is_correct(user_answer: str, expected: str) -> bool:
    options = build_options(expected)
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
        "index": 0, "score": 0, "combo": 0, "longest_combo": 0,
        "round_score": 0, "round_wrong": [], "rounds": 0,
        "expected": "", "direction": "", "waiting_next_round": False,
        "waiting_nickname": False, "nickname": "", "finished": False,
        "question_message_id": None,
    }


async def safe_delete(bot, chat_id, message_id):
    if not message_id:
        return
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass


def keep_render_awake(url: str):
    # Render sleep bo‘lsa, bu funksiya jarayon tirik paytda ping yuboradi.
    # Bu Render Free uyqusini 100% kafolat bilan bekor qilmaydi.
    def ping_loop():
        while True:
            try:
                urllib.request.urlopen(url, timeout=20).close()
            except Exception:
                pass
            time.sleep(600)
    threading.Thread(target=ping_loop, daemon=True).start()


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


async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = get_key(update)
    if is_group(update):
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        session = group_sessions.setdefault(chat_id, {"players": {}, "all_finished": False})
        if session["all_finished"]:
            session["players"] = {}
            session["all_finished"] = False
        if user_id in session["players"] and not session["players"][user_id]["finished"]:
            await update.message.reply_text("⚠️ Siz allaqachon testdasiz.")
            return
        session["players"].pop(user_id, None)
        state[key] = new_state()
        state[key]["waiting_nickname"] = True
        await update.message.reply_text("👤 Ismingizni yozing.\n\nMasalan: Otabek yoki Kumush")
        return
    state[key] = new_state()
    await ask(update, context)


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = get_key(update)
    state[key] = new_state()
    if is_group(update):
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        session = group_sessions.setdefault(chat_id, {"players": {}, "all_finished": False})
        session["players"].pop(user_id, None)
        session["all_finished"] = False
        state[key]["waiting_nickname"] = True
        await update.message.reply_text("🔄 Test qayta boshlandi!\n\n👤 Ismingizni yozing.\n\nMasalan: Otabek yoki Kumush")
        return
    await update.message.reply_text("🔄 Test qayta boshlandi!")
    await ask(update, context)


async def register_nickname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_group(update) or not update.message or not update.message.text:
        return False
    key = get_key(update)
    s = state.get(key)
    if not s or not s["waiting_nickname"]:
        return False
    nickname = update.message.text.strip()
    if not nickname:
        return True
    if len(nickname) > 50:
        await update.message.reply_text("⚠️ Ism juda uzun. 50 ta belgigacha kiriting.")
        return True
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    session = group_sessions.setdefault(chat_id, {"players": {}, "all_finished": False})
    s["nickname"] = nickname
    s["waiting_nickname"] = False
    s["finished"] = False
    session["players"][user_id] = {"nickname": nickname, "state_key": key, "finished": False}
    try:
        await update.message.delete()
    except Exception:
        pass
    await update.effective_chat.send_message(f"✅ {nickname} ro‘yxatdan o‘tdi!\n\n🚀 Test boshlandi!")
    await ask(update, context)
    return True


async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = get_key(update)
    s = state.get(key)
    if not s:
        return
    if s["index"] >= len(WORDS):
        await finish_test(update, context)
        return

    word, uzbek = WORDS[s["index"]]
    direction = random.choice(["en_uz", "uz_en"])
    s["direction"] = direction
    if direction == "en_uz":
        s["expected"] = uzbek
        flag = FLAGS.get(word, "")
        word_text = f"{flag} {word}" if flag else word
        question = f"❓ {s['index'] + 1}/{len(WORDS)}\n\n🇬🇧 {word_text}\n\n🇺🇿 O‘zbekchasini yozing:"
    else:
        s["expected"] = word
        question = f"❓ {s['index'] + 1}/{len(WORDS)}\n\n🇺🇿 {uzbek}\n\n🇬🇧 Inglizchasini yozing:"

    if is_group(update):
        nickname = s.get("nickname", "").strip()
        question = f"🎯 {nickname.upper()} UCHUN SAVOL\n\n{question}"

    sent = await update.effective_chat.send_message(question)
    s["question_message_id"] = sent.message_id


async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    key = get_key(update)
    s = state.get(key)
    if not s or s["waiting_nickname"] or s["finished"]:
        return
    if s["waiting_next_round"]:
        if is_group(update):
            await safe_delete(context.bot, update.effective_chat.id, update.message.message_id)
        return

    user_answer = update.message.text.strip()
    expected = s["expected"]
    correct = is_correct(user_answer, expected)

    if is_group(update):
        await safe_delete(context.bot, update.effective_chat.id, update.message.message_id)
        await safe_delete(context.bot, update.effective_chat.id, s.get("question_message_id"))
        s["question_message_id"] = None

    if correct:
        s["score"] += 1
        s["round_score"] += 1
        s["combo"] += 1
        s["longest_combo"] = max(s["longest_combo"], s["combo"])
        result = "✅ To‘g‘ri!"
        if s["combo"] == 3:
            result += "\n\n🔥 COMBO x3!"
        elif s["combo"] == 5:
            result += "\n\n⚡ COMBO x5 — zo‘r!"
        elif s["combo"] > 5 and s["combo"] % 5 == 0:
            result += f"\n\n🔥 COMBO x{s['combo']}!"
    else:
        s["combo"] = 0
        word, uzbek = WORDS[s["index"]]
        s["round_wrong"].append({"word": word, "uzbek": uzbek})
        result = "❌ Noto‘g‘ri."

    # Guruhda savol/javobdan keyin alohida natija xabari qoldirmaymiz.
    # Foydalanuvchi oxirida o‘zining to‘liq natijasini ko‘radi.
    if not is_group(update):
        await update.effective_chat.send_message(result)

    s["index"] += 1
    if s["index"] % ROUND_SIZE == 0 or s["index"] >= len(WORDS):
        await round_result(update, context)
    else:
        await ask(update, context)


async def round_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = get_key(update)
    s = state.get(key)
    if not s:
        return
    s["rounds"] += 1
    round_number = s["rounds"]
    start_number = (round_number - 1) * ROUND_SIZE + 1
    end_number = min(round_number * ROUND_SIZE, len(WORDS))
    question_count = end_number - start_number + 1
    percentage = s["score"] / end_number * 100

    text = (
        f"🏁 {round_number}-round tugadi!\n\n"
        f"📊 Natija: {s['round_score']}/{question_count}\n"
        f"🏆 Umumiy: {s['score']}/{end_number}\n"
        f"📈 Foiz: {percentage:.1f}%\n"
        f"🔥 Combo: x{s['combo']}\n"
        f"⚡ Eng uzun combo: x{s['longest_combo']}"
    )
    if s["round_wrong"]:
        text += "\n\n❌ XATO QILINGAN SO‘ZLAR:"
        for item in s["round_wrong"]:
            text += f"\n\n• 🇬🇧 {item['word']}\n  🇺🇿 {item['uzbek']}"
    else:
        text += "\n\n🎉 Bu bosqichda xato yo‘q!"

    if s["index"] >= len(WORDS):
        await update.effective_chat.send_message(text)
        await finish_test(update, context, already_sent=True)
        return

    s["waiting_next_round"] = True
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("➡️ Keyingi 10 ta", callback_data="next_round")]])
    text += "\n\n👇 Davom etish uchun tugmani bosing."
    await update.effective_chat.send_message(text, reply_markup=keyboard)


async def next_round(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()
    key = get_key(update)
    s = state.get(key)
    if not s or not s["waiting_next_round"]:
        return
    s["waiting_next_round"] = False
    s["round_score"] = 0
    s["round_wrong"] = []
    await ask(update, context)


async def finish_test(update: Update, context: ContextTypes.DEFAULT_TYPE, already_sent=False):
    key = get_key(update)
    s = state.get(key)
    if not s or s["finished"]:
        return
    s["finished"] = True

    if is_group(update):
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        session = group_sessions.get(chat_id)
        if session and user_id in session["players"]:
            session["players"][user_id]["finished"] = True

        percentage = s["score"] / len(WORDS) * 100
        nickname = s.get("nickname") or update.effective_user.first_name
        result = (
            f"🏆 {nickname.upper()}'NING TEST NATIJASI\n"
            "━━━━━━━━━━━━━━\n\n"
            f"🎯 Natija: {s['score']}/{len(WORDS)}\n"
            f"📊 Foiz: {percentage:.1f}%\n"
            f"🔥 Eng uzun combo: x{s['longest_combo']}\n"
            f"📚 Bosqichlar: {s['rounds']}"
        )
        await update.effective_chat.send_message(result)
        await show_group_leaderboard(update, context)
        return

    percentage = s["score"] / len(WORDS) * 100
    text = "" if already_sent else "🎉 TEST TUGADI!\n\n"
    text += (
        f"🏆 Natija: {s['score']}/{len(WORDS)}\n"
        f"📈 Foiz: {percentage:.1f}%\n"
        f"🔥 Eng uzun combo: x{s['longest_combo']}\n"
        f"📚 Bosqichlar: {s['rounds']}"
    )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Qayta boshlash", callback_data="restart_game")]])
    await update.effective_chat.send_message(text, reply_markup=keyboard)


async def show_group_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_group(update):
        return
    chat_id = update.effective_chat.id
    session = group_sessions.get(chat_id)
    if not session or not session["players"]:
        return

    players = session["players"]
    finished_count = sum(1 for p in players.values() if p["finished"])
    total_count = len(players)
    if finished_count < total_count:
        await update.effective_chat.send_message(
            f"🏁 Siz testni tugatdingiz!\n\n👥 Tugatganlar: {finished_count}/{total_count}\n\n⏳ Qolgan ishtirokchilarni kutamiz..."
        )
        return

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

    results.sort(key=lambda x: (x["score"], x["longest_combo"]), reverse=True)
    text = "🏆 TEST YAKUNI — LEADERBOARD\n━━━━━━━━━━━━━━\n\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, item in enumerate(results, 1):
        medal = medals[i - 1] if i <= 3 else f"{i}."
        text += f"{medal} {item['nickname']} — {item['score']}/{len(WORDS)} | 🔥 x{item['longest_combo']}\n"

    winner = results[0] if results else None
    if winner:
        text += f"\n👑 G‘OLIB: {winner['nickname']}"
    session["all_finished"] = True
    await update.effective_chat.send_message(text)


async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = get_key(update)
    s = state.get(key)
    if not s:
        await update.message.reply_text("📊 Hozircha test boshlanmagan.\n\n/test — testni boshlash")
        return
    done = s["index"]
    percentage = s["score"] / done * 100 if done else 0
    title = f"📊 {s.get('nickname', '').upper()}'NING NATIJASI\n\n" if is_group(update) and s.get("nickname") else "📊 SIZNING NATIJANGIZ\n\n"
    await update.message.reply_text(
        title +
        f"✅ To‘g‘ri: {s['score']}\n"
        f"❓ Javob berilgan: {done}\n"
        f"📈 Foiz: {percentage:.1f}%\n"
        f"🔥 Hozirgi combo: x{s['combo']}\n"
        f"⚡ Eng uzun combo: x{s['longest_combo']}\n"
        f"📚 Bosqichlar: {s['rounds']}"
    )


async def restart_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()
    key = get_key(update)
    state[key] = new_state()
    if is_group(update):
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        session = group_sessions.get(chat_id)
        if session:
            session["players"].pop(user_id, None)
            session["all_finished"] = False
        state[key]["waiting_nickname"] = True
        await update.effective_chat.send_message("🔄 Test qayta boshlandi!\n\n👤 Ismingizni yozing.\n\nMasalan: Otabek yoki Kumush")
        return
    await update.effective_chat.send_message("🔄 Test qayta boshlandi!")
    await ask(update, context)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    if is_group(update):
        key = get_key(update)
        s = state.get(key)
        if s and s["waiting_nickname"]:
            if await register_nickname(update, context):
                return
    await answer(update, context)


def main():
    token = os.environ.get("BOT_TOKEN")
    hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    port = int(os.environ.get("PORT", "10000"))
    if not token:
        raise RuntimeError("BOT_TOKEN topilmadi!")
    if not hostname:
        raise RuntimeError("RENDER_EXTERNAL_HOSTNAME topilmadi!")

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("test", test))
    application.add_handler(CommandHandler("restart", restart))
    application.add_handler(CommandHandler("score", score))
    application.add_handler(CallbackQueryHandler(next_round, pattern="^next_round$"))
    application.add_handler(CallbackQueryHandler(restart_game, pattern="^restart_game$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    webhook_path = "telegram"
    webhook_url = f"https://{hostname}/{webhook_path}"

    # Render jarayon tirik bo‘lsa, har 10 daqiqada o‘zini ping qiladi.
    keep_render_awake(f"https://{hostname}/")

    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=webhook_path,
        webhook_url=webhook_url,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
