# Domain A — Inventory management. HIDDEN staged spec + oracle answers (agents never see this file)

The agents see only the **current stage's request**. 

## Oracle policy — strict, passive, no volunteering
Asking the right questions is itself part of the method under test, so the oracle **answers only what is
explicitly asked** and **volunteers nothing**:
- **Broad "what do you need?"** → the owner names only the *forward* operations that come to mind:
  add a product, adjust its quantity as stock moves, see the inventory. Nothing more.
- **Complements** (remove a product, look up a single product, rename) → confirmed **only if the agent
  specifically probes** ("should I also support removing / editing / looking one up?"). If never asked,
  never told — and the agent's product simply won't have it. That gap is a real result, not noise.
- **Invariants / details** (unique names, non-negative, persistence, adjust-by-delta) → stated only when
  asked about that specific point.
- **The future** (web, multi-user, roles) → never volunteered; if asked "will there be X later?", the
  honest current answer is **"not now — build for what I need today."** Balash is NOT rewarded for
  guessing the future.

Answers are truthful for the **current stage only**. What each agent walks away knowing is exactly what
its own questions earned.

## Stage 1 — request handed to both arms (verbatim)
> Build me an inventory management tool that runs locally on my own machine. I track products — each
> product has a name and a quantity in stock. I need to add a new product, adjust a product's quantity as
> stock comes in or goes out, and see the current inventory whenever I want.

### Oracle answers (stage 1) — current-truthful, no future leak
- Users / login? → "It's just me, on my own machine. No login, no accounts."
- Web / remote / other machines? → "No — local only. I run it on my computer."
- Persistence between runs? → "Yes, it must remember the inventory after I close and reopen it."
- What identifies a product? → "Its name. Names are unique. Quantity is a whole number, never negative."
- **Remove a product** (complement of add)? → "Yes — if we stop carrying something I remove it."
- **Adjust down as well as up / see one product** (complements)? → "Yes, quantity goes up and down; I also want to look up a single product, not only the whole list."
- Audit trail / history of changes? → "Not needed now."
- Units, categories, price, supplier, locations, min-stock alerts? → "No. Just name and quantity, one location."
- What happens on an adjust that would go below zero? → "Block it; quantity can never be negative."
- Roughly how many products? → "A few hundred at most."
- "Should I design it so it could later become web-based / multi-user?" → "Don't build for that. Right now it's a local single-user tool; keep it simple for what I need today."

## Stage 2 — revealed only after Stage 1 is built
> Now I want to use this from a web browser instead of the terminal, so I can open it on any machine on
> my home/office network. Same features, just reachable in a browser.

### Oracle answers (stage 2)
- Multiple users / logins now? → "Still just me for now, but through the browser. No logins yet."
- Concurrent editing? → "Occasionally two browser tabs; nothing fancy. Don't lose data."
- Hosting? → "Runs on one machine, reachable over the local network. You choose the how."
- Keep the terminal version too? → "Don't care about the terminal anymore; the browser is the product now."

## Stage 3 — revealed only after Stage 2 is built
> Now I need separate access for a manager and employees. People log in with a username and password and
> can register. A new employee registers with a name and password, but a manager must approve them before
> they can use the system. Managers can add and remove products and approve employees; employees can only
> adjust quantities (not add/remove products, not approve people).

### Oracle answers (stage 3)
- First manager? → "Seed one manager account at setup (username admin). Everyone else registers and waits for approval."
- Can a manager also adjust quantities? → "Yes, a manager can do everything an employee can, plus manage products and approve people."
- Rejected / pending employee sees what? → "A pending employee is told they're awaiting approval and can't do anything else yet."
- Password storage? → "Store them safely, not in plain text. You handle the how."
- Audit of who changed what? → "Nice but not required now — don't block on it."
- Can an employee be removed / demoted later? → "Not needed now."

## What the final (post-stage-3) architecture is judged on (Balash review, blind, both arms)
Purely the **architectural quality of the final result** — not how much changed to get there:
- Is the **domain** (products, quantity rules, the non-negative invariant) owned in one coherent place,
  independent of delivery (CLI/web) and of auth?
- Is **authorization** (who may add/remove vs only adjust) owned at a single boundary, or scattered as
  ad-hoc checks?
- Is **identity/accounts/approval** a coherent unit with clear ownership?
- Encapsulation / coherence vs. tangle; and the **subtractive** check — is there speculative machinery
  that never earned its place (Balash can lose here if it over-built)?
- Does it actually work (deterministic checks: non-negative invariant holds; employee cannot add/remove;
  unapproved user is blocked)?
