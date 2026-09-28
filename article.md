# My Hindsight agent started citing its own guesses as evidence

The answer looked great. Loop, the social media agent I built on [Hindsight agent memory](https://github.com/vectorize-io/hindsight), recommended a carousel at 10 AM for a café's new single-origin coffee, and it backed the plan with a confident justification: "We're using the carousel layout and 10 AM slot that were recommended in our Sep 28 2026 plan for the Araku coffee series."

The only plan from Sep 28 was one Loop had written itself, minutes earlier, with nothing useful in memory. The café's real history pointed the other way: its Friday-evening reels mostly reached 4,700 to 7,000 people, and its static posts never broke 900.

My agent had started agreeing with itself. Here's how that happened, and what the fix looks like in code.

## What Loop does

Loop is a strategist for one brand at a time. You describe the brand in a few taps, then ask things like "write an Instagram post for our new Araku coffee" or "why do my discount posts get so little reach?" When a post goes live, you log its reach, likes, comments, shares and a note.

The stack is small: a FastAPI app (`main.py`), a single-page UI, Groq for generation (`openai/gpt-oss-120b`, falling back to `qwen/qwen3-32b`), and Hindsight for everything the agent knows. Each brand gets its own memory bank, created with a mission that tells Hindsight what the memory is for: learning which formats, topics, tones and posting times work for this audience.

Every chat message runs three steps:

1. **Recall** what Hindsight knows that's relevant.
2. **Generate** a reply grounded in those memories.
3. **Retain** something, so the next reply is better.

Post results are retained too, with their real timestamps. Hindsight extracts facts and consolidates them in the background into observations, beliefs like "reels featuring the café's craft drive the highest engagement," which fill a "What Loop has learned" panel. `reflect` turns the whole history into a weekly readout. That's the whole surface of Hindsight's [retain, recall and reflect APIs](https://hindsight.vectorize.io/). The rest of this post is about where I held them wrong.

![How Loop uses Hindsight: recall before every reply, retain only owner messages and measured results](docs/architecture.png)

## The bug: step three stored the wrong thing

My first version of step three stored the whole exchange: `content=f"The user asked: {req.message}\nLoop replied: {reply[:600]}"`. The agent remembers the conversation. That's what memory means, right?

The first time I asked about the new coffee, recall came back empty (more on why in the lessons), so the model produced a plausible generic plan: a carousel at 10 AM. That reply went straight into memory, and Hindsight did exactly its job, extracting a clean, dated fact: "Loop created a carousel Instagram post for Araku coffee featuring farm, roasting, brewing, and tasting notes."

The next time I asked, recall surfaced that fact next to the real post history. To a language model, a dated statement about a carousel plan looks exactly like evidence, so it cited it. The memory layer wasn't wrong. I had filed the agent's own speculation as experience.

This generalizes: any agent that writes its outputs into the store it reads evidence from will drift toward agreeing with itself.

## The fix: retain inputs, not outputs

Step three now stores only what the owner said:

```python
# RETAIN what the owner said (requests, preferences, feedback) in the background so the user
# isn't kept waiting. Loop's own reply is deliberately not stored: otherwise its past guesses
# come back later as "evidence" and the agent starts agreeing with itself.
if req.memory:
    hs_run(
        HS.retain,
        bank_id=bank,
        content=f"The brand owner told Loop: {req.message}",
        context="owner message in chat",
        retain_async=True,
    )
```

Owner messages are real signal. The agent's replies are hypotheses, and a hypothesis only becomes evidence once it's tested: a draft that gets posted and measured comes back through "Log results" with numbers attached. A draft nobody posted shouldn't come back at all.

The system prompt says so too, because older banks can still hold self-generated facts: "Loop's own earlier drafts are NOT evidence: never justify a choice by saying you suggested it before." And `retain_async=True` means retention no longer delays the reply.

## Recall: two queries, not one

A single recall on the user's message fails for vague questions. "What should I post this weekend?" looks nothing like "the café is closed on Mondays," but both matter. So each chat runs two recalls and merges them:

```python
def recall_context(bank: str, message: str):
    """Two searches: the user's actual request + a standing 'what do we know' query."""
    queries = (message, "brand voice, owner rules, audience preferences, best and worst performing posts and timing")
    seen, merged = set(), []
    for q in queries:
        for m in recall_texts(bank, q):
            if m["text"] not in seen:
                seen.add(m["text"])
                merged.append(m)
    return merged[:14]
```

The second query is boring on purpose: it keeps the owner's rules in context even when the question doesn't mention them.

## What it looks like now

The UI has a Memory switch. Off means no recall, no retain, a generic system prompt, and a separate conversation history. (My first version shared one history across both modes, which quietly leaked brand details into the "generic" answers.)

To test Loop, I seeded a bank with 24 posts of history for a café brand plus five owner rules, then asked the same question in both modes: "Write an Instagram post for our new Araku single-origin coffee."

Memory off produced a competent caption for a generic coffee brand, ending in eight hashtags. The owner's first rule is "never more than 4 hashtags."

![Memory off: a generic caption that breaks the owner's hashtag rule](docs/screenshots/05-memory-off.png)

Memory on suggested a 15-second reel of the first pour, and its "Why" line used numbers it hadn't invented: "The Sep 25 Reel of the first Araku pour pulled 6,880 reach, 905 likes, 184 comments, and 132 shares—our strongest recent performance, so we'll replicate that format and timing while staying under the 4-hashtag limit."

![Memory on: 14 memories recalled, and a draft grounded in a real post's numbers](docs/screenshots/03-memory-on.png)

Then the loop closed. I logged a result for that reel: 7,120 reach, 948 likes, 201 comments, and a note that lots of commenters asked where the beans came from. In a later session, with an empty chat history, the draft invited followers to ask about the beans' journey and cited the new result: "A Reel on 28 Sept 2026 about Araku beans reached 7,120 people, earned 948 likes and sparked many 'origin?' comments." The weekly readout from `reflect` turned that note into a recommendation to test a post "dedicated exclusively to the 'story behind the bean'", and flagged the 15%-off post that reached 570 people as what wasn't working.

![The weekly readout from reflect, next to the beliefs Hindsight consolidated](docs/screenshots/07-weekly-readout.png)

None of that lives in the prompt or the chat history. It lives in the bank.

## Lessons

**1. Retain inputs and measured outcomes, never raw outputs.** If your agent writes into the store it reads evidence from, it will eventually cite itself. Outputs should earn their way into memory by being tested.

**2. Give memories stable IDs and real timestamps.** Sample posts and the brand profile use fixed document IDs, so saving a profile twice replaces it instead of stacking contradictory versions. Hindsight rejects an async batch whose items share a document ID, which is how I caught a bug in my seeding code. Timestamps matter because "what's working lately?" is a temporal question:

```python
{"content": _post_sentence(p), "context": "post performance",
 "timestamp": _post_time(p).isoformat(), "document_id": f"sample-post-{i:02d}"}
```

**3. Know your client's concurrency model.** Remember the empty recall that started all this? The Python client wraps async calls in a sync API, and its HTTP session is tied to the event loop of the first thread that uses it. FastAPI runs sync routes on a thread pool, so calls failed at random with "Timeout context manager should be used inside a task." It looked like flaky memory; it was my threading. The smallest fix was one worker thread that owns every Hindsight call:

```python
_hs_thread = ThreadPoolExecutor(max_workers=1, thread_name_prefix="hindsight")

def hs_run(fn, **kwargs):
    return _hs_thread.submit(fn, **kwargs).result()
```

Async routes with the client's async methods would be cleaner.

**4. Show the memory.** The "What Loop has learned" panel and the "What it remembered" button did more for trust than any prompt tweak. When an answer cites a number, you can open the exact memories behind it. That's how I spotted my agent's own carousel plan in its recall results, dressed up as history.

## Closing

The model didn't get smarter between the eight-hashtag answer and the one that cited a real reel. What changed was what it was allowed to remember, and what I stopped letting it remember. If you're adding long-term memory to an agent, read up on [what agent memory is and how it differs from stuffing context](https://vectorize.io/what-is-agent-memory) before deciding what to write into it. In Loop, the most important line of code is the one that doesn't retain the reply.
