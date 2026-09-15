const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('static/main.js', 'utf8');
function run(date, reduced = false) {
  const nodes = new Map();
  function element() { return {textContent:'', hidden:false, style:{}, children:[], classList:{remove(){},add(){}}, handlers:{}, addEventListener(name, fn){this.handlers[name]=fn;}, appendChild(el){this.children.push(el);}, replaceChildren(){this.children=[];}, querySelectorAll(){return this.children;}}; }
  const get = id => {if(!nodes.has(id)) nodes.set(id,element()); return nodes.get(id);};
  get('celebration').dataset={date};
  get('married').hidden=true;
  let interval;
  vm.runInNewContext(source, {window:{matchMedia:()=>({matches:reduced})}, document:{querySelector:s=>get(s.slice(1)), getElementById:get, querySelectorAll:()=>[], createElement:element}, Date, Math, Number, String, Object, setInterval:fn=>{interval=fn;return 1;}, clearInterval:()=>{interval=null;}});
  return {get,interval};
}
const pending=run('');
assert.equal(pending.interval,undefined);
assert.equal(pending.get('married').hidden,true);
const future=run(new Date(Date.now()+90061000).toISOString());
assert.equal(future.get('days').textContent,'01');
assert.equal(future.get('hours').textContent,'01');
assert.equal(future.get('minutes').textContent,'01');
const past=run('2020-01-01T00:00:00+05:30');
assert.equal(past.get('married').hidden,false);
assert.equal(past.get('countdown').hidden,true);
assert.equal(past.get('confetti').children.length,78);
const quiet=run('2020-01-01T00:00:00Z',true);
assert.equal(quiet.get('confetti').children.length,0);
quiet.get('new-wish').handlers.click();
assert.match(quiet.get('wish').textContent,/thousand lamps/);
console.log('Passed: pending, future, past, reduced motion, and blessing rotation.');
