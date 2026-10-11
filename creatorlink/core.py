"""CreatorLink core logic: sample data, matching, sample concepts, agreements.

Pure Python (standard library only). No internet or API keys needed, so the
demo cannot fail because of Wi-Fi.
"""
import json
import os
import re
import time
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
EXTRA_FILE = os.path.join(HERE, "creators_extra.json")

LANGUAGES = ["English", "Hindi", "Tamil", "Telugu", "Marathi"]
NICHES = ["food", "fashion", "beauty", "tech", "education",
          "fitness", "finance", "handmade", "home", "travel"]

# ---------------------------------------------------------------- sample data
SEED_CREATORS = [
    dict(id="c01", name="Ananya Rao", city="Hyderabad",
         languages=["Telugu", "English", "Hindi"], niches=["food", "handmade"],
         tools=["Midjourney", "Runway"], style="warm nostalgic festive homely",
         bio="Turns home-kitchen brands into festive, story-led visuals.",
         price_min=3000, price_max=8000, delivery_days=4,
         formats=["15-sec Reel", "Festival poster set"],
         licence="Full commercial use, 12 months, social + print"),
    dict(id="c02", name="Karthik Subramanian", city="Chennai",
         languages=["Tamil", "English"], niches=["tech", "education"],
         tools=["ChatGPT", "Canva AI", "ElevenLabs"],
         style="clear friendly explainer simple",
         bio="Explainer videos that make apps and courses easy to understand.",
         price_min=4000, price_max=10000, delivery_days=5,
         formats=["45-sec explainer", "Carousel post"],
         licence="Full commercial use, 12 months, all digital"),
    dict(id="c03", name="Meera Joshi", city="Pune",
         languages=["Marathi", "Hindi", "English"], niches=["fashion", "beauty"],
         tools=["Midjourney", "Adobe Firefly"], style="elegant editorial premium",
         bio="Editorial-style lookbooks and campaign visuals for small labels.",
         price_min=6000, price_max=15000, delivery_days=6,
         formats=["Lookbook (8 images)", "Story ad"],
         licence="Commercial use, social media only, 6 months"),
    dict(id="c04", name="Rohit Verma", city="Delhi",
         languages=["Hindi", "English"], niches=["fitness", "finance"],
         tools=["Runway", "ElevenLabs"], style="high-energy punchy motivational",
         bio="Fast, punchy short videos for gyms, apps and money tips.",
         price_min=3500, price_max=9000, delivery_days=3,
         formats=["20-sec Reel", "Voiceover ad"],
         licence="Full commercial use, 12 months, all digital"),
    dict(id="c05", name="Sneha Kulkarni", city="Bengaluru",
         languages=["English", "Hindi"], niches=["home", "handmade"],
         tools=["Adobe Firefly", "Canva AI"], style="minimal cozy aesthetic calm",
         bio="Cozy, minimal product scenes for decor and handmade brands.",
         price_min=2500, price_max=7000, delivery_days=4,
         formats=["Product scene set", "Instagram carousel"],
         licence="Full buyout, perpetual, all media"),
    dict(id="c06", name="Imran Sheikh", city="Mumbai",
         languages=["Hindi", "English"], niches=["travel", "food"],
         tools=["Runway", "Midjourney"], style="vibrant street energetic fun",
         bio="Vibrant street-food and travel stories in short video form.",
         price_min=4000, price_max=11000, delivery_days=5,
         formats=["30-sec Reel", "Story series"],
         licence="Commercial use, social media only, 12 months"),
    dict(id="c07", name="Lakshmi Narayanan", city="Coimbatore",
         languages=["Tamil", "English"], niches=["handmade", "home"],
         tools=["Midjourney"], style="traditional colourful festive rooted",
         bio="Traditional, colourful visuals for sarees, crafts and decor.",
         price_min=2000, price_max=6000, delivery_days=4,
         formats=["Festival poster set", "Product story"],
         licence="Full commercial use, 12 months, social + print"),
    dict(id="c08", name="Vamsi Krishna", city="Vijayawada",
         languages=["Telugu", "English"], niches=["tech", "finance"],
         tools=["ChatGPT", "ElevenLabs"], style="straight-talking simple trustworthy",
         bio="Simple Telugu explainers for apps, loans and savings.",
         price_min=3000, price_max=8000, delivery_days=4,
         formats=["40-sec explainer", "Voiceover ad"],
         licence="Full commercial use, 6 months, all digital"),
    dict(id="c09", name="Pooja Nair", city="Kochi",
         languages=["English", "Hindi"], niches=["beauty", "fashion", "travel"],
         tools=["Adobe Firefly", "Runway"], style="dreamy pastel soft glow",
         bio="Soft pastel visuals for skincare, resorts and boutique labels.",
         price_min=5000, price_max=12000, delivery_days=5,
         formats=["20-sec Reel", "Campaign poster"],
         licence="Commercial use, social media only, 6 months"),
    dict(id="c10", name="Arjun Mehta", city="Ahmedabad",
         languages=["Hindi", "English"], niches=["education", "finance"],
         tools=["Canva AI", "ChatGPT"], style="storytelling relatable friendly",
         bio="Relatable story-style content for coaching and money brands.",
         price_min=3000, price_max=7500, delivery_days=4,
         formats=["Story-style Reel", "Carousel post"],
         licence="Full commercial use, 12 months, all digital"),
]

# One simple tagline per language. Please have a native speaker check these
# before showing them to judges.
HOOKS = {
    "English": "{p}: now in every home",
    "Hindi": "{p}: अब हर घर की पसंद",
    "Tamil": "{p}: இனி ஒவ்வொரு வீட்டிலும்",
    "Telugu": "{p}: ఇప్పుడు ప్రతి ఇంట్లో",
    "Marathi": "{p}: आता प्रत्येक घरात",
}

STOPWORDS = set("""a an and the for of to in on with at by from is are be this that it
our we you your my their as or but not no yes can will want need new make get""".split())


# ------------------------------------------------------------------ storage
def load_creators():
    """Seed creators plus any creators added through the web form."""
    creators = [dict(c) for c in SEED_CREATORS]
    try:
        with open(EXTRA_FILE, encoding="utf-8") as f:
            creators += json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return creators


def save_creator(creator):
    try:
        with open(EXTRA_FILE, encoding="utf-8") as f:
            extra = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        extra = []
    extra.append(creator)
    with open(EXTRA_FILE, "w", encoding="utf-8") as f:
        json.dump(extra, f, ensure_ascii=False, indent=2)


def get_creator(creator_id):
    for c in load_creators():
        if c["id"] == creator_id:
            return c
    return None


def new_creator_from_form(form):
    """Build a creator dict from submitted form fields (all strings)."""
    name = form.get("name", "").strip()
    if not name:
        raise ValueError("Please enter a name.")
    langs = [l for l in form.getlist("languages") if l in LANGUAGES] or ["English"]
    niches = [n for n in form.getlist("niches") if n in NICHES]
    if not niches:
        raise ValueError("Pick at least one niche.")
    pmin = to_int(form.get("price_min"), 3000)
    pmax = max(to_int(form.get("price_max"), 8000), pmin)
    tools = [t.strip() for t in form.get("tools", "").split(",") if t.strip()] or ["Not stated"]
    creator_id = "u%d" % (int(time.time() * 1000) % 10**9)
    return dict(
        id=creator_id, name=name[:60], city=form.get("city", "").strip()[:40] or "India",
        languages=langs, niches=niches, tools=tools[:6],
        style=form.get("style", "").strip()[:80],
        bio=form.get("bio", "").strip()[:200] or "New AI creator on CreatorLink.",
        price_min=pmin, price_max=pmax, delivery_days=to_int(form.get("delivery_days"), 5),
        formats=["Custom"], licence=form.get("licence", "").strip()[:80]
        or "Full commercial use, 12 months, all digital",
    )


# ----------------------------------------------------------------- matching
def to_int(value, default):
    try:
        return int(float(str(value).replace(",", "").replace("₹", "").strip()))
    except (TypeError, ValueError):
        return default


def tokens(text):
    words = re.findall(r"[a-zA-Z]+", (text or "").lower())
    return {w for w in words if len(w) > 2 and w not in STOPWORDS}


def score_creator(brief, creator):
    """Return (score 0-100, list of human-readable reasons)."""
    reasons = []

    # 1. language (35%)
    lang = brief["language"]
    if lang in creator["languages"]:
        lang_s = 1.0
        reasons.append("Creates in %s" % lang)
    elif "English" in creator["languages"]:
        lang_s = 0.2
        reasons.append("No %s, but works in English" % lang)
    else:
        lang_s = 0.0

    # 2. niche (30%)
    if brief["niche"] in creator["niches"]:
        niche_s = 1.0
        reasons.append("Specialises in %s brands" % brief["niche"])
    else:
        niche_s = 0.0

    # 3. keyword overlap with style/bio/niches (15%)
    brief_words = tokens(" ".join([brief["product"], brief["audience"], brief["tone"]]))
    creator_words = tokens(" ".join([creator["style"], creator["bio"],
                                     " ".join(creator["niches"])]))
    common = sorted(brief_words & creator_words)
    kw_s = min(1.0, len(common) / 3.0)
    if common:
        reasons.append("Style fits: " + ", ".join(common[:3]))

    # 4. budget (20%)
    budget = brief["budget"]
    pmin, pmax = creator["price_min"], creator["price_max"]
    if pmin <= budget <= pmax:
        budget_s = 1.0
        reasons.append("Budget fits (Rs %s-%s)" % (format(pmin, ","), format(pmax, ",")))
    elif budget > pmax:
        budget_s = 0.9
        reasons.append("Within budget (from Rs %s)" % format(pmin, ","))
    else:
        ratio = budget / pmin if pmin else 0
        budget_s = max(0.0, (ratio - 0.5) / 0.5)
        if budget_s > 0:
            reasons.append("Slightly below usual rate (Rs %s+)" % format(pmin, ","))

    score = 100 * (0.35 * lang_s + 0.30 * niche_s + 0.15 * kw_s + 0.20 * budget_s)
    return round(score), reasons


def match(brief, top_n=3):
    """Rank all creators for a brief. Returns (results, elapsed_ms)."""
    start = time.perf_counter()
    scored = []
    for c in load_creators():
        score, reasons = score_creator(brief, c)
        scored.append(dict(creator=c, score=score, reasons=reasons,
                           concept=sample_concept(brief, c)))
    scored.sort(key=lambda r: (-r["score"], r["creator"]["price_min"]))
    return scored[:top_n], round((time.perf_counter() - start) * 1000, 1)


def clean_brief(form):
    """Turn raw form data into a validated brief dict."""
    brand = form.get("brand", "").strip()[:60] or "Your brand"
    product = form.get("product", "").strip()[:80] or "your product"
    lang = form.get("language", "English")
    niche = form.get("niche", "food")
    return dict(
        brand=brand, product=product,
        audience=form.get("audience", "").strip()[:100] or "local customers",
        language=lang if lang in LANGUAGES else "English",
        niche=niche if niche in NICHES else "food",
        budget=max(500, to_int(form.get("budget"), 5000)),
        tone=form.get("tone", "").strip()[:100],
    )


# ------------------------------------------- "try before you hire" concepts
def sample_concept(brief, creator):
    """A quick sample concept in the creator's own style (template based)."""
    fmt = creator["formats"][0]
    lang = brief["language"] if brief["language"] in creator["languages"] else (
        "English" if "English" in creator["languages"] else creator["languages"][0])
    style_words = creator["style"].split()
    look = ", ".join(style_words[:3]) if style_words else "clean"
    hook = HOOKS.get(lang, HOOKS["English"]).format(p=brief["product"])
    return dict(
        format=fmt, language=lang, hook=hook,
        beats=[
            "Open: close-up of %s in a %s setting" % (brief["product"], look),
            "Middle: show how it helps %s" % brief["audience"],
            "Close: %s logo + 'Order today' call to action" % brief["brand"],
        ],
        tools=", ".join(creator["tools"]),
    )


# ------------------------------------------------------------- agreement
def agreement_text(brief, creator):
    concept = sample_concept(brief, creator)
    return "\n".join([
        "CONTENT USAGE AGREEMENT (TEMPLATE)",
        "Date: %s" % date.today().strftime("%d %B %Y"),
        "",
        "Between: %s (Brand) and %s (Creator, %s)" % (brief["brand"], creator["name"], creator["city"]),
        "",
        "1. Work: %s for %s, in %s." % (concept["format"], brief["product"], concept["language"]),
        "2. Fee: Rs %s, paid 50%% upfront and 50%% on delivery." % format(brief["budget"], ","),
        "3. Delivery: within %d days of the brief being confirmed, with 2 rounds of changes." % creator["delivery_days"],
        "4. AI disclosure: the Creator used %s to produce this work and will say so if asked." % ", ".join(creator["tools"]),
        "5. Usage rights: %s." % creator["licence"],
        "6. Originality: the Creator confirms they hold the rights to publish what they deliver "
        "and will not copy another person's work, logo or characters.",
        "",
        "This is a simple template for a hackathon demo, not legal advice.",
    ])
