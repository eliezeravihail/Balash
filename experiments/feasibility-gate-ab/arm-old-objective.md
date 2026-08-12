# Arm OLD — objective 0001 (verbatim), method *without* the feasibility gate

The pre-gate skill chose a **design** objective — designing the ownership boundary on top of the
still-unproven ChatGPT-Web-persistence premise, never questioning whether the premise holds.

---

> This is a brand-new product. The method (SKILL.md) is explicit that the very first objective of a new
> product is a **design** objective that reaches a *buildable* architecture. Levels 1 (product outline)
> and 2 (foundational substrate) are already settled … What remains ungrounded is level 3: the module
> skeleton and concrete TypeScript interface signatures. The method requires the objective to put the
> **hard decision** at its core — here that is the concurrency/ownership tension the brief describes …
>
> **OBJECTIVE 0001**
> **Kind:** design
> **Objective:** Produce a buildable architecture (module skeleton plus concrete TypeScript interface
> signatures on the fixed Node/Baileys/ChatGPT-web substrate) whose boundaries locate two hard
> decisions: who owns each sender's active-conversation selection versus the shared conversation store,
> and where per-conversation in-order execution is serialized so that concurrent requests from both
> numbers to the same conversation run in arrival order while every reply routes back to its originating
> sender.
> **Why now:** The product cannot be sprinted on until the seams are pinned in the chosen language, and
> the brief's central risk is not any single feature but the shared-account / per-sender-pointer /
> same-conversation-ordering interaction …
> **First exit criterion:** The architecture names the single component owning per-conversation FIFO
> execution and walks a two-senders-same-conversation interleaving …

**Reading:** the risk it named is the *concurrency/ownership* design tension — a real design question,
but not the one that decides whether the product can exist at all. The unofficial-integration
feasibility premise is treated as settled and built upon. This reproduces the original failure the gate
was written to prevent.
