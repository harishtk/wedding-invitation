const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const wishes = [
  'May you walk together in friendship, grow together in wisdom, and find a home in each other’s hearts.',
  'May your home be filled with the warmth of love, the laughter of family, and the light of a thousand lamps.',
  'May each new morning bring you good fortune, kind words, and another reason to choose each other.',
  'May your bond grow stronger through every season, blessed with patience, harmony, and lasting joy.',
  'May the blessings of your elders and the affection of your loved ones accompany you always.',
];
let wishIndex = 0;
document.querySelector('#new-wish').addEventListener('click', () => {
  wishIndex = (wishIndex + 1) % wishes.length;
  document.querySelector('#wish').textContent = wishes[wishIndex];
});
document.querySelectorAll('.photo img').forEach(img => {
  const fallback = () => { img.hidden = true; img.nextElementSibling.hidden = false; };
  img.addEventListener('error', fallback);
  if (img.complete && !img.naturalWidth) fallback();
});
function celebrate() {
  if (reducedMotion.matches) return;
  const layer = document.querySelector('#confetti');
  layer.replaceChildren();
  for (let i = 0; i < 75; i++) {
    const piece = document.createElement('span');
    piece.className = 'confetti-piece';
    piece.style.cssText = `left:${Math.random()*100}%;background:${['#b48b46','#571b2b','#e1aa77','#bc6879'][i%4]};--duration:${3+Math.random()*3}s;animation-delay:${Math.random()}s;--drift:${Math.random()*200-100}px;--spin:${Math.random()*720}deg`;
    layer.appendChild(piece);
  }
  ['May love flourish', 'Joy & prosperity', 'A lifetime of togetherness'].forEach((text, i) => {
    const blessing = document.createElement('span');
    blessing.className = 'floating-blessing';
    blessing.textContent = text;
    blessing.style.cssText = `left:${5+i*25}%;animation-delay:${i*.5}s;--spin:0deg;--drift:0px`;
    layer.appendChild(blessing);
  });
  layer.querySelectorAll('span').forEach(el => el.addEventListener('animationend', () => el.remove(), { once: true }));
}
document.querySelector('#celebrate').addEventListener('click', celebrate);
const dateString = document.querySelector('#celebration').dataset.date;
const target = dateString ? Date.parse(dateString) : NaN;
let celebrationStarted = false;
function updateCountdown() {
  if (!Number.isFinite(target)) return;
  const remaining = target - Date.now();
  if (remaining <= 0) {
    document.querySelector('#countdown').hidden = true;
    document.querySelector('#married').hidden = false;
    document.querySelector('#countdown-heading').textContent = 'Let the blessings bloom.';
    document.querySelector('#date-message').textContent = 'Celebrating our sacred union, today and always.';
    if (!celebrationStarted) { celebrationStarted = true; celebrate(); }
    return;
  }
  const seconds = Math.floor(remaining / 1000);
  const values = {days: Math.floor(seconds/86400), hours: Math.floor(seconds/3600)%24, minutes: Math.floor(seconds/60)%60, seconds: seconds%60};
  Object.entries(values).forEach(([key,value]) => {
    const el = document.getElementById(key);
    const next = String(value).padStart(2, '0');
    if (el.textContent !== next) {
      el.textContent = next;
      el.classList.remove('tick');
      void el.offsetWidth;
      el.classList.add('tick');
    }
  });
}
updateCountdown();
if (Number.isFinite(target) && !celebrationStarted) {
  const timer = setInterval(() => {updateCountdown(); if (celebrationStarted) clearInterval(timer);}, 1000);
}
