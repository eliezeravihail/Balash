/**
 * UI wiring for the printable Sudoku generator.
 *
 * Pure presentation layer: reads the controls, calls into
 * `SudokuCore.generateBatch` (src/sudoku-core.js), and renders the
 * resulting puzzles/answer keys as printable pages. Also keeps the
 * batch's seed/difficulty/count reflected in the URL query string so a
 * generated set can be reproduced just by sharing the link.
 */
(function () {
  "use strict";

  const form = document.getElementById("controls");
  const seedInput = document.getElementById("seed");
  const difficultySelect = document.getElementById("difficulty");
  const countInput = document.getElementById("count");
  const randomizeBtn = document.getElementById("randomize-seed");
  const copyLinkBtn = document.getElementById("copy-link");
  const printBtn = document.getElementById("print-btn");
  const statusEl = document.getElementById("status");
  const output = document.getElementById("output");
  const puzzlePageTpl = document.getElementById("tpl-puzzle-page");
  const answersPageTpl = document.getElementById("tpl-answers-page");

  const MIN_COUNT = 1;
  const MAX_COUNT = 50;

  function randomSeed() {
    // Not used for puzzle generation itself (that's deterministic) -
    // only to pick a fresh starting seed for the user, who is then
    // free to edit/share it.
    const bytes = new Uint32Array(2);
    if (window.crypto && window.crypto.getRandomValues) {
      window.crypto.getRandomValues(bytes);
    } else {
      bytes[0] = Math.floor(Math.random() * 0xffffffff);
      bytes[1] = Math.floor(Math.random() * 0xffffffff);
    }
    return (bytes[0].toString(36) + bytes[1].toString(36)).slice(0, 10);
  }

  function clampCount(value) {
    const n = Math.round(Number(value));
    if (!Number.isFinite(n)) return 4;
    return Math.min(MAX_COUNT, Math.max(MIN_COUNT, n));
  }

  function readStateFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const state = {};
    if (params.has("seed")) state.seed = params.get("seed");
    if (params.has("difficulty")) state.difficulty = params.get("difficulty");
    if (params.has("count")) state.count = params.get("count");
    return state;
  }

  function writeStateToUrl(state) {
    const params = new URLSearchParams();
    params.set("seed", state.seed);
    params.set("difficulty", state.difficulty);
    params.set("count", String(state.count));
    const newUrl = `${window.location.pathname}?${params.toString()}`;
    window.history.replaceState(null, "", newUrl);
  }

  function setStatus(message, isError) {
    statusEl.textContent = message;
    statusEl.classList.toggle("error", Boolean(isError));
  }

  // ---------------------------------------------------------------
  // Grid rendering
  // ---------------------------------------------------------------

  function buildGridElement(values, options) {
    options = options || {};
    const grid = document.createElement("div");
    grid.className = "sudoku-grid";
    for (let r = 0; r < 9; r++) {
      for (let c = 0; c < 9; c++) {
        const cell = document.createElement("div");
        cell.className = "cell";
        const value = values[r][c];
        if (value) {
          cell.textContent = String(value);
          if (options.given && options.given[r][c]) {
            cell.classList.add("given");
          } else if (options.markSolutionValues) {
            cell.classList.add("solution-value");
          } else {
            cell.classList.add("given");
          }
        }
        if (c === 2 || c === 5) cell.classList.add("border-right");
        if (r === 2 || r === 5) cell.classList.add("border-bottom");
        grid.appendChild(cell);
      }
    }
    return grid;
  }

  function givenMask(puzzleGrid) {
    return puzzleGrid.map((row) => row.map((v) => v !== 0));
  }

  function renderPuzzlePage(puzzle, batch) {
    const node = puzzlePageTpl.content.firstElementChild.cloneNode(true);
    node.querySelector(".puzzle-title").textContent =
      `Sudoku - ${capitalize(batch.difficulty)} - Puzzle ${puzzle.index + 1} of ${batch.count}`;
    node.querySelector(".page-meta").textContent = `${puzzle.givens} givens`;

    const placeholder = node.querySelector(".sudoku-grid");
    const gridEl = buildGridElement(puzzle.puzzle, { given: givenMask(puzzle.puzzle) });
    placeholder.replaceWith(gridEl);

    node.querySelector(".page-footer").textContent =
      `Seed: ${batch.seed}  ·  Difficulty: ${capitalize(batch.difficulty)}  ·  Puzzle ${puzzle.index + 1}/${batch.count}`;

    return node;
  }

  function renderAnswersPage(batch) {
    const node = answersPageTpl.content.firstElementChild.cloneNode(true);
    node.querySelector(".page-meta").textContent =
      `Seed: ${batch.seed}  ·  Difficulty: ${capitalize(batch.difficulty)}`;

    const answersGrid = node.querySelector(".answers-grid");
    for (const puzzle of batch.puzzles) {
      const item = document.createElement("div");
      item.className = "answer-item";

      const label = document.createElement("p");
      label.className = "answer-label";
      label.textContent = `Puzzle ${puzzle.index + 1}`;
      item.appendChild(label);

      const gridEl = buildGridElement(puzzle.solution, { markSolutionValues: true });
      item.appendChild(gridEl);

      answersGrid.appendChild(item);
    }
    return node;
  }

  function capitalize(word) {
    return word.charAt(0).toUpperCase() + word.slice(1);
  }

  // ---------------------------------------------------------------
  // Generation flow
  // ---------------------------------------------------------------

  function generateAndRender(state) {
    const startedAt = performance.now();
    let batch;
    try {
      batch = SudokuCore.generateBatch(state);
    } catch (err) {
      setStatus(`Could not generate puzzles: ${err.message}`, true);
      return;
    }

    output.innerHTML = "";
    const fragment = document.createDocumentFragment();
    for (const puzzle of batch.puzzles) {
      fragment.appendChild(renderPuzzlePage(puzzle, batch));
    }
    fragment.appendChild(renderAnswersPage(batch));
    output.appendChild(fragment);

    const elapsed = Math.round(performance.now() - startedAt);
    setStatus(
      `Generated ${batch.count} ${capitalize(batch.difficulty)} puzzle${batch.count === 1 ? "" : "s"} ` +
        `from seed "${batch.seed}" in ${elapsed} ms. Each has exactly one solution.`
    );

    writeStateToUrl(state);
  }

  function currentFormState() {
    let seed = seedInput.value.trim();
    if (!seed) {
      seed = randomSeed();
      seedInput.value = seed;
    }
    const difficulty = difficultySelect.value;
    const count = clampCount(countInput.value);
    countInput.value = String(count);
    return { seed, difficulty, count };
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    generateAndRender(currentFormState());
  });

  randomizeBtn.addEventListener("click", () => {
    seedInput.value = randomSeed();
    generateAndRender(currentFormState());
  });

  copyLinkBtn.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setStatus("Shareable link copied to clipboard.");
    } catch (err) {
      setStatus(`Could not copy link automatically - copy it from the address bar: ${window.location.href}`, true);
    }
  });

  printBtn.addEventListener("click", () => {
    window.print();
  });

  // ---------------------------------------------------------------
  // Boot: prefill from URL (if shared) or pick a fresh random seed,
  // then generate immediately so a shared link "just works".
  // ---------------------------------------------------------------

  (function init() {
    const urlState = readStateFromUrl();
    seedInput.value = urlState.seed || randomSeed();
    if (urlState.difficulty && SudokuCore.DIFFICULTIES[urlState.difficulty]) {
      difficultySelect.value = urlState.difficulty;
    }
    countInput.value = String(clampCount(urlState.count || countInput.value));

    generateAndRender(currentFormState());
  })();
})();
