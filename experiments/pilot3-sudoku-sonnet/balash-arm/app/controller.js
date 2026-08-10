// app/controller.js
//
// Thin glue: reads the difficulty/count/seed form inputs, calls
// PuzzleGenerator.generateBatch, hands the result to the renderer, wires
// the print button and the URL. Owns no domain rules -- every decision
// about uniqueness/difficulty/randomness lives in domain/. This is also
// the ONLY place in the app allowed to call Math.random/Date -- minting
// a fresh seed identity when the user leaves the field blank is a UI
// concern, not something domain/seed.js does (domain/ stays pure, D1).

import { Seed } from '../domain/seed.js';
import { Difficulty } from '../domain/difficulty.js';
import { generateBatch } from '../domain/generator.js';
import { renderBatch } from '../rendering/print-view.js';

const MAX_COUNT = 12;

const form = document.getElementById('controls');
const difficultyInput = document.getElementById('difficulty');
const countInput = document.getElementById('count');
const seedInput = document.getElementById('seed');
const generateBtn = document.getElementById('generate-btn');
const printBtn = document.getElementById('print-btn');
const statusEl = document.getElementById('status');
const resultInfo = document.getElementById('result-info');
const resultSeedEl = document.getElementById('result-seed');
const resultDifficultyEl = document.getElementById('result-difficulty');
const resultCountEl = document.getElementById('result-count');
const permalinkEl = document.getElementById('permalink');
const puzzlesContainer = document.getElementById('puzzles');
const answersContainer = document.getElementById('answers');

form.addEventListener('submit', (event) => {
  event.preventDefault();
  runGeneration();
});

printBtn.addEventListener('click', () => {
  window.print();
});

prefillFromURL();

// If the URL already carries a full spec (difficulty+seed), generate
// immediately so a shared link reproduces its batch without an extra click.
if (new URLSearchParams(window.location.search).has('seed')) {
  runGeneration();
}

function prefillFromURL() {
  const params = new URLSearchParams(window.location.search);
  const difficultyKey = params.get('difficulty');
  const count = params.get('count');
  const seed = params.get('seed');

  if (difficultyKey && Difficulty.byKey(difficultyKey)) {
    difficultyInput.value = difficultyKey;
  }
  if (count && Number.isFinite(Number(count))) {
    countInput.value = clampCount(Number(count));
  }
  if (seed) {
    seedInput.value = seed;
  }
}

function clampCount(n) {
  return Math.min(MAX_COUNT, Math.max(1, Math.round(n)));
}

function mintSeedIdentity() {
  // The only place in the app allowed to reach for real nondeterminism.
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
}

function runGeneration() {
  const difficultyKey = difficultyInput.value;
  const difficulty = Difficulty.byKey(difficultyKey);
  const count = clampCount(Number(countInput.value) || 1);
  countInput.value = count;

  const typedSeed = seedInput.value.trim();
  const seedIdentity = typedSeed || mintSeedIdentity();
  seedInput.value = seedIdentity;
  const seed = Seed.from(seedIdentity);

  setStatus(`Generating ${count} ${difficulty.name} puzzle(s)…`, 'working');
  printBtn.disabled = true;
  resultInfo.hidden = true;

  // Generation is synchronous CPU work; defer one tick so the "working"
  // status actually paints before the main thread is busy.
  window.setTimeout(() => {
    const result = generateBatch(seed, difficulty, count);

    if (!result.ok) {
      setStatus(
        `Could not generate puzzle ${result.failedSlot + 1} of ${result.count} ` +
          `at ${difficulty.name} difficulty (${result.reason}). Try a different seed.`,
        'error',
      );
      puzzlesContainer.replaceChildren();
      answersContainer.replaceChildren();
      return;
    }

    renderBatch(result.batch, { puzzlesContainer, answersContainer });

    setStatus(`Ready: ${count} ${difficulty.name} puzzle(s) generated.`, 'ok');
    printBtn.disabled = false;
    showResultInfo(seedIdentity, difficulty, count);
    updateURL(seedIdentity, difficultyKey, count);
  }, 0);
}

function setStatus(message, kind) {
  statusEl.textContent = message;
  statusEl.dataset.kind = kind;
}

function showResultInfo(seedIdentity, difficulty, count) {
  resultSeedEl.textContent = seedIdentity;
  resultDifficultyEl.textContent = difficulty.name;
  resultCountEl.textContent = String(count);
  permalinkEl.href = buildURL(seedIdentity, difficulty.key, count);
  resultInfo.hidden = false;
}

function buildURL(seedIdentity, difficultyKey, count) {
  const url = new URL(window.location.href);
  url.search = '';
  url.searchParams.set('seed', seedIdentity);
  url.searchParams.set('difficulty', difficultyKey);
  url.searchParams.set('count', String(count));
  return url.toString();
}

function updateURL(seedIdentity, difficultyKey, count) {
  const url = buildURL(seedIdentity, difficultyKey, count);
  window.history.replaceState({}, '', url);
}
