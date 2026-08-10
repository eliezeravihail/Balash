const { BookingRegistry } = require('./balash-arm/src/registry');
const { BookingSystem } = require('./direct-arm/booking');
// A3: negative everyMinutes -> backwards series?
let b = new BookingRegistry();
const rb = b.bookSeries('A','x',100,160,-100,3,[]);
console.log('BALASH negative-stride series result:', rb === null ? 'REJECTED (null)'
  : 'ACCEPTED -> ' + rb.map(x => `[${x.start},${x.end})`).join(' '));
let d = new BookingSystem();
let dres;
try { dres = d.bookRecurring('A',100,160,'x',{everyMinutes:-100,count:3},[]); dres = (dres===null?'REJECTED (null)':'ACCEPTED '+JSON.stringify(dres)); }
catch(e){ dres = 'THREW '+e.constructor.name; }
console.log('DIRECT negative-stride series result:', dres);
// B2: capacity 0
try { d.setCapacity('Z',0); console.log('DIRECT setCapacity(0): accepted'); } catch(e){ console.log('DIRECT setCapacity(0): THREW '+e.constructor.name); }
b.setCapacity('Z',0); console.log('BALASH setCapacity(0): accepted; book 0 attendees ->', b.book('Z','x',0,10,[])!==null?'booked':'null', '; book 1 attendee ->', b.book('Z','y',20,30,['p'])!==null?'booked':'null');
