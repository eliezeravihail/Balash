# Framing a task before you do it

A general companion to the Balash method. Balash makes *design* the goal a coding agent is handed;
this is the same idea for **any** task you give a capable agent — "plan a pension", "find the bugs",
"write the report". It is **not a form to fill in**. It is how to think about what the task actually is
before answering it — because a strong agent optimizes whatever it was told, so the *framing*, not just
the effort, decides whether the result helps. Read the six ideas below as a lens, not a ledger: none is
a box to tick; each is a question whose honest answer changes the work.

## Why framing is the work

A capable agent will produce *something* for any task. The danger is never that it does nothing — it is
that it optimizes the literal ask and quietly settles everything the ask left open by whatever default
is easiest. "Plan a pension" collapses into "list some funds"; "find the bugs" into "skim for the
obvious ones". The output looks like an answer and misses the thing that mattered. Framing is the short,
deliberate act of surfacing — *before* you execute — the few things that decide whether the result is
genuinely useful.

## 1. Optimize the real outcome, not a proxy for it

The agent hits exactly the target it was given, so name the outcome that would truly help the person, in
their terms — not the nearest easy-to-produce substitute. A pension plan's real outcome is "the money
lasts through a bad market to the end of life", not "a portfolio exists". A bug hunt's real outcome is
"the failures that would actually hurt a real user are found", not "a list of warnings was produced". If
you cannot yet state the real outcome plainly, you are not ready to start — that gap is the first thing
to close.

## 2. Find the hard judgment the task hides — and face it, don't route around it

Every task worth doing turns on one or two genuinely hard calls, and the lazy framing lets exactly those
evaporate. The value of the work lives there. For a pension: *how much loss can this person actually
endure without bailing out at the bottom* — the number that silently governs everything downstream. For
bugs: *which failure is catastrophic versus cosmetic* — because a hunt with no sense of severity buries
the one that matters under noise. Say the hard call out loud and make confronting it part of the task. A
good framing pushes the hard question to the surface instead of letting the agent slip past it to the
easy parts.

## 3. Separate what you know, what only the person can decide, and what you may choose freely

Three kinds of open point, and the discipline is not to confuse them. Facts you already have. Decisions
that change the result and belong to the human alone — **ask these, never guess**, because a plausible
guess here is still a guess, and it quietly decides someone's life or system for them. And free choices
with no real consequence — just pick something sensible and move on, without turning them into a
questionnaire. Pension: retirement age, dependents, real appetite for risk — ask. Bugs: what "correct"
even means here, what is in and out of scope — ask. The cardinal error is disguising a decision that is
the person's as a technical assumption of your own.

## 4. Say, checkably, what a good result looks like

A target you cannot test against is one the agent will meet on paper and miss in fact. Replace "a good
plan" or "be thorough" with a few conditions you could actually check. Pension: "it survives a
2008-scale drop without the money running out before age 90." Bugs: "every failure reported comes with
an input that reproduces it, or a precise pointer to the line." This is what stops the agent from
declaring a success it did not earn — and what stops it from leaving the exact hard cases unhandled
because nobody named them as part of "done".

## 5. Say what not to optimize, and what must not break

An unbounded "make it good" quietly trades away things that mattered. Name the constraints and the
things to preserve, so they are not sacrificed to the headline goal. Pension: don't chase the maximum
return; keep enough liquid for an emergency. Bugs: don't refactor while hunting; preserve the current
behavior. Naming what to hold fixed is as much of the frame as naming what to pursue — often more,
because it is what the agent's own drive to optimize will otherwise erode.

## 6. Trust evidence, not the agent's own say-so

The agent — like anyone — will report confidence it has not earned: "the plan is safe", "I checked every
path". A self-report cannot be verified, whether it is mistaken or deliberately glib; asking "are you
sure?" only invites the same answer again. So require the *evidence* to be present in the result, or the
claim to be marked unverified. Pension: "this survives a bad decade" means nothing without the actual
drawdown it was tested against. Bugs: "I checked all the inputs" means nothing without the list of what
was checked. Ask to see the basis, not to be reassured — because the presence or absence of the basis is
something you can actually observe, and a promise is not.

## Using this

These six are a way of thinking, not a checklist to satisfy. Before executing any task, reason through
them *in the task's own terms*, ask the person the few things only they can answer, and only then do the
work. The measure is not that six fields got filled — it is that you refused to start until you actually
understood what would make the result help, and named the hard call, the checkable "done", and the
things to protect, plainly enough that you could be held to them. A frame you can tick without thinking
is not a frame; it is the failure this document exists to prevent.
