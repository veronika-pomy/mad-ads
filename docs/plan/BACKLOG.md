# Backlog: AI Ad Agency over Telegram (agentic-assisted build)

Derived from [PLAN.md](./PLAN.md). Structured so each day ends with a
concrete, independently verifiable outcome — suitable for driving with an
agentic coding assistant one ticket at a time (small, testable diffs instead
of one big generation pass).

## How to use this backlog

- Work top to bottom within a day; don't start day N+1's tickets until day
  N's "End-of-day verification" passes.
- Each ticket has a **Definition of Done (DoD)** that is checkable by
  running a command or observing a concrete artifact — not "looks right."
  Verify by an actual run before checking it off.
- When handing a ticket to an agent, paste just that ticket (title +
  acceptance criteria) as the task — keeps context small and diffs reviewable.
- If a ticket needs splitting further while working, split it; don't let one
  agent turn touch more than ~1 concern (one file/module or one integration
  point).

---

## Day 1 — Repo scaffold + Telegram round-trip proven

**Goal: prove the one external dependency you don't control (Telegram) works, before writing any agent code.**

- [x] **1.1 Repo scaffold**
  Create the file structure from PLAN §7 (`app.py`, `agents_defs.py`,
  `telegram_tools.py`, `conversation_store.py`, `.env.example`,
  `book_brief.example.json`, `target_reader.example.json`, empty
  `manuscript/`).
  **DoD:** `python -c "import app"` (or equivalent entrypoint check) runs
  without `ImportError`; `.env.example` lists `TELEGRAM_BOT_TOKEN` and
  `OPENAI_API_KEY`.
  **Verified:** `python app.py` imports `telegram_tools` and
  `conversation_store` cleanly.

- [x] **1.2 Dependency + env setup**
  Add `requirements.txt`/`pyproject.toml` with `requests` (or
  `python-telegram-bot`), `openai`/agent-framework SDK, `python-dotenv`.
  **DoD:** fresh virtualenv install (`pip install -r requirements.txt`)
  succeeds with no errors.
  **Verified:** clean `.venv` install of `requests`, `python-dotenv`,
  `openai` succeeded.

- [x] **1.3 Delete stale webhook, confirm bot identity**
  Call `deleteWebhook`, then `getMe`, using the existing bot token.
  **DoD:** `getMe` response printed to terminal shows the correct bot
  username; `getWebhookInfo` shows `"url": ""` afterward.
  **Verified:** bot is `@aries1221_bot`; webhook already absent.

- [x] **1.4 Outbound round-trip**
  Implement `send_telegram_message(chat_id, text)` in `telegram_tools.py`
  using the Bot API `sendMessage`.
  **DoD:** running a small script sends a real message to your test chat;
  you see it arrive in the Telegram client within a few seconds.
  **Verified:** test message sent to chat_id 1118353116, confirmed received.

- [x] **1.5 Inbound round-trip**
  Implement a `getUpdates` long-poll loop; print incoming messages + their
  `chat_id` to the console.
  **DoD:** typing a message to the bot in Telegram prints it (with correct
  `chat_id`) in the terminal within the poll interval.
  **Verified:** `poll_updates` printed live inbound messages from chat_id
  1118353116 while running.

- [ ] **1.6 Draft brief files**
  Fill `book_brief.example.json` and `target_reader.example.json` from your
  actual manuscript/published book (schema in PLAN §3a).
  **DoD:** both files parse as valid JSON (`python -m json.tool file.json`
  exits 0) and contain non-placeholder `title`, `back_cover_blurb`,
  `tropes`, `purchase_link`.

**End-of-day verification:** run one script that (a) sends yourself a
message, (b) waits for your reply, (c) prints it back — all against the
real bot. No agent/LLM code involved yet.

---

## Day 2 — Copywriter agents + code-orchestrated drafting

**Goal: brief in → 3 distinct, on-style drafts out, no manual judging needed yet.**

- [ ] **2.1 Agent definitions**
  Port the 3 copywriter agents (Professional / Witty / Punchy) into
  `agents_defs.py` using the `intro` + style-instructions pattern from
  PLAN §3, parameterized by `{target_reader}` / `{book_brief}`.
  **DoD:** each agent object/function is independently callable and
  returns a non-empty string for a given brief.

- [ ] **2.2 Orchestrator (code-based, parallel)**
  Implement `asyncio.gather` (or equivalent) call to all 3 copywriters given
  one brief.
  **DoD:** running the orchestrator against
  `book_brief.example.json`/`target_reader.example.json` returns exactly 3
  non-empty strings in under ~15s.

- [ ] **2.3 Manual style QA**
  Run the orchestrator 3 times; read the 9 outputs.
  **DoD:** for each run, all 3 drafts are (a) non-empty, (b) recognizably
  different in tone from each other, (c) read like ad copy/blurb, not
  literary prose or a full summary — record this pass/fail in this
  checklist, don't just eyeball once.

**End-of-day verification:** one command takes a brief file path and prints
3 labeled drafts to the console.

---

## Day 3 — Picker + Telegram send wired end-to-end (Phase A complete)

**Goal: brief in → best ad lands in your real Telegram chat, fully automated.**

- [ ] **3.1 Picker agent**
  Implement the picker using the rubric in PLAN §6; input is the 3 drafts +
  target reader, output is exactly one selected ad (no explanation).
  **DoD:** given 3 clearly different drafts, the picker returns text that
  exactly matches one of the 3 inputs (byte-for-byte), 5 runs in a row.

- [ ] **3.2 Wire Picker → send_telegram_message**
  Picker/Sender agent calls the Day 1 send tool with the winning draft and
  your test `chat_id`.
  **DoD:** running `app.py` (or a `phase_a` entrypoint) end-to-end — brief
  in, no manual steps — results in exactly one message arriving in your
  Telegram chat, and it is readable (no raw JSON/markdown artifacts).

- [ ] **3.3 Basic tracing**
  Add `with trace(...)` (or logging) around the draft/pick/send pipeline.
  **DoD:** a log/trace file or console output shows, for one run: 3 drafts
  produced, 1 picked, 1 sent, with timestamps.

**End-of-day verification:** Phase A checklist items from PLAN §9 (rows
1–3) all pass in one live run.

---

## Day 4 — Conversation store + inbound loop (Phase B skeleton)

**Goal: a buyer's reply reliably reaches an agent and gets *some* response — even a stub — proving the loop works before investing in Closer prompt quality.**

- [ ] **4.1 Conversation store**
  Implement `conversation_store.py`: append inbound/outbound messages to a
  JSON file or SQLite table keyed by `chat_id`; provide a `get_history(chat_id)`.
  **DoD:** after sending 2 messages and receiving 2 replies, `get_history`
  returns all 4 in correct chronological order.

- [ ] **4.2 Stub Closer agent**
  Implement a Closer that just echoes/acknowledges ("Thanks for your
  message, more soon!") — no real sales logic yet.
  **DoD:** replying in Telegram triggers a visible ack reply within a few
  seconds, and both messages are recorded in the conversation store.

- [ ] **4.3 Loop robustness check**
  Send 3 replies in a row (simulating a real back-and-forth) without
  restarting the process.
  **DoD:** all 3 get acked, history has 6 entries in order, process does not
  crash or double-reply to any single message.

**End-of-day verification:** PLAN §9 checklist row "Replying in Telegram
triggers the Closer agent within a few seconds" passes; conversation
history persists across the run.

---

## Day 5 — Real Sales Closer prompt (Phase B complete)

**Goal: the Closer can actually sell — answer FAQs, handle objections, share the link — without hallucinating or being pushy.**

- [ ] **5.1 Closer prompt**
  Replace the stub with the full prompt from PLAN §3a (tropes, comp titles,
  no-pressure rules, link-sharing condition), fed the accumulated history
  each turn.
  **DoD:** the agent's system/instructions text includes the book's real
  `tropes` and `purchase_link` interpolated from the brief (not hardcoded
  literals).

- [ ] **5.2 Scripted persona QA — interested buyer**
  Manually role-play a buyer who asks 2–3 questions then says "sounds
  great, where do I get it?"
  **DoD:** Closer answers questions using only facts present in
  `book_brief.json` (no invented plot details) and shares `purchase_link`
  only after the buyer signals interest.

- [ ] **5.3 Scripted persona QA — skeptical buyer**
  Role-play objections (price, "not sure it's my genre").
  **DoD:** Closer responds to the specific objection raised (not a generic
  reply) and does not push the purchase link before genuine interest is shown.

- [ ] **5.4 Scripted persona QA — goes quiet**
  Stop replying mid-conversation.
  **DoD:** Closer does not send unprompted follow-up/chase messages (verify
  by leaving the chat idle for a few minutes with no new bot messages).

**End-of-day verification:** PLAN §9 checklist rows on Closer accuracy,
link-sharing, and non-pushiness all pass across the 3 personas above.

---

## Day 6 — Full end-to-end QA pass

**Goal: the whole flow — brief → 3 drafts → pick → send → reply → close — works as one continuous run, with issues found and fixed, not just each phase in isolation.**

- [ ] **6.1 One continuous run**
  From a cold process start: load brief → generate/pick/send ad → reply as
  buyer → carry a 4+ turn conversation → reach a clear buy/decline outcome.
  **DoD:** all 8 items in PLAN §9's manual QA checklist are checked off in
  a single session, not stitched together from separate runs.

- [ ] **6.2 Fix rough edges found in 6.1**
  Track each issue found during 6.1 as a sub-item here as you find it, and
  close them out same-day.
  **DoD:** re-running 6.1 after fixes reproduces no previously-seen bugs.

- [ ] **6.3 Trace review**
  Check `platform.openai.com/traces` (or equivalent) for the run in 6.1.
  **DoD:** no failed/errored spans in the trace for the full run.

**End-of-day verification:** a single unattended run satisfies the entire
PLAN §9 checklist, and you can point to a trace/log as evidence.

---

## Day 7 — Polish, deploy, document (buffer day)

**Goal: a shareable, always-on demo plus a README someone else could run from cold.**

- [ ] **7.1 Prompt polish**
  Address any tone/quality nits noticed during Day 6 QA (not new features).
  **DoD:** re-run the Day 6 continuous-run checklist after changes; still
  all green.

- [ ] **7.2 Deploy to always-on host**
  Push to a small VM or PaaS background worker per PLAN §12
  recommendation, using the existing polling loop (no webhook migration).
  **DoD:** send a message to the bot from a phone (not your dev machine) and
  receive a Closer reply, while your laptop is asleep/off.

- [ ] **7.3 README**
  Write setup + run instructions (env vars, how to start Phase A, how the
  poller runs) and a "known limitations" section from PLAN §10.
  **DoD:** a person unfamiliar with the repo can follow the README alone to
  get a message sent, with no undocumented steps.

- [ ] **7.4 Demo artifact**
  Record a short demo run (screen recording or saved trace + transcript).
  **DoD:** artifact committed or linked in README; playable/viewable
  end-to-end.

**End-of-day verification:** fresh clone + README-only setup on a second
machine (or clean env) reaches a working send within a reasonable amount of
time, with no tribal knowledge required.

---

## Out-of-scope reminder

Do not pull in items from PLAN §11 (Stretch Goals) during this week —
webhook migration, multi-business config, admin views, and payment tracking
are explicitly post-POC. If an agent session suggests one mid-task, defer it
to a new backlog entry instead of expanding current scope.
