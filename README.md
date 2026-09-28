# Loop: a social media engagement agent that learns with Hindsight memory

Loop drafts posts for one brand and gets better every time: it recalls what worked before,
writes with that evidence, and stores the results you log so the next draft is smarter.

![Loop answering with memory on](docs/screenshots/03-memory-on.png)

## Run it
1. `python -m venv venv` then activate it (Windows: `venv\Scripts\activate`, Mac/Linux: `source venv/bin/activate`)
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in your three values
4. `uvicorn main:app --reload --port 8000`
5. Open http://localhost:8000

Opening `index.html` from another local server (for example VS Code Live Server) also works, as long as
uvicorn is running on port 8000. If something is misconfigured, a red banner at the top says what.

## Try the demo
1. Click **Just looking? Open the demo café**. It loads 24 sample posts; the "What Loop has learned"
   panel fills in within about a minute
2. Ask: "Write an Instagram post for our new Araku single-origin coffee" with Memory on
3. Switch Memory off and ask the same question. Each mode keeps its own conversation,
   so the generic answer never sees the memory-based one
4. Click **Log results** under a reply, enter numbers, then ask again
5. Click **Weekly readout** for Hindsight's reflection over everything it has learned

All brand data and post numbers in the demo are synthetic.

## Use it for your own brand
Type a brand name and what you post about, tap where you post and how you sound, and save. Audience and
rules are optional. Each brand gets its own memory bank; switch brands, edit one, or add another from the
menu at the top left. Brand profiles are remembered in your browser; everything Loop learns lives in Hindsight.

## How Hindsight is used
- `retain`: brand profile, owner rules, what the owner says in chat, and post results (with their real dates)
- `recall`: before every reply, pulls what worked and what the owner asked for
- `reflect`: writes the weekly readout
- One memory bank per brand keeps each brand's data separate
- Observations (Hindsight's consolidated beliefs) fill the "What Loop has learned" panel
- The server terminal prints one `[memory]` line per recall, retain and reflect, so you can watch memory work live

## Design notes
- Loop stores what the owner says, not its own replies. If it stored its replies, its past
  guesses would come back as "evidence" and it would start agreeing with itself.
- Sample posts and the brand profile use fixed document ids, so loading or saving them again
  replaces the old copy instead of duplicating it.
- The Hindsight sync client is tied to the event loop of the thread that first uses it, so
  every Hindsight call runs on one dedicated thread (see `hs_run` in `main.py`).
# loop-hindsight
# loop-hindsight
