// Renderer (edge) — reads a CardSet and emits printable HTML (D7). It only READS
// the domain: it asks each Card to iterate its rows (tell-don't-ask) and never
// recomputes geometry. Page breaks and card sizing live in the print stylesheet,
// not here. Returns an HTML string, so it is also verifiable headlessly.

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// One card → a <section> whose grid columns come from the Card's own dimension.
function renderCard(card, index) {
  const dim = card.gridSize.dimension;
  let cells = '';
  for (const row of card.rows()) {
    for (const word of row) {
      cells += `<div class="bingo-cell"><span>${escapeHtml(word)}</span></div>`;
    }
  }
  return (
    `<section class="bingo-card" style="--dim:${dim}">` +
    `<header class="bingo-card__header">` +
    `<span class="bingo-card__title">BINGO</span>` +
    `<span class="bingo-card__num">Card ${index + 1}</span>` +
    `</header>` +
    `<div class="bingo-grid">${cells}</div>` +
    `</section>`
  );
}

// A whole CardSet → the printable region.
export function renderCardSetHtml(cardSet) {
  const cards = cardSet.cards.map((card, i) => renderCard(card, i)).join('');
  return `<div class="bingo-sheet">${cards}</div>`;
}
