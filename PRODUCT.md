# Loop — product context

**What it is:** a social media engagement agent for one brand at a time. It drafts posts, suggests formats
and posting times, and learns from the results the owner logs, using Hindsight long-term memory.

**Who uses it**
- Creators and small brand owners managing one or a few brands (e.g. a gaming creator, a café).
  Setup must take under a minute; no long forms.
- People trying it for two minutes, such as viewers of a demo. The demo brand must be one click away and
  the difference between Memory on and Memory off must be obvious.

**Core jobs**
1. Tell Loop about the brand (name, what it is, audience, platforms, tone, rules).
2. Ask for a post / timing / explanation and get a grounded draft.
3. Log how a post performed so Loop learns.
4. See what Loop has learned and get a weekly readout.

**Look & feel (owner's choice):** dark and sleek — dark-first, one vivid accent, feels at home next to
gaming and streaming dashboards. Mode: Operate (task-focused app UI).

**Constraints:** single static `index.html` served by FastAPI (`main.py`); no build step; API routes
`/api/onboard, /api/seed, /api/chat, /api/result, /api/learned/{id}, /api/insights, /api/health`.
All demo data (Brew & Bloom) is synthetic.
