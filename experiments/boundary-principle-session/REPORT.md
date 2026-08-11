# Session report — sharpening Balash's design principles by using it

## What this session was

The user tested the current Balash skill the way it is meant to be used: by pointing it at a real
build task, with no extra scaffolding, and watching it drive. Two build tasks were used as **design
proofs** (validation that the method produces a good design), and the conversation that surrounded
them turned into a substantial **sharpening of Balash's design-principles and operating loop**, which
is the durable deliverable committed here.

- **Task A** — a framework to train and predict with a Vision Transformer in **Keras 3**.
- **Task B** — a harder variant: a framework whose **data layer is PyTorch**, whose **augmentation is
  a real library**, and whose **model is Keras 3** — three foreign heavy dependencies to keep off the
  public seams at once.

An honest method note: the first pass ran the method **from memory** (the skill was not yet
registered as an invocable skill in that session). We then **installed the skill** and re-ran it
faithfully from the file. All principle changes below came from running the real, installed skill.

## The durable deliverable — what changed in the skill

Everything below lives on branch `claude/tools-structure-review-3ujsfj` and is merged to `main`.

### 1. `design-principles.md` §2 — choosing the *level of generality* of a boundary type

The section now leads with a **domain-free general rule**, then illustrates it, with an explicit
warning not to mistake the example for the principle:

> The type that crosses an interface should be the **most generic type that is still complete for the
> consumer and still honestly producible by every implementation you unify.** Two independent bounds
> pin it: the consumer's needed information is the **floor** (more generic loses information); the
> least-capable intended producer is the **ceiling** (more specific forces a producer to fabricate or
> distort). The invariant underneath: **minimize the knowledge you force on the other side — no more
> than the concept requires, no less than it needs, and never your own implementation choice.**

Supporting points added:
- The **swap-survival test**: would the type in your public signature survive you swapping your
  implementation? `np.ndarray` survives a Keras→PyTorch swap; `keras.Model` does not.
- The object-detection worked example distinguishing an **identity leak** (`YOLOv26`) from a
  **format leak** (a vendor `Results` object), both fixed by a domain type (`DetectedObject`) defined
  by what the consumer needs, not the vendor's fields renamed.
- The **`angle=0` cram anti-pattern**: a fabrication can be *value-correct yet design-wrong* — an
  axis-aligned rectangle truly is an `OrientedBox` with angle 0, but encoding it that way forces the
  orientation concept onto parties that lack it (§3) and inverts the specialization.
- **Unmeetable bounds → two types, not a lossy compromise.** When no single type satisfies both
  bounds, that is evidence of two genuine concepts: segregate (a `Box` supertype for the common part,
  `OrientedBox` as a subtype), so no producer is flattened (losing info) and none is crammed
  (fabricating a foreign field). `OrientedBox <: Box`.

### 2. `design-principles.md` §7 — which types may cross a public boundary (day-zero, *normative*)

> The only things permitted to cross a public seam are (1) generic interface / your own domain types,
> and (2) a small, **closed set of foundational, cross-infrastructure dependencies agreed in advance**
> (numpy, cv2). Never a concrete type from a dependency you chose as an implementation detail
> (`keras.Model`, `tf.data`, a vendor result object).

The decisive correction here: this set is decided **normatively and up front**, *not* empirically.
"Pass whatever the other side already depends on" is unknowable and invites rationalization; the
permitted foundation is a **shared-kernel / published-language** choice you commit to, and "the
consumer also depends on it" is a *consequence* of that commitment, not an assumption about the
consumer. Balanced against **primitive obsession (§4)**: the answer is your own domain type, not a
retreat to bare primitives. (Source added: Evans, *Domain-Driven Design*.)

**A later extension (§7/§11): the boundary's vocabulary includes its error types.** An implementation
leaks through the *exception channel* exactly as through a parameter or return value — letting a
`torch.cuda.OutOfMemoryError` or a vendor exception escape a public seam couples the consumer to the
chosen implementation. So at a public seam, implementation exceptions are translated into the
framework's own error types phrased in the consumer's concepts (§11), with one carve-out the user
insisted on: failures there is **no utility in catching** — a process-fatal collapse no consumer could
act on (a CUDA OOM that takes the process down anyway) — are left to fall; wrapping them is decorative
machinery. The test is **actionability**. `numpy`/`cv2` were also marked in §7 as *illustrative, chosen
per product* — never a canonical list a future agent should copy as a default.

### 3. Operating loop — **foundational dependencies are now a day-zero step-1 requirement**

The §7 policy was promoted from a principle into the method, on a distinction the user drew sharply:

- A **foundational dependency** is the very-infrastructural substrate everything is built on, whose
  replacement would mean rewriting everything (numpy, scipy, cv2). The test is **pervasiveness, not
  weight**.
- A **heavy but replaceable** dependency (a model framework, a data loader, an augmentation library)
  is **not** foundational — it is confined behind a boundary and can be adopted later.
- The foundational set + own domain types are the only things allowed to cross a public seam.
- It is decided **up front, kept minimal, extended only rarely**. Unlike other technical freedoms it
  is **not deferred to the Worker** (left to accrete, the whole codebase silently couples to whatever
  was picked); the **Guide** decides it unless it materially affects the product. It sets a
  *constraint*, not an architecture.

Touch points: `SKILL.md` step 1; `references/discovery.md` (new section + record-template line);
`assets/state-template.md` (new `### Foundational dependencies (day-zero)` field);
`design-principles.md` §7 cross-reference.

### 4. The command surface — names that explain themselves (§11)

Applying §11 to Balash's *own* public vocabulary. The `/balash-auto` command was renamed to
**`/balash-plan-and-build`** because "auto" did not say what it does. A one-shot `/balash-plan-and-do`
(briefly added, then removed) was recognized as the same concept as the loop — consolidated to one
well-named command rather than two overlapping ones. The public command set is now `/balash-plan`,
`/balash-build`, `/balash-plan-and-build` (the full autonomous plan→build→review loop, which repeats
until the change is delivered), and `/balash-review`. The internal `Mode` value stays `auto` — the
state/hook contract is unchanged — so only the public name moved: rename the surface, keep the
internals, which is the same boundary discipline turned inward. The `balash-guide` skill itself was
also marked `user-invocable: false`, so the bare `/balash-guide` entry point disappears from the slash
menu while the skill stays model-invocable and command-entered — the four phase commands are now the
only user-facing entries.

### 5. Standalone review classifies its kind first (a required gate)

A standalone `review <target>` (a diff / branch / PR with no `.balash/state.md`) has nothing telling it
the review kind or the criteria to measure against — an in-loop review reads both from state. Applying
the wrong lens, or measuring against invented criteria, makes the whole review measure the wrong thing.
So "determine the kind + ground truth" was promoted from a soft inline instruction into an explicit
**Step 0 gate**: before any reading, commit in writing to (1) the **kind** — handling a mixed-kind
change by naming the dominant one and adding the other lens, and asking one concrete question when the
kind is unclear *and* would change what is measured — and (2) the **ground truth**, asking rather than
inventing criteria. Kept as an **inline gate, not a subagent** (the user's alternative): classification
needs exactly the context the review needs, and standalone review already runs inline.

## The two design proofs (validation)

These were demonstrations run in a scratch workspace (not committed here); their role was to test
whether the sharpened method yields good designs. Both reached **met**, and in both the Guide
**measured the result itself** — reading every public signature, grepping the seams, and re-running
the end-to-end slice — rather than trusting the Worker's report.

### Task A — Keras 3 ViT framework
- Preprocessing owned in one place and **baked into the saved artifact**, so train-time and
  predict-time preprocessing are identical *by construction*; a reloaded artifact predicts
  bit-identically to the in-memory model.
- No public signature accepts or returns `tf.data.Dataset` or `keras.Model`; data ingestion sits
  behind a numpy-only return-value seam. The subtractive pass declined a `Preprocessor` class
  precisely because it would reintroduce the two-copies risk.

### Task B — PyTorch data + augmentation library + Keras 3 model
- Each heavy dependency confined to exactly one module (verified by grep): `torch`→`data.py`,
  `keras`→`model.py`, `albumentations`→`augmentation.py`, `cv2`→`preprocessing.py`. The public
  modules import **only numpy**, so no public signature can even *name* a forbidden type.
- The **torch→keras bridge is numpy** (a `collate_fn` returns numpy; Keras runs on the torch
  backend), so neither library reaches the other's module.
- Augmentation is constructed only inside `train()` and handed only to the pipeline, so it is
  **structurally absent from inference**; deterministic preprocessing is a single shared instance
  serialized into the artifact. The Guide re-ran the slice: reloaded vs in-memory score difference
  `0.0`.
- The subtractive pass **declined** the entire `DataBackend`/`ModelBackend`/`Augmenter` ABC family:
  replaceability is delivered *by the confinement boundary*, not by speculative plugin hierarchies
  (§2/§10).

## Commits (branch `claude/tools-structure-review-3ujsfj` → `main`)

1. `design-principles: sharpen the boundary-payload rule (§2/§7)`
2. `design-principles (§2): pin the level of generality from both sides`
3. `design-principles (§2): name the angle=0 cram anti-pattern`
4. `design-principles (§2): unmeetable bounds resolve to two types, not a lossy compromise`
5. `design-principles (§2): lead with the domain-free general rule`
6. `balash: make foundational-dependencies a day-zero step-1 requirement`
7. `report: session summary` (this file; then updated)
8. `design-principles (§7/§11): the boundary vocabulary includes its error types`
9. `commands: add /balash-plan-and-do` — superseded by #10
10. `commands: replace /balash-auto with self-explanatory /balash-plan-and-build`
11. `review: make standalone review classify its kind as a required first gate`

## Throughline

Every change traces to one idea, applied at four levels — the type at a boundary, the *errors* a
boundary may raise, the vocabulary a boundary may speak, and the dependencies a whole codebase stands
on: **minimize the knowledge you force on the other side — no more than the concept requires, no less
than it needs, and never your own implementation choice.** The final touches turned the same lens on
Balash itself: its command names must say what they do (§11) without leaking internal mode names, and
its standalone review must first decide what it is even measuring.
