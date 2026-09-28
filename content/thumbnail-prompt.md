# Thumbnail prompt (Prompt 6)

Paste everything in the box into Nano Banana (Gemini) and attach a clear, well-lit photo of yourself
(looking at the camera or pointing to one side works best). You can also attach
`docs/screenshots/05-memory-off.png` and `docs/screenshots/03-memory-on.png` so it can borrow the real UI.

```text
Generate a viral thumbnail for this YouTube video. Make the thumbnail attention grabbing and something that people scrolling would want to click on if they see it. The aspect ratio needs to be 16:9.

Visual direction: a near-black background with one acid-lime accent (#C5F25A), matching the app. Split the frame in two. Left side, dimmed grey and labelled "MEMORY OFF": a generic Instagram caption ending in a long row of hashtags, with a red "8 hashtags" callout. Right side, glowing lime and labelled "MEMORY ON": the same post with a short caption and a "14 memories used" badge. Put the person from the attached photo on the right edge, looking surprised at the left side. Big bold headline text, at most 5 words: "IT CITED ITSELF". Keep text large enough to read on a phone.

Here is the video script:

Hi, I'm [your name]. This is Loop, a social media agent that learns what works for one brand. You set a brand up with two fields and a few taps, it drafts posts, and every result you log goes into long-term memory with Hindsight. The drafting isn't the interesting part. What's interesting is what the agent is allowed to remember.

Here's the agent with memory off. Same model, same question. It writes a perfectly decent caption, and then eight hashtags. This café's owner has one hard rule: never more than four. Without memory the agent has no idea, and every conversation starts from zero.

Memory on. Before it generates anything, Loop calls Hindsight's recall twice. Fourteen memories came back. Now it suggests a reel, stays under the hashtag limit, and cites a real post: the first-pour reel from September 25th, 6,880 reach.

Here's the bug: my first version retained Loop's own replies. One time recall came back empty, the model invented a carousel-at-10-AM plan, that reply got stored, and the next answer cited it as evidence. It was agreeing with itself. Now it only retains what the owner says, and replies only come back as evidence after they've been posted and measured.

I log the reel's real results, reload, ask again, and the new draft cites them. Reflect writes a weekly readout from the whole memory bank.

What surprised me: the model didn't get any smarter. What changed was what it remembers, and what I stopped letting it remember.
```
