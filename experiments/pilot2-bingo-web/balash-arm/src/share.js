// Share links (edge) — round-trip the full reproducible state (words + settings
// + seed) through the URL so ONE link reproduces the exact CardSet. If the word
// list is too long for a sane URL, fall back to encoding seed + settings only
// (the seed is always shown and copyable for manual re-paste).

const MAX_URL_LENGTH = 1800; // conservative, well under common browser limits

// Unicode-safe base64 (btoa only handles Latin-1).
function b64encode(str) {
  const bytes = new TextEncoder().encode(str);
  let bin = '';
  for (const b of bytes) bin += String.fromCharCode(b);
  return btoa(bin).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function b64decode(b64) {
  const padded = b64.replace(/-/g, '+').replace(/_/g, '/');
  const bin = atob(padded);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return new TextDecoder().decode(bytes);
}

// Build a shareable URL. `words` is an array of cleaned words.
// Returns { url, includesWords }.
export function buildShareUrl(baseUrl, { words, cardCount, seed }) {
  const full = {
    v: 1,
    s: seed, // seed string
    n: cardCount,
    w: words,
  };
  const fullUrl = `${baseUrl}#d=${b64encode(JSON.stringify(full))}`;
  if (fullUrl.length <= MAX_URL_LENGTH) {
    return { url: fullUrl, includesWords: true };
  }
  // Fall back: seed + settings only.
  const lean = { v: 1, s: seed, n: cardCount };
  const leanUrl = `${baseUrl}#d=${b64encode(JSON.stringify(lean))}`;
  return { url: leanUrl, includesWords: false };
}

// Parse the fragment of the current URL. Returns null if none/invalid, else
// { seed, cardCount, words|null }.
export function parseShareFragment(hash) {
  const m = /(?:^#?|&)d=([^&]+)/.exec(hash || '');
  if (!m) return null;
  try {
    const data = JSON.parse(b64decode(m[1]));
    return {
      seed: typeof data.s === 'string' ? data.s : null,
      cardCount: Number.isInteger(data.n) ? data.n : null,
      words: Array.isArray(data.w) ? data.w : null,
    };
  } catch {
    return null;
  }
}
