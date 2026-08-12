# Arm NEW — objective 0001 (verbatim), method *with* the feasibility gate

The gated skill chose an **implementation** objective — a minimal end-to-end spike that proves the
load-bearing premise on the real target *before* any ownership/boundary design — and explicitly deferred
the design to objective 0002. No one told it feasibility was the risk; it derived that from the gate.

---

> This is the textbook "new product on a genuinely uncertain load-bearing assumption" case, so I'll
> follow the method's explicit ruling for it.
>
> **OBJECTIVE 0001**
> **Kind:** implementation
> **Objective:** Prove the product's load-bearing feasibility premise with a minimal end-to-end spike: a
> message from an allow-listed WhatsApp number (via Baileys) is driven into a headless-automated ChatGPT
> web session and the model's reply is delivered back to that sender — running headless on the real
> Google Cloud VM, with both logins persisted so the flow survives a process restart without re-login.
> **Why now:** The product rests entirely on two unofficial, brittle integrations — Baileys for WhatsApp
> and browser-driving the ChatGPT web app — running headless on a cloud VM with sessions that must
> survive restarts; if that ground does not hold, no ownership/boundary design matters because it would
> be a different product. The method requires this doubt to be objective number one, proven before any
> design is built on top of it.
> **First exit criterion:** On the target GCP VM, headless, an allow-listed number sends a plain text
> message and receives ChatGPT's actual reply to that same number, demonstrated as a real round trip
> (not mocked).
>
> **RATIONALE:** Feasibility here is genuinely uncertain (unofficial Baileys + undocumented ChatGPT-web
> automation, headless, on a cloud host with restart-surviving auth), which the method says outranks
> every design objective — so the correct first move is a minimal spike declared `implementation`, not
> the ownership/boundary/architecture design. Designing the elegant conversation-routing and
> shared-account boundaries first would be optimizing the wrong thing, because a false premise (session
> blocked or not persistable on the VM) would invalidate that design entirely. Once this round trip and
> its restart-survival hold, the ARCHITECTURE-level design objective … becomes objective 0002.

**Reading:** the gate flipped the first move from "design the boundary" to "prove the ground exists" —
exactly the correction the user had to force by hand in the run that prompted the change.
