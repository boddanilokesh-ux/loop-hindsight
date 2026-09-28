"""Synthetic demo data for a fictional brand: Brew & Bloom (specialty cafe, Hyderabad).

All names and numbers are invented. The history contains deliberate patterns
(Friday-evening reels win, discount posts flop, questions in captions boost
comments, hashtag stuffing hurts reach) so you can watch the agent learn them.
"""
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))

DEMO_BRAND = {
    "name": "Brew & Bloom",
    "niche": "a specialty coffee cafe and small-batch roastery in Jubilee Hills, Hyderabad",
    "audience": "college students and young professionals aged 20-35 who love filter coffee and weekend cafe hangouts",
    "platforms": "Instagram (main), LinkedIn (hiring and sourcing stories)",
    "tone": "friendly, a little cheeky, sounds like a barista and not a brochure; English with light Telugu is welcome",
    "rules": "Never use more than 4 hashtags. Never mention competitors. The cafe is closed on Mondays. Do not write corporate-sounding captions.",
}


def profile_sentence(b: dict) -> str:
    return (
        f"Brand profile: {b['name']} is {b['niche']}. "
        f"Audience: {b['audience']}. Platforms: {b['platforms']}. "
        f"Preferred tone: {b['tone']}. Owner's rules: {b['rules']}"
    )


# (date, time, platform, format, topic, caption style, reach, likes, comments, shares)
_POSTS = [
    ("Mon 3 Aug 2026", "9:00am", "Instagram", "static post", "10% off your first order", "promo announcement", 640, 31, 2, 0),
    ("Wed 5 Aug 2026", "8:30am", "Instagram", "carousel", "5 brew methods explained", "educational, short slides", 1420, 96, 11, 14),
    ("Fri 7 Aug 2026", "7:30pm", "Instagram", "reel", "behind the scenes of a small-batch roast", "casual voiceover, 3 hashtags", 5180, 640, 71, 88),
    ("Sun 9 Aug 2026", "11:00am", "Instagram", "static post", "the new menu as a plain list", "informational", 780, 44, 3, 1),
    ("Tue 11 Aug 2026", "10:00am", "LinkedIn", "text post", "how we source beans from Araku farmers", "story-led, first person", 950, 38, 4, 6),
    ("Fri 14 Aug 2026", "8:00pm", "Instagram", "reel", "filter coffee nostalgia, pouring the decoction", "English and Telugu mixed caption, 2 hashtags", 6340, 812, 134, 120),
    ("Sun 16 Aug 2026", "12:00pm", "Instagram", "static post", "a generic Sunday quote", "quote graphic", 520, 25, 1, 0),
    ("Tue 18 Aug 2026", "9:00am", "Instagram", "carousel", "how to read our menu", "explainer", 1050, 60, 6, 5),
    ("Fri 21 Aug 2026", "7:00pm", "Instagram", "reel", "latte art fails compilation", "self-deprecating humour, 2 hashtags", 4700, 590, 62, 77),
    ("Sun 23 Aug 2026", "10:00am", "Instagram", "static post", "giveaway announcement", "giveaway with 15 hashtags", 890, 52, 40, 2),
    ("Tue 25 Aug 2026", "8:00am", "Instagram", "carousel", "cold brew at home guide", "educational, saves-friendly", 1380, 88, 9, 12),
    ("Fri 28 Aug 2026", "8:00pm", "Instagram", "reel", "a barista's day in the life", "ends with the question 'what is your go-to order?'", 5560, 701, 158, 64),
    ("Sun 30 Aug 2026", "9:00am", "Instagram", "static post", "20% off weekend deal", "discount announcement", 610, 28, 2, 0),
    ("Tue 1 Sep 2026", "9:30am", "LinkedIn", "text post", "we are hiring baristas", "direct and warm", 1800, 72, 9, 15),
    ("Fri 4 Sep 2026", "7:45pm", "Instagram", "reel", "monsoon evening filter coffee pour", "English and Telugu mixed caption, 3 hashtags", 7020, 930, 171, 143),
    ("Sun 6 Sep 2026", "11:00am", "Instagram", "carousel", "5 coffee myths busted", "myth vs fact slides", 1610, 118, 16, 21),
    ("Tue 8 Sep 2026", "8:30am", "Instagram", "static post", "a product photo of the beans", "one-line caption", 590, 27, 1, 1),
    ("Fri 11 Sep 2026", "8:00pm", "Instagram", "reel", "customers reacting to their first cold brew", "playful, 4 hashtags", 5900, 760, 96, 90),
    ("Sat 12 Sep 2026", "6:00pm", "Instagram", "reel", "weekend cafe vibe with friends laughing", "light captions, 2 hashtags", 5240, 655, 84, 79),
    ("Tue 15 Sep 2026", "9:00am", "Instagram", "carousel", "3 mistakes when making coffee at home", "educational, save this post", 1720, 131, 19, 28),
    ("Fri 18 Sep 2026", "7:00pm", "Instagram", "reel", "a trending audio clip unrelated to coffee", "15 hashtags", 3100, 320, 22, 15),
    ("Sun 20 Sep 2026", "10:00am", "Instagram", "static post", "15% off this week", "discount announcement", 570, 22, 1, 0),
    ("Tue 22 Sep 2026", "8:45am", "Instagram", "carousel", "how to read a coffee bag label", "educational, save this post", 1940, 158, 24, 41),
    ("Fri 25 Sep 2026", "7:30pm", "Instagram", "reel", "first pour of the new Araku single-origin", "ends with a question to the audience, 3 hashtags", 6880, 905, 184, 132),
]

# Things the owner has said in past conversations (preferences and feedback).
_OWNER_NOTES = [
    "The owner said captions that sound like a corporate brochure feel wrong for Brew & Bloom; she wants a friendly, slightly cheeky barista voice.",
    "The owner said she is happy with a mix of English and Telugu in captions because most regulars speak both.",
    "The owner said she never wants more than 4 hashtags on any post.",
    "The owner said the cafe is closed on Mondays, so no post should invite people to visit on a Monday.",
    "The owner said she does not want competitor cafes mentioned in any post.",
]


def _post_sentence(p) -> str:
    date, time, platform, fmt, topic, style, reach, likes, comments, shares = p
    return (
        f"{date} at {time} IST: Brew & Bloom posted on {platform}, format: {fmt}, about {topic}. "
        f"Caption style: {style}. Result: reach {reach:,}, {likes} likes, "
        f"{comments} comments, {shares} shares."
    )


def _post_time(p) -> datetime:
    date, time = p[0], p[1]
    return datetime.strptime(f"{date.split(' ', 1)[1]} {time.upper()}", "%d %b %Y %I:%M%p").replace(tzinfo=IST)


# Each item gets its own document_id, so loading the samples twice replaces them instead of duplicating.
SEED_ITEMS = (
    [
        {"content": _post_sentence(p), "context": "post performance",
         "timestamp": _post_time(p).isoformat(), "document_id": f"sample-post-{i:02d}"}
        for i, p in enumerate(_POSTS, 1)
    ]
    + [
        {"content": n, "context": "owner preference", "document_id": f"sample-owner-note-{i}"}
        for i, n in enumerate(_OWNER_NOTES, 1)
    ]
)
