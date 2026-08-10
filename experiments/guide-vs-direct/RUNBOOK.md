# Runbook

## Research question

Does separating engineering-objective selection from implementation improve how well a software product absorbs realistic later changes, while requiring only ordinary product-language input from the user?

## Controlled variables

Use for both conditions:

- the same coding model and model version;
- the same reasoning setting / budget where configurable;
- the same tools and repository permissions;
- fresh, empty repositories;
- the exact same stage requirements;
- the same test/runtime environment;
- no access to later stage files before the current stage is complete.

The Guide condition may use extra model calls because the extra reasoning loop is the treatment being tested. Record that cost; do not artificially give Direct hidden architecture instructions to equalize it.

## Conditions

### Direct

At each stage, send only the exact content of `scenario/stage-N.md` to the coding agent. The agent may plan, inspect, code and test as it normally would. Do not add "clean architecture", future hints, or reviewer instructions.

### Guide

At each stage, send the exact same `scenario/stage-N.md` to Balash Guide. The Guide may ask product questions according to its skill. Answer using `scenario/user-oracle.md` and the answer policy below. The Guide delegates implementation to a Worker. The Worker must not see future stage files.

## Answer policy for Guide questions

The experiment operator acts as an ordinary product owner, not an architect.

1. Answer from facts explicitly available in `user-oracle.md` for the current stage.
2. Do not volunteer facts the Guide did not ask for.
3. Never reveal a later-stage requirement.
4. If the Guide asks a technical-choice question the ordinary user should not decide (architecture pattern, interface shape, database abstraction, etc.), answer: `I don't know; choose a simple sensible technical approach.`
5. If the Guide asks about a hypothetical future capability not established at the current stage, answer: `I don't know yet. Build for what I described without making the product unnecessarily rigid.`
6. Log every question and answer in `logs/guide-questions.md`.

This is important: Balash is being tested on its ability to turn product knowledge into engineering objectives, not on its ability to make the user act as the architect.

## Stage protocol

For each condition and each stage:

1. Ensure only the current and previous requirements are visible.
2. Deliver the current stage requirement verbatim.
3. Allow the condition to work until it claims the requested product behavior is complete.
4. Run the project's tests.
5. Commit the repository with tag `stage-N`.
6. Run `python evaluator/collect_metrics.py <repo> --stage N` from this experiment package and append/save the JSON output.
7. Record model usage if available: turns, input/output tokens, wall-clock time and model calls.
8. Only then reveal the next stage to both conditions.

Do not let one condition see the other condition's repository.

## Number of runs

Minimum useful pilot: 1 Direct + 1 Guide run.

Evidence worth trusting: at least 3 independent runs per condition with fresh model contexts:

- Direct-1, Direct-2, Direct-3
- Guide-1, Guide-2, Guide-3

Do not reuse a conversation/session across independent repetitions.

## What success looks like

The hypothesis is supported if Guide tends to show, across later stages:

- smaller and more coherent change surfaces for comparable behavior;
- fewer unrelated source modules touched by a product change;
- less need for large corrective refactors before adding a feature;
- tests/invariants that make later changes safer;
- fewer speculative abstractions that never become useful;
- a final structure whose responsibilities remain understandable;
- reasonable user-question burden.

The initial implementation does not need to be more elaborate than Direct. In fact, unnecessary up-front framework code counts against Guide.

## Prompt contamination check

Before a run, search the Guide skill/instructions for vocabulary that names or strongly suggests later scenario changes. The experimental Guide must teach **how to derive objectives**, not contain a catalog that accidentally predicts the hidden stages.

For this packaged version, the Guide materials intentionally avoid mentioning the later experiment concepts such as the concrete assignee types, storage technologies, or dependency feature.
