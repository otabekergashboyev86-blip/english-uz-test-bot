import os
import random
import re
import unicodedata

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters


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


state = {}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", str(s)).lower().strip()

    # Turli apostroflarni bir xil ko‘rinishga keltirish
    for ch in ["’", "‘", "ʻ", "ʼ", "`", "´"]:
        s = s.replace(ch, "'")

    # Ketma-ket bo‘sh joylarni bitta qilish
    s = re.sub(r"\s+", " ", s)

    # Oddiy tinish belgilarini oxiridan olib tashlash
    return s.strip(" .!?")


def is_correct(user_answer: str, expected: str) -> bool:
    user = norm(user_answer)
    expected = str(expected).strip()

    options = set()

    # Asl javobning o‘zi
    options.add(norm(expected))

    # Vergul yoki / bilan berilgan variantlar
    # Masalan: "kasb, ish" yoki "ustoz / o‘qituvchi"
    for part in re.split(r"\s*(?:,|/)\s*", expected):
        if part.strip():
            options.add(norm(part))

    # Qavs ichidagi alternativalar
    # Masalan:
    # The USA (The US)
    # The USA
    # The US
    #
    # My family name (surname) is ...
    # My family name is ...
    # My surname is ...
    match = re.search(r"\(([^()]*)\)", expected)

    if match:
        before = expected[:match.start()].strip()
        inside = match.group(1).strip()
        after = expected[match.end():].strip()

        if before or after:
            # Qavsni olib tashlangan variant
            without_parentheses = f"{before} {after}".strip()
            options.add(norm(without_parentheses))

            # Qavs ichidagi variant bilan
            with_inside = f"{before} {inside} {after}".strip()
            options.add(norm(with_inside))

        # Oddiy holatda qavs ichidagi variantni ham qabul qilish
        if inside:
            options.add(norm(inside))

    return user in options


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🇺🇿 English ↔ Uzbek test bot\n\n"
        "/test — testni boshlash\n"
        "/restart — boshidan boshlash\n"
        "/score — natijani ko‘rish"
    )


async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    state[uid] = {"index": 0, "score": 0}
    await ask(update, uid)


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await test(update, context)


async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    s = state.get(uid)

    if not s:
        await update.message.reply_text("Avval /test buyrug‘ini bosing.")
        return

    await update.message.reply_text(
        f"📊 Natija: {s['score']}/{s['index']}"
    )


async def ask(update: Update, uid: int):
    s = state[uid]

    if s["index"] >= len(WORDS):
        await update.message.reply_text(
            f"🎉 Test tugadi!\nNatijangiz: {s['score']}/{len(WORDS)}"
        )
        return

    n = s["index"] + 1
    word, uzbek = WORDS[s["index"]]

    direction = random.choice(["en_to_uz", "uz_to_en"])
    s["direction"] = direction

    if direction == "en_to_uz":
        s["expected"] = uzbek
        await update.message.reply_text(
            f"{n}/111. 🇬🇧 {word}\n"
            "🇺🇿 O‘zbekchasi nima?"
        )
    else:
        s["expected"] = word
        await update.message.reply_text(
            f"{n}/111. 🇺🇿 {uzbek}\n"
            "🇬🇧 Inglizchasi nima?"
        )


async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if uid not in state:
        return

    s = state[uid]
    expected = s.get("expected", "")

    if is_correct(update.message.text, expected):
        s["score"] += 1
        await update.message.reply_text("✅ To‘g‘ri!")
    else:
        await update.message.reply_text(
            f"❌ Noto‘g‘ri. To‘g‘ri javob: {expected}"
        )

    s["index"] += 1
    await ask(update, uid)


def main():
    token = os.environ.get("BOT_TOKEN")

    if not token:
        raise RuntimeError("BOT_TOKEN environment variable is missing")

    hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")

    if not hostname:
        raise RuntimeError("RENDER_EXTERNAL_HOSTNAME is missing")

    port = int(os.environ.get("PORT", "10000"))

    webhook_path = "telegram"
    webhook_url = f"https://{hostname}/{webhook_path}"

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test", test))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(CommandHandler("score", score))

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, answer)
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
