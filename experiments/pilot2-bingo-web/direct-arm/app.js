/*
 * app.js — DOM wiring for the bingo-card generator.
 * All generation logic lives in bingo.js; this file only reads the form,
 * calls Bingo.generateCards, and renders the result.
 */
(function () {
  'use strict';

  const $ = function (id) {
    return document.getElementById(id);
  };

  const els = {
    form: $('generator-form'),
    words: $('words'),
    wordCount: $('word-count'),
    gridSize: $('grid-size'),
    cardCount: $('card-count'),
    freeSpace: $('free-space'),
    seed: $('seed'),
    newSeed: $('new-seed'),
    cardTitle: $('card-title'),
    generate: $('generate'),
    print: $('print'),
    error: $('error'),
    meta: $('meta'),
    cards: $('cards'),
  };

  // --- Rendering ------------------------------------------------------------

  function renderCard(card, heading, seed, cardNumber) {
    const el = document.createElement('section');
    el.className = 'card';

    const title = document.createElement('h2');
    title.className = 'card__title';
    title.textContent = heading || '';
    if (heading) el.appendChild(title);

    const grid = document.createElement('div');
    grid.className = 'card__grid';
    grid.style.gridTemplateColumns = 'repeat(' + card.size + ', 1fr)';

    card.cells.forEach(function (cell) {
      const c = document.createElement('div');
      c.className = 'card__cell' + (cell.free ? ' card__cell--free' : '');
      c.textContent = cell.text;
      grid.appendChild(c);
    });
    el.appendChild(grid);

    const sub = document.createElement('p');
    sub.className = 'card__sub';
    sub.textContent =
      'Card ' + cardNumber + '  ·  seed ' + seed + '  ·  ' +
      card.size + 'x' + card.size;
    el.appendChild(sub);

    return el;
  }

  function renderResult(result, heading) {
    els.cards.innerHTML = '';
    result.cards.forEach(function (card, i) {
      els.cards.appendChild(renderCard(card, heading, result.seed, i + 1));
    });

    els.meta.innerHTML =
      'Generated <strong>' +
      result.cardCount +
      '</strong> card' +
      (result.cardCount === 1 ? '' : 's') +
      ' at <strong>' +
      result.gridSize +
      'x' +
      result.gridSize +
      '</strong>' +
      (result.freeSpace ? ' (free space)' : '') +
      '. Seed: <code>' +
      escapeHtml(result.seed) +
      '</code> — reuse the same words, settings and seed to reproduce this set.';
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
      }[c];
    });
  }

  // --- Form handling --------------------------------------------------------

  function readOptions() {
    return {
      seed: els.seed.value.trim(),
      gridSize: els.gridSize.value,
      cardCount: parseInt(els.cardCount.value, 10) || 1,
      freeSpace: els.freeSpace.checked,
    };
  }

  function updateWordCount() {
    const n = Bingo.parseWords(els.words.value).length;
    els.wordCount.textContent =
      n + ' distinct word' + (n === 1 ? '' : 's');
  }

  function generate() {
    els.error.textContent = '';
    const opts = readOptions();
    const result = Bingo.generateCards(els.words.value, opts);

    if (!result.ok) {
      els.error.textContent = result.error;
      els.cards.innerHTML = '';
      els.meta.innerHTML = '';
      els.print.disabled = true;
      return;
    }

    renderResult(result, els.cardTitle.value.trim());
    els.print.disabled = false;
  }

  // --- Wire up --------------------------------------------------------------

  els.form.addEventListener('submit', function (e) {
    e.preventDefault();
    generate();
  });

  els.words.addEventListener('input', updateWordCount);

  els.newSeed.addEventListener('click', function () {
    els.seed.value = Bingo.randomSeed();
  });

  els.print.addEventListener('click', function () {
    window.print();
  });

  // Initial state: a default seed and a small sample set so the tool is
  // immediately usable / demonstrable.
  els.seed.value = Bingo.randomSeed();
  els.words.value = [
    'apple', 'banana', 'cherry', 'date', 'elderberry',
    'fig', 'grape', 'honeydew', 'kiwi', 'lemon',
    'mango', 'nectarine', 'orange', 'papaya', 'quince',
    'raspberry', 'strawberry', 'tangerine', 'ugli', 'vanilla',
    'watermelon', 'xigua', 'yuzu', 'zucchini', 'apricot',
  ].join('\n');
  updateWordCount();
  generate();
})();
