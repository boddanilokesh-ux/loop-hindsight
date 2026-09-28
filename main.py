"""Loop: a social media engagement agent that learns your audience with Hindsight memory.

Flow for every chat message:
  1. RECALL   what Hindsight knows about this brand (what worked, owner rules, audience)
  2. GENERATE a reply with the LLM, grounded in those memories
  3. RETAIN   the exchange so the next reply is smarter
Post results the user logs are RETAINED too, and Hindsight consolidates them into
"observations" (learned beliefs) that we show in the Memory panel.
"""
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import List, Literal, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from groq import Groq
from hindsight_client import Hindsight

from seed_data import DEMO_BRAND, SEED_ITEMS, profile_sentence

load_dotenv()

for _key in ("HINDSIGHT_URL", "GROQ_API_KEY"):
    if not os.getenv(_key):
        print(f"[config] {_key} is not set. Copy .env.example to .env and fill it in.")

HS = Hindsight(
    base_url=os.getenv("HINDSIGHT_URL", "http://localhost:8888"),
    api_key=os.getenv("HINDSIGHT_API_KEY") or None,
    timeout=90.0,
)
# Created only when a key is set, so the server still starts and the page can explain what is missing.
LLM = Groq(api_key=os.getenv("GROQ_API_KEY")) if os.getenv("GROQ_API_KEY") else None
MODELS = list(dict.fromkeys([os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"), "qwen/qwen3-32b"]))

app = FastAPI(title="Loop")
# Let the page work even when it is opened from another local server (e.g. VS Code Live Server on :5500).
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_methods=["*"],
    allow_headers=["*"],
)
_known_banks = set()

# The Hindsight sync client binds its HTTP session to the event loop of the first thread that uses it.
# FastAPI runs sync routes on a pool of worker threads, so calling it directly fails at random
# ("Timeout context manager should be used inside a task"). Every Hindsight call goes through this one thread.
_hs_thread = ThreadPoolExecutor(max_workers=1, thread_name_prefix="hindsight")


def hs_run(fn, **kwargs):
    return _hs_thread.submit(fn, **kwargs).result()


def log(action: str, bank: str, detail: str) -> None:
    """One terminal line per memory operation, so retain/recall/reflect are visible live."""
    line = f"[memory] {action:<7} {bank}  {detail}"
    enc = sys.stdout.encoding or "utf-8"  # a redirected Windows console may not be UTF-8; never crash on emoji
    print(line.encode(enc, "replace").decode(enc), flush=True)


# ---------- helpers ----------
def bank_id(user_id: str) -> str:
    """One memory bank per workspace/user, so each user's data stays separate."""
    slug = re.sub(r"[^a-z0-9-]", "-", user_id.lower()).strip("-")[:40] or "demo"
    return f"loop-{slug}"


def make_mission(brand: str) -> str:
    return (
        f"I am Loop, a social media engagement strategist for {brand}. I learn from every post "
        "result, audience reaction and piece of owner feedback: which formats, topics, tones and "
        "posting times work for THIS audience. When new results contradict an old belief, I "
        "update the belief and keep the history."
    )


def hs(action: str, fn, **kwargs):
    """Call Hindsight and turn failures into a readable 502 instead of a bare 500."""
    try:
        return hs_run(fn, **kwargs)
    except Exception as e:
        print(f"[hindsight:{action}] {e}")
        raise HTTPException(502, f"Memory service failed to {action}. Check HINDSIGHT_URL and HINDSIGHT_API_KEY.")


def ensure_bank(bank: str, brand: str = "this brand") -> None:
    if bank in _known_banks:
        return
    try:
        hs_run(
            HS.create_bank,
            bank_id=bank,
            name="Loop",
            mission=make_mission(brand),
            disposition={"skepticism": 4, "literalism": 2, "empathy": 3},
        )
    except Exception as e:  # bank probably exists already
        print(f"[create_bank] {e}")
    _known_banks.add(bank)


def clean(text: str) -> str:
    """Drop Hindsight's '| Involving: ...' style suffixes but keep the '| When: ...' date."""
    parts = [p.strip() for p in text.split(" | ")]
    keep = [parts[0]] + [p for p in parts[1:] if p.startswith("When:")]
    return " | ".join(keep)


def recall_texts(bank: str, query: str, types: Optional[List[str]] = None, limit: int = 12):
    kwargs = dict(bank_id=bank, query=query, budget="mid", max_tokens=2500)
    if types:
        kwargs["types"] = types
    try:
        res = hs_run(HS.recall, **kwargs)
        out = [{"text": clean(r.text), "type": getattr(r, "type", None)} for r in res.results][:limit]
        log("recall", bank, f"{query[:50]!r} -> {len(out)} memories" + (f" [{', '.join(types)}]" if types else ""))
        return out
    except Exception as e:
        print(f"[recall] {e}")
        return []


def recall_context(bank: str, message: str):
    """Two searches: the user's actual request + a standing 'what do we know' query."""
    queries = (message, "brand voice, owner rules, audience preferences, best and worst performing posts and timing")
    seen, merged = set(), []
    for q in queries:  # sequential: the Hindsight sync client is not safe to share across threads
        for m in recall_texts(bank, q):
            if m["text"] not in seen:
                seen.add(m["text"])
                merged.append(m)
    return merged[:14]


def call_llm(system: str, messages: list) -> str:
    if LLM is None:
        raise HTTPException(503, "GROQ_API_KEY is not set. Add it to .env and restart the server.")
    last = None
    for model in MODELS:  # open models can fail; fall back to the next one
        try:
            r = LLM.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": system}] + messages,
                temperature=0.7,
                max_tokens=1500,
            )
            text = re.sub(r"<think>.*?</think>", "", r.choices[0].message.content or "", flags=re.S).strip()
            if text:
                return text
            last = "empty reply"
        except Exception as e:
            last = e
        print(f"[llm:{model}] {last}")
    raise HTTPException(502, f"The language model call failed: {last}")


def build_system(memories: list, memory_on: bool) -> str:
    if not memory_on:
        return (
            "You are a generic social media assistant. You know nothing about this user's brand, "
            "audience or past results. Give sound but general advice and draft posts in a neutral style. "
            "Keep it under 180 words."
        )
    facts = "\n".join(f"- {m['text']}" for m in memories) or "- (no memories yet)"
    return (
        "You are Loop, a social media engagement strategist for ONE specific brand.\n"
        f"Today is {datetime.now():%A %d %B %Y}.\n"
        "Below is what your long-term memory (Hindsight) recalled for this request.\n\n"
        f"MEMORY:\n{facts}\n\n"
        "Rules:\n"
        "1. Ground every recommendation in the MEMORY. Never invent metrics that are not there.\n"
        "2. Obey the owner's rules and preferences in MEMORY strictly (hashtag limits, closed days, tone).\n"
        "3. Measured post results and owner statements are evidence. Loop's own earlier drafts are NOT "
        "evidence: never justify a choice by saying you suggested it before.\n"
        "4. If MEMORY has no evidence for something, say so and suggest a small test.\n"
        "5. Format: the draft first (caption, format, best time to post), then one line starting with "
        "'Why:' that names the specific past results or preferences that shaped it.\n"
        "6. Be concise: under 220 words."
    )


# ---------- request models ----------
class Msg(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatReq(BaseModel):
    user_id: str
    message: str = Field(min_length=1, max_length=4000)
    memory: bool = True
    history: List[Msg] = []


class OnboardReq(BaseModel):
    user_id: str
    name: str
    niche: str
    audience: str
    platforms: str
    tone: str
    rules: str = ""


class ResultReq(BaseModel):
    user_id: str
    post_text: str = ""
    platform: str = "Instagram"
    format: str = "reel"
    posted_at: str = ""
    reach: int = Field(0, ge=0)
    likes: int = Field(0, ge=0)
    comments: int = Field(0, ge=0)
    shares: int = Field(0, ge=0)
    note: str = ""


class UserReq(BaseModel):
    user_id: str


# ---------- routes ----------
@app.get("/")
def home():
    return FileResponse(os.path.join(os.path.dirname(__file__), "index.html"))


@app.get("/api/ping")
def ping():
    """Instant check the page uses to find this server. Makes no outside calls."""
    return {"loop": True}


@app.get("/api/health")
def health():
    try:
        hs_run(HS.get_version)
        hs_ok = True
    except Exception:
        hs_ok = False
    return {"hindsight": hs_ok, "llm_key_set": bool(os.getenv("GROQ_API_KEY"))}


@app.post("/api/onboard")
def onboard(req: OnboardReq):
    bank = bank_id(req.user_id)
    ensure_bank(bank, req.name)
    # A fixed document_id means saving the profile again replaces the old one instead of piling up.
    hs("save the brand profile", HS.retain, bank_id=bank, content=profile_sentence(req.model_dump()),
       context="brand profile", document_id="brand-profile")
    log("retain", bank, f"brand profile for {req.name!r}")
    return {"ok": True}


@app.post("/api/seed")
def seed(req: UserReq):
    """Load 24 synthetic posts + owner notes so the demo starts with history."""
    bank = bank_id(req.user_id)
    ensure_bank(bank, DEMO_BRAND["name"])
    hs("save the brand profile", HS.retain, bank_id=bank, content=profile_sentence(DEMO_BRAND),
       context="brand profile", document_id="brand-profile")
    hs("load the sample posts", HS.retain_batch, bank_id=bank, items=SEED_ITEMS, retain_async=True)
    log("retain", bank, f"{len(SEED_ITEMS)} sample memories (async batch)")
    return {"ok": True, "count": len(SEED_ITEMS)}


@app.post("/api/chat")
def chat(req: ChatReq):
    bank = bank_id(req.user_id)
    memories = []
    if req.memory:
        ensure_bank(bank)
        memories = recall_context(bank, req.message)

    messages = [{"role": m.role, "content": m.content} for m in req.history[-6:]]
    messages.append({"role": "user", "content": req.message})
    reply = call_llm(build_system(memories, req.memory), messages)

    # RETAIN what the owner said (requests, preferences, feedback) in the background so the user
    # isn't kept waiting. Loop's own reply is deliberately not stored: otherwise its past guesses
    # come back later as "evidence" and the agent starts agreeing with itself.
    if req.memory:
        try:
            hs_run(
                HS.retain,
                bank_id=bank,
                content=f"The brand owner told Loop: {req.message}",
                context="owner message in chat",
                retain_async=True,
            )
            log("retain", bank, f"owner message {req.message[:50]!r} (Loop's reply is not stored)")
        except Exception as e:
            print(f"[retain] {e}")
    return {"reply": reply, "memories": memories, "memory_on": req.memory}


@app.post("/api/result")
def log_result(req: ResultReq):
    """The learning loop: real performance numbers go back into memory."""
    bank = bank_id(req.user_id)
    ensure_bank(bank)
    when = None
    try:
        when = datetime.fromisoformat(req.posted_at)
    except ValueError:
        pass
    when_text = f" posted {when:%a %d %b %Y at %I:%M%p}" if when else (f" posted {req.posted_at}" if req.posted_at else "")
    text = (
        f"Result of a {req.platform} {req.format}{when_text}: \"{req.post_text[:240]}\". "
        f"Reach {req.reach:,}, {req.likes} likes, {req.comments} comments, {req.shares} shares. {req.note}"
    ).strip()
    kwargs = dict(bank_id=bank, content=text, context="post performance")
    if when:
        kwargs["timestamp"] = when
    hs("save the post result", HS.retain, **kwargs)
    log("retain", bank, f"post result: {req.platform} {req.format}, reach {req.reach:,}, {req.comments} comments")
    return {"ok": True}


@app.get("/api/learned/{user_id}")
def learned(user_id: str):
    """What the agent believes now. Observations are Hindsight's consolidated beliefs."""
    bank = bank_id(user_id)
    q = "what works and what does not for this audience: formats, topics, tone, posting times, owner rules"
    observations = recall_texts(bank, q, types=["observation"], limit=10)
    recent = []
    if len(observations) < 3:  # consolidation can lag a little behind retain
        recent = recall_texts(bank, "post results and owner preferences", types=["world", "experience"], limit=6)
    return {"observations": observations, "recent": recent}


@app.post("/api/insights")
def insights(req: UserReq):
    """REFLECT: Hindsight reasons over memory and writes a weekly readout."""
    bank = bank_id(req.user_id)
    ensure_bank(bank)
    ans = hs(
        "write the readout", HS.reflect,
        bank_id=bank,
        query=(
            "Give the owner a weekly readout in 4 short bullets: what is working for this audience, "
            "what is not, and one thing to test next week. Cite the evidence."
        ),
        budget="low",
        context="weekly readout for the brand owner",
    )
    log("reflect", bank, "weekly readout")
    return {"text": ans.text}
