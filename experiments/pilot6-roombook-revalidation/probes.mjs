import { createRoomBook, InvalidRecurrenceError } from './balash-arm/roombook.js';

function assert(c, m){ if(!c){ console.log('FAIL:', m); process.exitCode=1;} else console.log('ok  :', m); }

// ---------- A1: cross-room promotion on a PERSON-freeing cancel (pilot#4's broken case) ----------
{
  const rb = createRoomBook();
  const idA = rb.book('A', 0, 60, 'alice', ['p1']);      // person p1 busy in room A
  const idB = rb.book('B', 0, 60, 'filler', []);          // occupy room B so a join is allowed
  rb.joinWaitlist('B', 0, 60, 'bob', ['p1']);             // bob waits for B, needs p1
  // cancel B's filler: room B interval frees, but bob still blocked by p1 in room A
  rb.cancel(idB);
  let bobIn = rb.schedule('B').some(x => x.organizer === 'bob');
  assert(!bobIn, 'A1a: bob NOT promoted while p1 still busy in room A (person rule holds)');
  // cancel A: frees the PERSON p1 -> bob must now promote into room B (cross-room reach)
  rb.cancel(idA);
  bobIn = rb.schedule('B').some(x => x.organizer === 'bob');
  assert(bobIn, 'A1b: cancel in room A (frees person p1) PROMOTES bob in room B  <-- pilot#4 broke this');
}

// ---------- A3: non-positive recurring stride rejected, nothing booked ----------
{
  const rb = createRoomBook();
  let threw = null;
  try { rb.bookRecurring('X', 100, 160, 'org', { everyMinutes:-100, count:3 }); }
  catch(e){ threw = e; }
  assert(threw instanceof InvalidRecurrenceError, 'A3a: negative stride throws InvalidRecurrenceError');
  assert(rb.schedule('X').length === 0, 'A3b: negative-stride series booked NOTHING (no backwards bookings)');
}

// ---------- A2: is there ANY way for a user to read the waitlist? ----------
{
  const rb = createRoomBook();
  const surface = Object.keys(rb).sort();
  console.log('    public instance surface:', surface.join(', '));
  const hasWaitlistRead = surface.some(k => /wait|queue|pending/i.test(k) && k !== 'joinWaitlist');
  assert(!hasWaitlistRead ? true : true, 'A2: (informational) waitlist-read affordance present? -> ' + (hasWaitlistRead ? 'YES' : 'NO'));
  console.log('    A2 VERDICT:', hasWaitlistRead ? 'affordance EXISTS' : 'NO waitlist-read affordance (a user cannot see who is queued)');
}
