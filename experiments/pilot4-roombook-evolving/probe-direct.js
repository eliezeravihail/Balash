const { BookingSystem } = require('./direct-arm/booking');
let s = new BookingSystem();
s.book('A', 10, 20, 'org', ['P']);
console.log('DIRECT person-overlap single rejected:', s.book('B', 15, 25, 'org', ['P']) === null);
s.setCapacity('C', 2);
console.log('DIRECT capacity reject :', s.book('C', 0, 10, 'o', ['x','y','z']) === null);
console.log('DIRECT capacity accept :', typeof s.book('C', 0, 10, 'o', ['x','y']) === 'number');
// cross-room promotion: person P freed in room A should promote the room-B entry waiting on P
let t = new BookingSystem();
const a = t.book('A', 10, 20, 'o', ['P']);
const w = t.bookOrWaitlist('B', 10, 20, 'o', ['P']);
console.log('DIRECT B waitlisted      :', w.status === 'waitlisted');
t.cancel(a);
const b = t.schedule('B');
console.log('DIRECT cross-room PROMOTED:', b.length === 1 && b[0].start === 10);
