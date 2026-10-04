import re
import unicodedata


# =========================================================
# JAVOBNI NORMALIZATSIYA QILISH
# =========================================================

def norm(text):
    if text is None:
        return ""

    text = unicodedata.normalize("NFKC", str(text))

    # Katta-kichik harf farq qilmaydi
    text = text.casefold()

    # O‘zbek apostroflarining barcha ko‘rinishlarini bir xil qilamiz
    apostrophes = "’‘ʻʼ`´ʹ′"
    for ch in apostrophes:
        text = text.replace(ch, "'")

    # Ko‘p uchraydigan belgilarni bir xil ko‘rinishga keltirish
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = text.replace("_", " ")

    # Qavs va tinish belgilarini olib tashlaymiz
    text = re.sub(r"[()[\]{}]", " ", text)
    text = re.sub(r"[,;:!?]+", " ", text)

    # Chiziqcha so‘z oralig‘i sifatida ishlasin
    text = re.sub(r"\s*-\s*", " ", text)

    # Ortiqcha bo‘sh joylar
    text = re.sub(r"\s+", " ", text).strip()

    # Oxiridagi nuqta va boshqa belgilar
    text = text.strip(" .,!?:;-")

    return text


# =========================================================
# JAVOB VARIANTLARINI AJRATISH
# =========================================================

def build_options(expected):
    """
    Masalan:
    'kasb, ish'
    -> kasb
    -> ish

    'ustoz / o‘qituvchi'
    -> ustoz
    -> o‘qituvchi

    'The USA (The US)'
    -> The USA
    -> The US
    -> The USA The US
    """

    expected = str(expected).strip()

    options = {expected}

    # Vergul va / orqali berilgan variantlar
    parts = re.split(r"\s*[,/]\s*", expected)

    for part in parts:
        part = part.strip()
        if part:
            options.add(part)

    # Qavs ichidagi variantlarni ham alohida qabul qilamiz
    matches = re.findall(r"\((.*?)\)", expected)

    for inside in matches:
        inside = inside.strip()

        if inside:
            options.add(inside)

    # Qavssiz ko‘rinish
    without_parentheses = re.sub(r"\s*\(.*?\)", "", expected).strip()

    if without_parentheses:
        options.add(without_parentheses)

    return {
        norm(x)
        for x in options
        if norm(x)
    }


# =========================================================
# MAXSUS QABUL QILINADIGAN VARIANTLAR
# =========================================================
#
# Bu yerda foydalanuvchi tabiiy ravishda aytishi mumkin
# bo‘lgan javoblar beriladi.
#
# DIQQAT:
# Bu WORDS ro‘yxatini o‘zgartirmaydi.
# Faqat javob tekshirishni aqlli qiladi.
# =========================================================

ANSWER_ALIASES = {

    # -------------------------
    # 112-150 YANGI SO‘ZLAR
    # -------------------------

    "about": [
        "haqida"
    ],

    "father": [
        "ota",
        "dada"
    ],

    "mother": [
        "ona",
        "oyi"
    ],

    "parents": [
        "ota ona",
        "ota-ona",
        "ota va ona"
    ],

    "grandfather": [
        "bobo",
        "katta ota"
    ],

    "grandmother": [
        "buvi",
        "katta ona"
    ],

    "son": [
        "o‘g‘il",
        "o'g'il",
        "oʻgʻil",
        "o‘g‘il bola",
        "o'g'il bola",
        "oʻgʻil bola"
    ],

    "daughter": [
        "qiz",
        "qiz farzand",
        "qiz bola"
    ],

    "child": [
        "bola",
        "farzand"
    ],

    "children": [
        "bolalar",
        "farzandlar"
    ],

    "uncle": [
        "amaki",
        "tog‘a",
        "tog'a",
        "togʻa"
    ],

    "aunt": [
        "xola",
        "amma"
    ],

    "cousin(e)": [
        "amakivachcha",
        "xolavachcha",
        "tog‘avachcha",
        "tog'avachcha",

        # Ko‘p uchraydigan yozish xatolari
        "amakivatcha",
        "xolavatcha",
        "togavatcha",

        # Ikkalasini birga yozsa ham
        "amakivachcha xolavachcha",
        "amakivatcha xolavatcha"
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
        "o‘g‘il bola"
    ],

    "niece": [
        "jiyan",
        "jiyan qiz",
        "jiyan qi",
        "jiyan qiz bola",
        "qiz jiyan",
        "qiz bola",
        "qizbola",
        "qizjoyan"
    ],

    "husband": [
        "er",
        "eri",
        "er kishi",
        "turmush o‘rtog‘i",
        "turmush o'rtog'i"
    ],

    "wife": [
        "xotin",
        "hotin",
        "rafiqa",
        "turmush o‘rtog‘i",
        "turmush o'rtog'i"
    ],

    # MUHIM: Deck emas, Desk
    "desk": [
        "parta",
        "maktab partasi"
    ],

    "table": [
        "stol"
    ],

    "chair": [
        "stul",
        "kursi"
    ],

    "key": [
        "kalit"
    ],

    "clock": [
        "soat"
    ],

    "cup": [
        "krujka",
        "piyola"
    ],

    "who": [
        "kim"
    ],

    "whose": [
        "kimning"
    ],

    "what": [
        "nima",
        "qanday"
    ],

    "where": [
        "qayer",
        "qayerda"
    ],

    "when": [
        "qachon"
    ],

    "why": [
        "nega",
        "nima uchun",
        "nimaga"
    ],

    "how": [
        "qanday",
        "qanday qilib"
    ],

    "how often": [
        "qanchalik tez-tez",
        "qanchalik tez tez",
        "necha marta",
        "qancha tez-tez",
        "qancha tez tez"
    ],

    "how many": [
        "nechta",
        "qancha"
    ],

    "how much": [
        "qancha"
    ],

    "how much is this?": [
        "bu qancha turadi",
        "bu necha pul",
        "bu nechi pul",
        "nechi pul bu",
        "qancha turadi"
    ],

    "how much are these?": [
        "bular qancha turadi",
        "bular necha pul",
        "bular nechi pul",
        "nechi pul bular",
        "qancha turadi"
    ],

    "can i pay by card?": [
        "kartadan to‘lasam bo‘ladimi",
        "kartadan to'lasam bo'ladimi",
        "karta bilan to‘lasam bo‘ladimi",
        "karta bilan to'lasam bo'ladimi"
    ],

    "here you are": [
        "mana",
        "marhamat",
        "mana marhamat"
    ],

    "here is your change": [
        "mana qaytimingiz",
        "mana qaytishingiz",
        "qaytimingiz",
        "qaytim"
    ],

    "cash or card?": [
        "naqd pulmi yoki kartami",
        "naqd pulmi yoki karta",
        "naqdmi yoki karta",
        "naqd yoki karta"
    ],


    # -------------------------
    # ESKI SO‘ZLARDAGI MUHIM VARIANTLAR
    # -------------------------

    "work": [
        "ishlamoq",
        "ishlash",
        "ish",
        "mehnat qilmoq",
        "mehnat"
    ],

    "job": [
        "kasb",
        "ish"
    ],

    "read": [
        "o‘qimoq",
        "o'qimoq",
        "oʻqimoq",
        "oqimoq"
    ],

    "help": [
        "yordam",
        "yordam bermoq"
    ],

    "correct": [
        "to‘g‘ri",
        "to'g'ri",
        "toʻgʻri",
        "togri",
        "to‘g‘rilamoq",
        "to'g'rilamoq"
    ],

    "make": [
        "qilmoq",
        "yasamoq",
        "yasash"
    ],

    "some": [
        "ba’zi",
        "ba'zi",
        "baʼzi",
        "bir nechta"
    ],

    "all": [
        "hamma",
        "barcha"
    ],

    "photo": [
        "rasm",
        "surat"
    ],

    "page": [
        "sahifa",
        "bet"
    ],

    "class": [
        "dars",
        "sinf"
    ],

    "nice to meet you": [
        "tanishganimdan xursandman",
        "tanishganimdan hursandman"
    ],

    "conference": [
        "konferensiya"
    ],

    "what’s your phone number?": [
        "telefon raqamingiz qanday",
        "telefon raqamingiz nima",
        "telefon raqamingiz"
    ],

    "what’s your email address?": [
        "elektron pochtangiz qanday",
        "elektron pochta manzilingiz qanday",
        "email manzilingiz qanday",
        "emailingiz qanday"
    ],

    "sorry, can you say that again?": [
        "uzr qaytadan ayta olasizmi",
        "uzr qayta ayta olasizmi",
        "qaytadan ayta olasizmi",
        "qayta ayta olasizmi"
    ],

    "how do you spell (your name)?": [
        "ismingiz qanday harflanadi",
        "ismingizni qanday harflaysiz",
        "ismingizni harflab ayting",
        "qanday harflanadi",
        "what spell"
    ],

    "dot": [
        "nuqta"
    ],

    "hotel": [
        "mehmonxona"
    ],

    "now": [
        "hozir"
    ],

    "today": [
        "bugun"
    ],

    "late": [
        "kech qolmoq",
        "kechikmoq",
        "kech qolish"
    ],

    "match": [
        "tanlamoq",
        "moslashtirmoq",
        "moslashtirish"
    ],

    "complete": [
        "tugatmoq",
        "to‘ldirmoq",
        "to'ldirmoq",
        "toʻldirmoq"
    ],

    "alternative": [
        "tanlov",
        "muqobil variant",
        "muqobil"
    ],

    "tell": [
        "aytmoq",
        "gapirib bermoq"
    ],

    "nice": [
        "yaxshi",
        "yoqimli"
    ],

    "short": [
        "kalta",
        "qisqa"
    ],

    "form": [
        "shakl",
        "forma"
    ],

    "use": [
        "ishlatmoq",
        "foydalanmoq"
    ],

    "here": [
        "bu yerda",
        "shu yerda"
    ],

    "flag": [
        "bayroq"
    ],

    "country": [
        "mamlakat",
        "davlat"
    ],

    "person": [
        "odam",
        "kishi"
    ],

    "people": [
        "odamlar",
        "kishilar"
    ],

    "repeat": [
        "qaytarmoq",
        "takrorlamoq"
    ],

    "conversation": [
        "muloqot",
        "suhbat"
    ],

    "sentence": [
        "gap"
    ],

    "exercise": [
        "mashq"
    ],

    "other": [
        "boshqa"
    ],

    "order": [
        "tartib"
    ],

    "partner": [
        "sherik"
    ],

    "friend": [
        "do‘st",
        "do'st",
        "dost"
    ],
}


# =========================================================
# EXPECTED ENGLISH SO‘ZNI HAM NORMALIZATSIYA QILISH
# =========================================================

def english_key(text):
    return norm(text)


# =========================================================
# BARCHA QABUL QILINADIGAN JAVOBLARNI YIG‘ISH
# =========================================================

def get_all_options(expected):
    options = set()

    # Asosiy WORDS tarjimasi
    options.update(build_options(expected))

    # English so‘zning maxsus aliaslari
    # Bu funksiya is_correct ichida expected English ekanini
    # bilish uchun alohida key orqali ishlatiladi.

    return options


# =========================================================
# ASOSIY TEKSHIRUV
# =========================================================

def is_correct(user_answer, expected, english_word=None):
    """
    Juda yumshoq, lekin nazoratli tekshiruv.

    Qabul qiladi:
    - katta/kichik harf farqini
    - o‘ / o' / oʻ / oʼ farqini
    - g‘ / g' / gʻ farqini
    - ortiqcha bo‘sh joylarni
    - qavslarni
    - vergul/slash variantlarini
    - sinonim va tabiiy javoblarni
    """

    user = norm(user_answer)

    if not user:
        return False

    # 1. Asosiy expected javoblar
    options = build_options(expected)

    # 2. English so‘z bo‘yicha maxsus aliaslar
    if english_word:
        key = english_key(english_word)

        if key in ANSWER_ALIASES:
            for alias in ANSWER_ALIASES[key]:
                options.add(norm(alias))

    # 3. To‘g‘ridan-to‘g‘ri tenglik
    if user in options:
        return True

    return False
