# A/B — the "prove an uncertain load-bearing premise first" gate (validates commit `11983a5`)

**What prompted it.** A Balash run (Codex, a WhatsApp↔ChatGPT bridge) produced a *well-formed* design
objective — clean ownership boundary, adversarial exit criteria, subtractive pass — but it was the wrong
**first** objective: the whole product rested on an unproven, brittle premise (a headless ChatGPT-Web
session surviving on a cloud host past a restart without being blocked), and the design was built on top
of that premise without checking it. The user had to *demand* the feasibility proof; the method didn't
choose it. So the skill gained a calibrated rule (commit `11983a5`): when a **new product rests on a
genuinely uncertain load-bearing premise**, the first objective is a **minimal build (spike) that proves
the premise plausible** before designing on it — while a product whose feasibility is obvious (a CRUD
app, a Monday/Trello clone, a second implementation of a proven capability) proceeds straight to design.

## Method

Two blind arms, **same neutral product brief** ([`product-brief.md`](product-brief.md) — a WhatsApp↔
ChatGPT bridge, stated the way a user would, with **no hint** that feasibility is the risk). The only
difference between arms is the **method text**:

- **Arm OLD** — `balash-guide` at the commit **before** the gate (`skill-old/`).
- **Arm NEW** — `balash-guide` **with** the gate (`skill-new/`).

Each arm was told the foundational substrate was already settled (Node/TS/Baileys/ChatGPT-web) and asked
to run the plan phase and state **objective 0001 only**. Nobody told either arm that the ChatGPT-Web
persistence assumption was the risk.

## Result — the gate changes the first move

| | Arm OLD (pre-gate) | Arm NEW (with gate) |
|---|---|---|
| **Objective 0001 Kind** | `design` | `implementation` |
| **What it chose** | "Produce a buildable architecture… boundaries that locate the concurrency/ownership decisions" — i.e. **design the ownership boundary on top of the unproven premise** | "Prove the product's load-bearing feasibility premise with a **minimal end-to-end spike**… running headless on the real Google Cloud VM… survives a process restart without re-login" |
| **The unproven premise** | not surfaced as the priority | named as objective 0001; the ownership design **explicitly deferred to 0002** |

Arm NEW, with no prompting, reproduced exactly the correct move the user had to force in the original
run: *prove the ground exists before designing on it.* Arm OLD reproduced the original failure — an
elegant boundary over a premise that might be false (and if false, the product becomes a different
product — the excluded official API).

## Honest limit

**n = 1 per arm.** This is a single-run mechanism check (the arms' outputs are deterministic *choices*,
not graded opinions), not a replicated result. Per the methodology note now in `../RESULTS.md`, a
load-bearing wording change deserves **≥ 2 runs per arm** before it is treated as robust; this one is
directional. The arm outputs below are the verbatim objective-0001 statements each produced.

## Files
- [`product-brief.md`](product-brief.md) — the shared, neutral product request given to both arms.
- [`skill-old/`](skill-old) / [`skill-new/`](skill-new) — the two method-text variants (SKILL.md, discovery.md, objective-selection.md).
- [`arm-old-objective.md`](arm-old-objective.md) / [`arm-new-objective.md`](arm-new-objective.md) — each arm's verbatim objective 0001.
