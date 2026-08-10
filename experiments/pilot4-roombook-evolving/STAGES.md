# RoomBook — staged product spec (master, orchestrator-only)

Pure Node.js, in-memory, zero external deps. Ship `node --test` tests each stage.
Time = integer minutes. Intervals are half-open [start,end): [10,20) and [20,30) do NOT conflict.

## Stage 1 — Booking + same-room conflict rejection
- book(room, start, end, organizer) -> booking id on success; rejected if it overlaps an existing booking in the SAME room.
- schedule(room) -> that room's bookings ordered by start.

## Stage 2 — Recurring series + cancel
- bookRecurring(room, start, end, organizer, {everyMinutes, count}) -> creates `count` occurrences.
  ALL-OR-NOTHING: if ANY occurrence conflicts, the whole series is rejected and nothing is booked.
- cancel(bookingId) -> removes a booking.

## Stage 3 — Waitlist with auto-promotion
- If a booking request conflicts, the requester may instead JOIN A WAITLIST for that room+interval.
- When a booking is cancelled and frees an interval, the earliest-queued compatible waitlist entry is
  AUTOMATICALLY promoted into a real booking.

## Stage 4 — Two stressors
- (a) Capacity: a room has a capacity; a booking carries an attendee COUNT; reject if attendees > capacity.
- (b) NEW INVARIANT: a booking carries an attendee LIST (person ids). A person cannot be in two
  overlapping meetings: reject a booking if ANY attendee already has an overlapping booking in ANY room.
