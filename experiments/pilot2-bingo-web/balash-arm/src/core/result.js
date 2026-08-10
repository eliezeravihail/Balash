// Result<T, E> — typed outcomes so no raw exceptions cross the core seam (D6).
// A Result is either { ok: true, value } or { ok: false, error }.

export function ok(value) {
  return { ok: true, value };
}

export function err(error) {
  return { ok: false, error };
}

export function isOk(result) {
  return result != null && result.ok === true;
}
