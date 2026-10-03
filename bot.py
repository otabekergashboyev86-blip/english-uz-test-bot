import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

WORDS = "[('Argentina', 'argentina'), ('Brazil', 'Braziliya'), ('Canada', 'Kanada'), ('Italy', 'Italiya'), ('Japan', 'Yaponiya'), ('Mexico', 'Meksika'), ('Poland', 'Polsha'), ('Spain', 'Ispaniya'), ('Thailand', 'Tailand'), ('Great Britain', 'Buyuk Britaniya'), ('The UK', 'Qo‘shma qirolliklar (Buyuk Britaniya)'), ('The USA (The US)', 'Amerika Qo‘shma Shtatlari'), ('Turkey', 'Turkiya'), ('Flag', 'bayroq'), ('Country', 'mamlakat'), ('Match', 'tanlamoq'), ('Look', 'qaramoq'), ('Listen', 'tinglamoq'), ('Work', 'ishlamoq'), ('Person', 'odam'), ('People', 'odamlar'), ('Box', 'quti'), ('Check', 'tekshirmoq'), ('Repeat', 'qaytarmoq'), ('Conversation', 'muloqot'), ('Read', 'o‘qimoq'), ('Sentence', 'gap'), ('Help', 'yordam bermoq'), ('Exercise', 'mashq'), ('With', 'bilan'), ('Complete', 'tugatmoq'), ('Other', 'boshqa'), ('Map', 'xarita'), ('Underline', 'tagiga chizmoq'), ('Job', 'kasb, ish'), ('Short', 'kalta'), ('Form', 'shakl'), ('Question', 'savol'), ('Answer', 'javob'), ('Page', 'sahifa, bet'), ('Again', 'qaytadan'), ('Correct', 'to‘g‘ri, to‘g‘rilamoq'), ('Example', 'misol'), ('Alternative', 'tanlov'), ('Tell', 'gapirib bermoq'), ('Pronunciation', 'talaffuz'), ('Nationality', 'millat'), ('The same', 'bir xil'), ('Famous', 'mashhur'), ('Some', 'ba’zi, bir nechta'), ('True', 'to‘g‘ri'), ('False', 'noto‘g‘ri'), ('Word', 'so‘z'), ('Make', 'qilmoq, yasamoq'), ('All', 'hamma, barcha'), ('Photo', 'rasm, surat'), ('Order', 'tartib'), ('Useful phrases', 'foydali iboralar'), ('Use', 'ishlatmoq'), ('Partner', 'sherik'), ('Nice to meet you', 'Tanishganimdan xursandman'), ('Here', 'bu yerda'), ('Conference', 'konferensiya'), ('What’s your name?', 'Ismingiz nima?'), ('My name is ...', 'Mening ismim ...'), ('What’s your family name (surname)', 'Familiyangiz nima?'), ('My family name (surname) is ...', 'Mening familiyam ...'), ('Where are you from?', 'Qayerdansiz?'), ('I’m from ...', 'Men ...daman'), ('Football player', 'futbolchi'), ('Doctor', 'shifokor'), ('School teacher', 'ustoz / o‘qituvchi'), ('Pilot', 'uchuvchi'), ('Farmer', 'fermer'), ('Nurse', 'hamshira'), ('Taxi driver', 'taksist'), ('Office worker', 'ofis xodimi'), ('Hospital', 'shifoxona'), ('Small', 'kichkina'), ('Good', 'yaxshi'), ('Team', 'jamoa'), ('Manager', 'menejer'), ('Nice', 'yaxshi'), ('Thai', 'tailandlik'), ('British', 'Britaniyalik'), ('Polish', 'polshalik'), ('Spanish', 'ispaniyalik'), ('Turkish', 'turkiyalik'), ('Mexican', 'meksikalik'), ('Japanese', 'yaponiyalik'), ('Italian', 'italiyalik'), ('American', 'amerikalik'), ('Canadian', 'kanadalik'), ('Brazilian', 'braziliyalik'), ('Argentinian', 'argentinalik'), ('University', 'universitet'), ('Friend', 'do‘st'), ('All over the world', 'dunyo bo‘ylab'), ('And', 'va'), ('But', 'lekin'), ('Now', 'hozir'), ('Hotel', 'mehmonxona'), ('What’s your phone number?', 'telefon raqamingiz qanday?'), ('What’s your email address?', 'elektron pochtangiz qanday?'), ('Sorry, can you say that again?', 'Uzr, qaytadan ayta olasizmi?'), ('How do you spell (your name)?', 'Harflab qanday aytiladi?'), ('@', 'at'), ('Dot', 'nuqta'), ('Class', 'dars, sinf'), ('Late', 'kech qolmoq'), ('Today', 'bugun')]"

# Per-user progress: user_id -> {"index": 0, "score": 0}
state = {}

def norm(s: str) -> str:
    return " ".join(s.lower().strip().replace("’", "'").split())

def is_correct(user_answer: str, expected: str) -> bool:
    a = norm(user_answer)
    # Allow common equivalent answers separated by "/".
    options = [norm(x) for x in expected.replace(" / ", "/").split("/")]
    return a in options

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🇺🇿 English → Uzbek test bot\n\n"
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
            f"🎉 Test tugadi!
Natijangiz: {s['score']}/{len(WORDS)}"
        )
        return

    n = s["index"] + 1
    word, uzbek = WORDS[s["index"]]

    # Har bir savolda yo‘nalish aralashadi:
    # inglizcha -> o‘zbekcha yoki o‘zbekcha -> inglizcha.
    import random
    direction = random.choice(["en_to_uz", "uz_to_en"])
    s["direction"] = direction

    if direction == "en_to_uz":
        s["expected"] = uzbek
        await update.message.reply_text(
            f"{n}/111. 🇬🇧 {word}
🇺🇿 O‘zbekchasi nima?"
        )
    else:
        s["expected"] = word
        await update.message.reply_text(
            f"{n}/111. 🇺🇿 {uzbek}
🇬🇧 Inglizchasi nima?"
        )

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in state:
        return

    s = state[uid]
    if s["index"] >= len(WORDS):
        return

    word, uzbek = WORDS[s["index"]]
    expected = s.get("expected", uzbek)

    if is_correct(update.message.text, expected):
        s["score"] += 1
        reply = f"✅ To‘g‘ri! {s['score']}/{s['index'] + 1}"
    else:
        reply = (
            f"❌ Noto‘g‘ri.
"
            f"To‘g‘ri javob: {expected}
"
            f"Natija: {s['score']}/{s['index'] + 1}"
        )

    s["index"] += 1
    await update.message.reply_text(reply)

    if s["index"] < len(WORDS):
        await ask(update, uid)
    else:
        await update.message.reply_text(
            f"🏆 Test tugadi! Yakuniy natija: {s['score']}/{len(WORDS)}"
        )

def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN environment variable topilmadi.")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test", test))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(CommandHandler("score", score))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))
    print("Bot ishga tushdi.")
    app.run_polling()

if __name__ == "__main__":
    main()
