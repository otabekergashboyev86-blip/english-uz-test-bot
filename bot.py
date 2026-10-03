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


ROUND_SIZE = 10

state = {}
group_players = {}


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


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", str(s)).lower().strip()

    for ch in ["’", "‘", "ʻ", "ʼ", "`", "´"]:
        s = s.replace(ch, "'")

    s = re.sub(r"\s+", " ", s)

    return s.strip(" .!?")


def is_correct(user_answer: str, expected: str) -> bool:
    user = norm(user_answer)
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
            without_parentheses = f"{before} {after}".strip()
            options.add(norm(without_parentheses))

            with_inside = f"{before} {inside} {after}".strip()
            options.add(norm(with_inside))

        if inside:
            options.add(norm(inside))

    return user in options


def new_state():
    return {
        "index": 0,
        "score": 0,
        "combo": 0,
        "longest_combo": 0,
        "round_score": 0,
        "wrong": [],
        "rounds": 0,
        "expected": None,
        "direction": None,
        "waiting_next_round": False,
        "nickname": None,
        "waiting_nickname": False,
        "finished": False,
    }


def is_group(update: Update) -> bool:
    return update.effective_chat.type in ["group", "supergroup"]


def get_key(update: Update):
    return (
        update.effective_chat.id,
        update.effective_user.id,
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_group(update):
        await update.message.reply_text(
            "👥 Guruh testi botiga xush kelibsiz!\n\n"
            "📝 Testni boshlash uchun /test bosing.\n"
            "Har bir ishtirokchi o‘z niknameini kiritadi."
        )
    else:
        await update.message.reply_text(
            "🇬🇧 English → Uzbek test botiga xush kelibsiz!\n\n"
            "/test — testni boshlash\n"
            "/restart — testni boshidan boshlash\n"
            "/score — natijangiz"
        )


async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = get_key(update)

    state[key] = new_state()

    if is_group(update):
        state[key]["waiting_nickname"] = True

        await update.message.reply_text(
            "👤 Ishtirok etish uchun niknameingizni yozing.\n\n"
            "Masalan: @Ali yoki Ali"
        )

        return

    await update.message.reply_text(
        f"🚀 Test boshlandi!\n\n"
        f"📚 Jami: {len(WORDS)} ta so‘z\n"
        f"📝 Har raund: {ROUND_SIZE} ta savol"
    )

    await ask(update, context)


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = get_key(update)

    state[key] = new_state()

    if is_group(update):
        state[key]["waiting_nickname"] = True

        await update.message.reply_text(
            "🔄 Test qaytadan boshlandi.\n\n"
            "👤 Niknameingizni yozing:"
        )

        return

    await update.message.reply_text(
        "🔄 Test boshidan boshlandi!"
    )

    await ask(update, context)


async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = get_key(update)

    if key not in state:
        await update.message.reply_text(
            "Hali test boshlamagansiz.\n\n"
            "/test ni bosing."
        )
        return

    s = state[key]

    percentage = (s["score"] / len(WORDS)) * 100

    nickname = s["nickname"]

    name_text = f"👤 {nickname}\n" if nickname else ""

    await update.message.reply_text(
        f"📊 Natijangiz:\n\n"
        f"{name_text}"
        f"✅ Ball: {s['score']}/{len(WORDS)}\n"
        f"📈 Foiz: {percentage:.1f}%\n"
        f"🔥 Eng uzun combo: x{s['longest_combo']}\n"
        f"📚 Raundlar: {s['rounds']}"
    )


async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = get_key(update)

    if key not in state:
        return

    s = state[key]

    index = s["index"]

    if index >= len(WORDS):
        await finish_test(update, context)
        return

    word, uzbek = WORDS[index]

    direction = random.choice(["en_uz", "uz_en"])

    s["direction"] = direction

    if direction == "en_uz":
        s["expected"] = uzbek

        flag = FLAGS.get(word, "")
        word_text = f"{flag} {word}" if flag else word

        question = (
            f"❓ {index + 1}/{len(WORDS)}\n\n"
            f"🇬🇧 {word_text}\n\n"
            f"🇺🇿 O‘zbekchasini yozing:"
        )

    else:
        s["expected"] = word

        question = (
            f"❓ {index + 1}/{len(WORDS)}\n\n"
            f"🇺🇿 {uzbek}\n\n"
            f"🇬🇧 Inglizchasini yozing:"
        )

    await update.effective_message.reply_text(question)


async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = get_key(update)

    if key not in state:
        return

    s = state[key]

    # Guruhda avval nikname kiritish
    if is_group(update) and s["waiting_nickname"]:

        nickname = update.message.text.strip()

        if not nickname:
            return

        s["nickname"] = nickname
        s["waiting_nickname"] = False

        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        if chat_id not in group_players:
            group_players[chat_id] = {}

        group_players[chat_id][user_id] = {
            "nickname": nickname,
            "score": 0,
            "longest_combo": 0,
            "finished": False,
        }

        # Nikname xabarini ham o‘chiramiz
        try:
            await update.message.delete()
        except Exception:
            pass

        await update.effective_chat.send_message(
            f"✅ {nickname} ro‘yxatdan o‘tdi!\n\n"
            f"🚀 Test boshlandi!"
        )

        await ask(update, context)

        return

    if s["waiting_next_round"]:
        try:
            await update.message.delete()
        except Exception:
            pass

        await update.effective_chat.send_message(
            "👇 Avval «Keyingi 10 ta» tugmasini bosing."
        )

        return

    if s["finished"]:
        try:
            await update.message.delete()
        except Exception:
            pass

        return

    user_answer = update.message.text
    expected = s["expected"]

    index = s["index"]

    if index >= len(WORDS):
        return

    word, uzbek = WORDS[index]

    correct = is_correct(user_answer, expected)

    # Eng muhim qism:
    # foydalanuvchi yozgan javobni darhol o‘chiramiz
    if is_group(update):
        try:
            await update.message.delete()
        except Exception:
            pass

    if correct:

        s["score"] += 1
        s["round_score"] += 1
        s["combo"] += 1

        if s["combo"] > s["longest_combo"]:
            s["longest_combo"] = s["combo"]

        result_text = "✅ To‘g‘ri!"

        if s["combo"] == 3:
            result_text += "\n🔥 COMBO x3!"

        elif s["combo"] == 5:
            result_text += "\n⚡ COMBO x5 — zo‘r!"

        elif s["combo"] > 5 and s["combo"] % 5 == 0:
            result_text += f"\n🔥 COMBO x{s['combo']}!"

    else:

        s["combo"] = 0

        s["wrong"].append(
            {
                "word": word,
                "uzbek": uzbek,
                "user_answer": user_answer,
                "expected": expected,
            }
        )

        result_text = (
            f"❌ Noto‘g‘ri.\n"
            f"✅ To‘g‘ri javob: {expected}"
        )

    # Guruhdagi umumiy o‘yinchi ma'lumotini yangilash
    if is_group(update):
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        if chat_id in group_players:
            group_players[chat_id][user_id]["score"] = s["score"]
            group_players[chat_id][user_id]["longest_combo"] = (
                s["longest_combo"]
            )

    if is_group(update):
        await update.effective_chat.send_message(result_text)
    else:
        await update.message.reply_text(result_text)

    s["index"] += 1

    if s["index"] >= len(WORDS):
        await finish_test(update, context)
        return

    if s["index"] % ROUND_SIZE == 0:
        await round_result(update, context)
        return

    await ask(update, context)


async def round_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = get_key(update)

    s = state[key]

    s["rounds"] += 1
    s["waiting_next_round"] = True

    round_number = s["rounds"]

    text = (
        f"🏁 {round_number}-raund tugadi!\n\n"
        f"📊 Natija: {s['round_score']}/{ROUND_SIZE}\n"
        f"🏆 Umumiy: {s['score']}/{len(WORDS)}\n"
    )

    if s["wrong"]:
        text += "\n❌ Xato qilingan so‘zlar:\n"

        for item in s["wrong"]:
            text += (
                f"• {item['word']} — {item['uzbek']}\n"
            )
    else:
        text += "\n🎉 Bu raundda xato yo‘q!"

    keyboard = [
        [
            InlineKeyboardButton(
                "➡️ Keyingi 10 ta",
                callback_data="next_round"
            )
        ]
    ]

    markup = InlineKeyboardMarkup(keyboard)

    await update.effective_message.reply_text(
        text,
        reply_markup=markup
    )


async def next_round(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()

    chat_id = query.message.chat_id
    user_id = query.from_user.id

    key = (chat_id, user_id)

    if key not in state:
        await query.message.reply_text(
            "Test topilmadi. /test ni bosing."
        )
        return

    s = state[key]

    if not s["waiting_next_round"]:
        return

    s["waiting_next_round"] = False
    s["round_score"] = 0
    s["wrong"] = []

    await query.message.reply_text(
        "🚀 Keyingi 10 ta savol boshlandi!"
    )

    await ask(update, context)


async def restart_game(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query

    await query.answer()

    chat_id = query.message.chat_id
    user_id = query.from_user.id

    key = (chat_id, user_id)

    old_nickname = None

    if key in state:
        old_nickname = state[key].get("nickname")

    state[key] = new_state()

    # Guruhda nikname saqlanadi
    if is_group(update) and old_nickname:
        state[key]["nickname"] = old_nickname

        if chat_id in group_players and user_id in group_players[chat_id]:
            group_players[chat_id][user_id]["score"] = 0
            group_players[chat_id][user_id]["longest_combo"] = 0
            group_players[chat_id][user_id]["finished"] = False

        await query.message.reply_text(
            f"🔄 {old_nickname}, test qaytadan boshlandi!"
        )

        await ask(update, context)

    else:
        await query.message.reply_text(
            "🔄 Test qaytadan boshlandi!"
        )

        await ask(update, context)


async def finish_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = get_key(update)

    s = state[key]

    s["finished"] = True

    total = len(WORDS)
    score_value = s["score"]
    percentage = (score_value / total) * 100

    nickname = s["nickname"]

    # Guruh o‘yinchisini yakunlangan deb belgilash
    if is_group(update):
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        if chat_id not in group_players:
            group_players[chat_id] = {}

        if user_id not in group_players[chat_id]:
            group_players[chat_id][user_id] = {
                "nickname": nickname or str(user_id),
                "score": score_value,
                "longest_combo": s["longest_combo"],
                "finished": True,
            }

        group_players[chat_id][user_id]["score"] = score_value
        group_players[chat_id][user_id]["longest_combo"] = (
            s["longest_combo"]
        )
        group_players[chat_id][user_id]["finished"] = True

        text = (
            f"🎉 {nickname} TESTNI YAKUNLADI!\n\n"
            f"🏆 Natija: {score_value}/{total}\n"
            f"📈 Foiz: {percentage:.1f}%\n"
            f"🔥 Eng uzun combo: x{s['longest_combo']}"
        )

        await update.effective_chat.send_message(text)

        await show_group_leaderboard(
            update,
            context,
            chat_id
        )

        return

    # Shaxsiy chatdagi yakuniy natija
    text = (
        "🎉 TEST YAKUNLANDI!\n\n"
        f"🏆 Umumiy natija: {score_value}/{total}\n"
        f"📈 Foiz: {percentage:.1f}%\n"
        f"🔥 Eng uzun combo: x{s['longest_combo']}\n"
        f"📚 Raundlar: {s['rounds']}\n\n"
    )

    if score_value == total:
        text += "💯 Mukammal natija! 🔥"

    elif percentage >= 90:
        text += "🌟 Juda yaxshi natija!"

    elif percentage >= 70:
        text += "👏 Yaxshi natija!"

    elif percentage >= 50:
        text += "💪 Yana mashq qiling!"

    else:
        text += "📚 So‘zlarni yana bir bor takrorlang!"

    keyboard = [
        [
            InlineKeyboardButton(
                "🔄 Qaytadan boshlash",
                callback_data="restart_game"
            )
        ]
    ]

    await update.effective_message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_group_leaderboard(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int
):
    if chat_id not in group_players:
        return

    players = group_players[chat_id]

    if not players:
        return

    # Hamma qatnashchilar testni tugatganmi?
    if not all(
        player["finished"]
        for player in players.values()
    ):
        finished_count = sum(
            1
            for player in players.values()
            if player["finished"]
        )

        total_players = len(players)

        await update.effective_chat.send_message(
            f"⏳ Hozircha {finished_count}/{total_players} "
            f"ishtirokchi testni tugatdi."
        )

        return

    # Ball bo‘yicha saralash.
    # Ball teng bo‘lsa, eng uzun combo yuqoriga chiqadi.
    ranking = sorted(
        players.values(),
        key=lambda x: (
            x["score"],
            x["longest_combo"]
        ),
        reverse=True
    )

    text = "🏆 TEST YAKUNIY NATIJALARI!\n\n"

    medals = ["🥇", "🥈", "🥉"]

    for i, player in enumerate(ranking):

        if i < 3:
            medal = medals[i]
        else:
            medal = f"{i + 1}."

        percentage = (
            player["score"] / len(WORDS)
        ) * 100

        text += (
            f"{medal} {player['nickname']}\n"
            f"   📊 {player['score']}/{len(WORDS)} "
            f"({percentage:.1f}%)\n"
            f"   🔥 Combo: x{player['longest_combo']}\n\n"
        )

    winner = ranking[0]

    text += (
        "🎉🎉🎉 G‘OLIB 🎉🎉🎉\n\n"
        f"🏆 {winner['nickname']}\n"
        f"📊 {winner['score']}/{len(WORDS)}\n"
        f"🔥 Eng uzun combo: x{winner['longest_combo']}\n\n"
        "👏 Barcha ishtirokchilarga rahmat!"
    )

    await update.effective_chat.send_message(text)


def main():
    token = os.environ["BOT_TOKEN"]

    hostname = os.environ["RENDER_EXTERNAL_HOSTNAME"]
    port = int(os.environ.get("PORT", 10000))

    webhook_path = "telegram"

    webhook_url = f"https://{hostname}/{webhook_path}"

    app = Application.builder().token(token).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("test", test)
    )

    app.add_handler(
        CommandHandler("restart", restart)
    )

    app.add_handler(
        CommandHandler("score", score)
    )

    app.add_handler(
        CallbackQueryHandler(
            next_round,
            pattern="^next_round$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            restart_game,
            pattern="^restart_game$"
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            answer
        )
    )

    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=webhook_path,
        webhook_url=webhook_url,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
