import os
import re
import random
import unicodedata
import threading
import time
import urllib.request

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================================================
# 150 TA SO'Z
# Eski 111 ta + yangi 39 ta
# =========================================================

WORDS = [

    # 1-111
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

    # 112-150
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
    ("Here is your change", "mana, qaytimi"),
    ("Cash or card?", "naqd pulmi, yoki karta?"),
]

assert len(WORDS) == 150, f"WORDS soni 150 emas: {len(WORDS)}"


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
    "Thai": "🇹🇭",
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
    """
    Javoblarni juda yumshoq va aqlli tekshiradi.

    Katta/kichik harf farq qilmaydi.
    Apostrof turlari farq qilmaydi.
    Ortiqcha bo'sh joylar farq qilmaydi.
    Nuqta, !, ? oxirida bo'lsa hisobga olinmaydi.
    """

    if text is None:
        return ""

    text = str(text)

    # Unicode
    text = unicodedata.normalize("NFKC", text)

    # Kichik harf
    text = text.lower()

    # Har xil apostroflarni bir xil qilish
    apostrophes = "’‘ʻʼ`´ʹʾ"
    for ch in apostrophes:
        text = text.replace(ch, "'")

    # Dashlarni oddiy bo'sh joyga yaqinlashtirish
    text = text.replace("–", "-")
    text = text.replace("—", "-")

    # Bir nechta bo'sh joy -> bitta
    text = re.sub(r"\s+", " ", text)

    # Boshi/oxirini tozalash
    text = text.strip()

    # Oxiridagi belgilarni olib tashlash
    text = text.strip(" .!?,")

    return text


# =========================================================
# MAXSUS QABUL QILINADIGAN JAVOBLAR
# =========================================================

EXTRA = {

    # Work
    "work": [
        "ishlamoq",
        "ish",
        "mehnat qilmoq",
        "mehnat",
    ],

    # Help
    "help": [
        "yordam bermoq",
        "yordam",
    ],

    # Father
    "father": [
        "ota",
        "dada",
    ],

    # Mother
    "mother": [
        "ona",
        "oyi",
    ],

    # Wife
    "wife": [
        "xotin",
        "hotin",
        "ayol",
    ],

    # Husband
    "husband": [
        "eri",
        "er",
    ],

    # Nice to meet you
    "nice to meet you": [
        "tanishganimdan xursandman",
        "tanishganimdan hursandman",
    ],

    # Conference
    "conference": [
        "konferensiya",
        "konferensia",
    ],

    # Cousin
    "cousin(e)": [
        "amakivachcha",
        "xolav
