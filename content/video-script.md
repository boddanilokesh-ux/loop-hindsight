# Video script: "My agent started citing its own guesses" (about 3 minutes)

Replace `[your name]`. Talk it through in your own words rather than reading it; the lines are a guide.

## Before you hit record
- Start the server in a terminal you can show on screen:
  `venv\Scripts\python.exe -m uvicorn main:app --port 8000`
- Open http://localhost:8000 and click **Open the demo café** about two minutes before recording, so the
  "What Loop has learned" panel is already full.
- Open `main.py` in your editor at the chat route (search for `@app.post("/api/chat")`).
- Increase the font size in the browser (Ctrl +), the editor and the terminal. Turn off notifications.
- Record at 1080p or higher (the guide's minimum), and record the screen itself, not a phone pointed at it.
- Keep the server terminal visible next to the browser. Every memory operation prints one `[memory]` line
  (`recall`, `retain`, `reflect`). That's how you show retain and recall happening live.
- The model's wording and numbers change between runs. Point at whatever the "Why:" line actually cites.

## 0:00–0:30 Intro
**On screen:** your camera, or the app with the brand menu open (top left, **Add a brand** shows the setup screen; press Cancel after).

> Hi, I'm [your name]. This is Loop, a social media agent that learns what works for one brand. You set a brand up with two fields and a few taps, it drafts posts, and every result you log goes into long-term memory with Hindsight. The drafting isn't the interesting part. What's interesting is what the agent is allowed to remember.

## 0:30–1:00 The problem: no memory
**On screen:** click the **Memory** switch to off. The grey note appears: "Memory is off…". Click the suggestion
**Write an Instagram post for our new Araku single-origin coffee**. Zoom in on the hashtag line and the
"Generic answer, no memory" tag.

> Here's the agent with memory off. Same model, same question. It writes a perfectly decent caption, and then eight hashtags. This café's owner has one hard rule: never more than four. Without memory the agent has no idea, and every conversation starts from zero.

## 1:00–2:55 Demo: recall, retain, and the bug
**1:00 On screen:** switch Memory back on. A divider appears in the chat. Ask the same question.

**On screen:** point at the terminal: two `[memory] recall` lines appear before the reply, then
`[memory] retain ... owner message ... (Loop's reply is not stored)` right after it.

> Memory on. Before it generates anything, Loop calls Hindsight's recall twice: once with my question, and once with a standing query for the brand's rules and its best and worst posts. You can see both recalls in the terminal, and then a retain of my message. Not its reply. Hold that thought.

**1:15 On screen:** point at the "14 memories used" tag, then the **Why:** line.

> Fourteen memories came back. Now it suggests a reel, stays under the hashtag limit, and the Why line cites a real post: the first-pour reel from September 25th, 6,880 reach.

**1:30 On screen:** click **What it remembered**.

> This is exactly what recall returned: past posts with their dates, and the owner's rules. None of this is in the prompt template. It's in the memory bank.

**1:45 On screen:** switch to `main.py`, the retain block at the end of the chat route.

> Here's the bug I want to talk about. My first version retained the whole exchange, the question and Loop's reply. One time recall came back empty, so the model invented a plan: a carousel at 10 AM. That reply got stored, and the next answer cited it as evidence: "the carousel layout recommended in our September 28th plan." It was agreeing with itself. Now it only retains what the owner says. Replies are hypotheses, and they only come back as evidence after they've been posted and measured.

**2:15 On screen:** back to the app. Under the memory-on reply click **Log results**. Fill in Reach 7120,
Likes 948, Comments 201, Shares 139, note "lots of comments asked where the beans are from". Click
**Save to memory**. Show the terminal line `[memory] retain ... post result: Instagram reel, reach 7,120, 201 comments`.

> So let's measure it. This goes to the result endpoint, which retains the numbers with the real posting time.

**2:30 On screen:** reload the page (the chat is empty again) and ask the same question.

> Fresh page, empty chat history. The new draft leans into the beans' origin story, and the Why line cites the result I just logged.

(If the Why line doesn't mention it, ask: "What did we learn from the Araku reel?")

**2:45 On screen:** click **Weekly readout** in the right-hand panel; the terminal prints `[memory] reflect ... weekly readout`.

> And reflect writes a weekly readout from the whole bank: reels about the café's craft are working, the 15%-off post that reached 570 people isn't, and it suggests testing a story-behind-the-bean post, straight from that comment note.

## 2:55–3:20 Takeaway
**On screen:** your camera, or `docs/architecture.png`.

> What surprised me: the model didn't get any smarter between the eight-hashtag answer and this one. What changed was what it remembers, and what I stopped letting it remember. Retain inputs and measured outcomes, never raw outputs. The code's linked below, and so is Hindsight.

---

## Title options
1. My AI Agent Started Citing Its Own Guesses (Here's the Fix)
2. Same Agent, Same Question: Memory Off vs Memory On
3. The One Line That Stopped My Agent Agreeing With Itself
4. I Built a Social Media Agent That Learns From Every Post
5. Adding Long-Term Memory to an Agent With Hindsight (Live Demo)

## Description (paste under the video)
```text
Loop is a social media agent that learns what works for one brand, using Hindsight for long-term memory.
In this demo: the same question with memory off and on, the bug where my agent started citing its own guesses,
and how logging a post's results changes the next answer.

Code: [GitHub repo link]
Article: [article URL]
Hindsight: https://github.com/vectorize-io/hindsight
```
