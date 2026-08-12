# Base Dependencies

## Foundational substrate

Set by the user in the product request (not chosen by the Guide or Worker):

- **JavaScript on Node.js (pure Node, no framework).** Everything stands on it; the language and
  runtime are the substrate.
- **Zero external dependencies.** No npm packages, ever, unless the user changes this. The public
  seams speak only JavaScript built-in types and our own domain types.
- **In-memory state.** No storage layer of any kind is part of the substrate; all product state
  lives in process memory.
- **`node:test` (built-in runner) for tests.** Each stage ships tests runnable with `node --test`.
- **Time is integer minutes; intervals are half-open [start, end).** A substrate-level
  representation decision: every time value crossing any seam is an integer minute count.
