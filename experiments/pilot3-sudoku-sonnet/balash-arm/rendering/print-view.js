// rendering/print-view.js
//
// DOM-aware. Walks a finished PuzzleBatch to build two printable
// sections: puzzle pages and answer-key pages. Only ever reads
// Puzzle.givens() / Puzzle.solution() (and PuzzleBatch's own fields) --
// it never imports domain/puzzle.js's Puzzle constructor path, so it has
// no way to construct or mutate a Puzzle. Whatever it renders is
// necessarily backed by an already-verified-unique Puzzle (D7).

import { SIZE } from '../domain/grid.js';

// Renders `batch` (a PuzzleBatch) into the given container elements.
// Clears each container first. Returns nothing; this is a side-effecting
// DOM operation by design (rendering is the one layer allowed to touch
// the DOM directly, per app/controller.js wiring it up).
export function renderBatch(batch, { puzzlesContainer, answersContainer }) {
  puzzlesContainer.replaceChildren();
  answersContainer.replaceChildren();

  batch.puzzles.forEach((puzzle, index) => {
    const label = `Puzzle ${index + 1} of ${batch.puzzles.length} — ${batch.difficulty.name}`;
    puzzlesContainer.appendChild(renderPage(label, puzzle.givens(), batch, index, false));
  });

  batch.puzzles.forEach((puzzle, index) => {
    const label = `Answer Key ${index + 1} of ${batch.puzzles.length} — ${batch.difficulty.name}`;
    answersContainer.appendChild(renderPage(label, puzzle.solution(), batch, index, true));
  });
}

function renderPage(label, grid, batch, index, isSolution) {
  const page = document.createElement('section');
  page.className = 'page';

  const heading = document.createElement('div');
  heading.className = 'page-heading';
  heading.textContent = label;
  page.appendChild(heading);

  page.appendChild(renderGridTable(grid, isSolution));
  page.appendChild(renderFooter(batch, index));

  return page;
}

function renderGridTable(grid, isSolution) {
  const table = document.createElement('table');
  table.className = 'sudoku-grid' + (isSolution ? ' sudoku-grid--solution' : '');

  for (let row = 0; row < SIZE; row++) {
    const tr = document.createElement('tr');
    for (let col = 0; col < SIZE; col++) {
      const pos = row * SIZE + col;
      const value = grid.cellAt(pos);
      const td = document.createElement('td');
      td.textContent = value === 0 ? '' : String(value);

      const classes = [];
      if (row % 3 === 0) classes.push('box-top');
      if (col % 3 === 0) classes.push('box-left');
      if (row === SIZE - 1) classes.push('box-bottom');
      if (col === SIZE - 1) classes.push('box-right');
      if (value !== 0) classes.push('filled');
      td.className = classes.join(' ');

      tr.appendChild(td);
    }
    table.appendChild(tr);
  }

  return table;
}

function renderFooter(batch, index) {
  const footer = document.createElement('div');
  footer.className = 'page-footer';
  footer.textContent =
    `Seed: ${batch.seed.identity()}  ·  Difficulty: ${batch.difficulty.name}  ·  ` +
    `Puzzle ${index + 1}/${batch.count}`;
  return footer;
}
