# Domain C — Android ntfy↔messaging bridge. HIDDEN staged spec + oracle policy (agents never see this)

Same strict passive oracle as A/B: answer only what is explicitly asked; never volunteer; the future
(the second channel, Telegram) is NEVER volunteered — if asked "will there be other messengers later?",
answer **"not now — build for what I need today."**

Two architectural cruxes for the final judgment (not shown to agents):
1. **Feasibility gate.** Driving WhatsApp from an ordinary Android app is genuinely unproven/brittle:
   WhatsApp has no public send/receive API; the only avenues are the NotificationListener service
   (read incoming) and Accessibility/UI-automation or notification reply-actions (send) — fragile,
   permission-heavy, breakable by any WhatsApp update, and arguably against WhatsApp ToS. This is a
   textbook "new product resting on an uncertain load-bearing feasibility assumption." A strong method
   should surface this and make **proving the WhatsApp read+send path on a real device the first
   objective (a spike)** before designing the bridge on top of it — NOT design an elegant bridge over an
   unproven premise.
2. **Channel seam.** WhatsApp is one messaging channel; Telegram (stage 2) is a second. Does the design
   isolate a "messaging channel" port that WhatsApp implements, so Telegram slots in as a sibling — or is
   WhatsApp hardwired through the bridge so the second channel forces a tear-open? (Telegram, unlike
   WhatsApp, HAS a real bot API — so the two channels have very different feasibility and mechanics, which
   a good port abstraction must accommodate.)

## Stage 1 — request handed to both arms (verbatim)
> Build an Android app that bridges the ntfy notification service and WhatsApp, so I can run a WhatsApp
> bot where WhatsApp itself only lives on the phone (client side). Concretely: when my server publishes a
> message to an ntfy topic, the app should send it as a WhatsApp message; and when a WhatsApp message
> comes in on the phone, the app should publish it back to an ntfy topic. The bot logic runs on my server
> and talks only to ntfy; the app is the WhatsApp side.

### Oracle answers (stage 1) — current-truthful, forward-only, no future leak
- Which WhatsApp accounts / chats? → "My own WhatsApp on the phone. Outgoing: send to a phone number or chat the server names in the ntfy message. Incoming: messages that arrive to my WhatsApp get forwarded to ntfy."
- ntfy server / topic? → "A topic on the public ntfy.sh (or a server URL I configure). One topic for outgoing (server→app→WhatsApp), one for incoming (WhatsApp→app→ntfy→server) — or however you structure it; I'll configure the topic names."
- Auth to ntfy? → "It can be an open topic to start; I may add a token later, keep that in mind but don't over-build it." (if pressed) 
- How does the app send a WhatsApp message technically? → **This is exactly the uncertain part. Do not hand them a solution.** If asked "is X approach acceptable / will it work?": "I don't know the internals — that's your area. I need it to actually work on my real phone; if a given approach can't reliably send and receive, that's important to find out." (Do NOT confirm any specific API exists; there is no official one.)
- Must it survive the phone rebooting / running in background? → "Yes, it should keep working in the background and after a reboot — it's meant to run unattended on a spare phone."
- Message types? → "Plain text to start."
- Telegram / other messengers? → **not now** (never volunteer): if asked, "Right now just WhatsApp; build for that."

## Stage 2 — revealed only after Stage 1 works/holds
> Now I also want the same bridge to work with **Telegram**, not just WhatsApp — the server publishes to
> ntfy and the app relays to/from Telegram too, and I can use either channel.

### Oracle answers (stage 2)
- One app doing both, or separate? → "One app that can bridge either WhatsApp or Telegram (or both), selected by configuration."
- Telegram mechanism? → "Telegram has an official bot API — use that; it's much more reliable than the WhatsApp side."
- Routing? → "The ntfy message says which channel to use (whatsapp or telegram); incoming messages carry which channel they came from."

## Final judgment (both arms)
- **Feasibility handling (the decisive axis for this domain):** did the arm recognize the WhatsApp
  read+send path is unproven and make *proving it on a real device* the first move — or did it design/
  build an elegant bridge assuming an API that doesn't exist? Charging ahead on a false premise is the
  failure; surfacing and de-risking it is the win.
- **Channel seam:** when Telegram arrives, does it slot into a channel port (WhatsApp and Telegram as
  siblings behind one interface the ntfy-bridge core talks to), or does it force tearing open a
  WhatsApp-hardwired bridge? Note that Telegram (real API) and WhatsApp (fragile automation) differ
  sharply, so the port must not leak WhatsApp assumptions.
- Encapsulation/ownership and the subtractive check as usual. (Buildability caveat: a full Android build
  can't run/verify here, so this domain is judged largely on the design + feasibility posture the arms
  produce, plus whatever runnable core they manage.)
