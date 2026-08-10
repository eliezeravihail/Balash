// app (edge, the ONLY code that touches the page) — reads the textarea, settings
// and URL; builds domain values; mints a seed if blank (the single
// nondeterministic act, done OUTSIDE the core and fed in); calls generate();
// asks the renderer to paint; surfaces the seed and any input-cleaning notices.
// It holds NO domain rules.

import { WordList } from './core/wordlist.js';
import { Seed } from './core/seed.js';
import { selectGridSize } from './core/gridsize.js';
import { generate } from './core/generate.js';
import { renderCardSetHtml } from './render.js';
import { buildShareUrl, parseShareFragment } from './share.js';

const CARD_COUNT_DEFAULT = 8;
const CARD_COUNT_MAX = 30;

const els = {
  words: document.getElementById('words'),
  cardCount: document.getElementById('cardCount'),
  seed: document.getElementById('seed'),
  generate: document.getElementById('generate'),
  print: document.getElementById('print'),
  share: document.getElementById('share'),
  copySeed: document.getElementById('copySeed'),
  notices: document.getElementById('notices'),
  output: document.getElementById('output'),
};

// ---- helpers ----------------------------------------------------------------

// Mint a fresh seed. This — and only this — is nondeterministic, and it lives
// OUTSIDE the core.
function mintSeed() {
  const n = Math.floor(Math.random() * 0x100000000) >>> 0;
  return Seed.fromUint32(n);
}

function clampCardCount(raw) {
  const n = parseInt(raw, 10);
  if (!Number.isFinite(n)) return CARD_COUNT_DEFAULT;
  return Math.max(1, Math.min(CARD_COUNT_MAX, n));
}

function showNotices(lines, kind = 'info') {
  els.notices.className = `notices notices--${kind}`;
  els.notices.innerHTML = lines
    .map((l) => `<p>${l.replace(/&/g, '&amp;').replace(/</g, '&lt;')}</p>`)
    .join('');
}

function clearOutput() {
  els.output.innerHTML = '';
  els.print.disabled = true;
  els.share.disabled = true;
}

// ---- the one action ---------------------------------------------------------

function run() {
  // 1. Read the page.
  const rawText = els.words.value;
  const cardCount = clampCardCount(els.cardCount.value);
  els.cardCount.value = String(cardCount);

  // 2. Build domain values. WordList owns all cleaning; read its stats for the
  //    honest "your pool changed" notice.
  const { wordList, stats } = WordList.build(rawText);

  // 3. Resolve the seed: parse what's typed, or mint a fresh one and show it.
  let seed;
  const typedSeed = els.seed.value.trim();
  if (typedSeed === '') {
    seed = mintSeed();
    els.seed.value = seed.toString();
  } else {
    const parsed = Seed.parse(typedSeed);
    if (!parsed.ok) {
      clearOutput();
      showNotices([parsed.error.message], 'error');
      return;
    }
    seed = parsed.value;
    els.seed.value = seed.toString();
  }

  // 4. Call the pure core. Typed outcomes only — no exceptions to catch.
  const result = generate(wordList, { cardCount }, seed);
  if (!result.ok) {
    clearOutput();
    showNotices([result.error.message], 'error');
    return;
  }
  const cardSet = result.value;

  // 5. Paint.
  els.output.innerHTML = renderCardSetHtml(cardSet);

  // 6. Report: cleaning notices + distinctness facts.
  const notices = [];
  if (stats.blanksDropped > 0) {
    notices.push(`Dropped ${stats.blanksDropped} blank line(s).`);
  }
  if (stats.duplicatesMerged > 0) {
    notices.push(`Merged ${stats.duplicatesMerged} duplicate word(s).`);
  }
  notices.push(
    `${cardSet.gridSize} grid from a pool of ${wordList.size} words. ` +
      `Seed ${seed.toString()}.`,
  );
  if (cardSet.isTruncated) {
    notices.push(
      `Requested ${cardSet.requestedCount} cards but the pool can only make ` +
        `${cardSet.producedCount} distinct card(s); stopped there rather than repeat.`,
    );
    showNotices(notices, 'warn');
  } else {
    notices.push(`Generated ${cardSet.producedCount} distinct card(s).`);
    showNotices(notices, 'info');
  }

  els.print.disabled = false;
  els.share.disabled = false;

  // Stash current state for sharing.
  run._last = { words: wordList.words, cardCount, seed: seed.toString() };
}

// ---- wiring -----------------------------------------------------------------

function doShare() {
  if (!run._last) return;
  const base = `${location.origin}${location.pathname}`;
  const { url, includesWords } = buildShareUrl(base, run._last);
  navigator.clipboard?.writeText(url).catch(() => {});
  location.hash = url.split('#')[1] || '';
  const note = includesWords
    ? 'Share link copied — it reproduces this exact set (words + settings + seed).'
    : 'Word list too long for the URL; link carries seed + settings only. ' +
      `Re-paste the same words. Seed ${run._last.seed}.`;
  showNotices([note], includesWords ? 'info' : 'warn');
}

function copySeed() {
  navigator.clipboard?.writeText(els.seed.value.trim()).catch(() => {});
}

function hydrateFromUrl() {
  const parsed = parseShareFragment(location.hash);
  if (!parsed) return false;
  if (parsed.seed) els.seed.value = parsed.seed;
  if (parsed.cardCount) els.cardCount.value = String(parsed.cardCount);
  if (parsed.words) {
    els.words.value = parsed.words.join('\n');
    return true; // enough to auto-generate
  }
  return false; // seed+settings only; user must paste words
}

els.generate.addEventListener('click', run);
els.print.addEventListener('click', () => window.print());
els.share.addEventListener('click', doShare);
els.copySeed.addEventListener('click', copySeed);

// On load: if a share link carried the words, reproduce immediately.
if (hydrateFromUrl()) {
  run();
}
