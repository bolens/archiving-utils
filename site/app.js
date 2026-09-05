'use strict';
const search = document.querySelector('#search');
const category = document.querySelector('#category');
const commands = [...document.querySelectorAll('.tool')];
function filter() {
  const query = search.value.trim().toLowerCase();
  let count = 0;
  for (const command of commands) {
    const match = command.dataset.search.toLowerCase().includes(query) &&
      (category.value === 'all' || command.dataset.category === category.value);
    command.hidden = !match;
    if (match) count++;
  }
  document.querySelector('#count').textContent = `${count} command${count === 1 ? '' : 's'}`;
  document.querySelector('#empty').hidden = count !== 0;
}
search.addEventListener('input', filter);
category.addEventListener('change', filter);
const theme = document.querySelector('#theme');
const key = document.title.split(' ')[0] + '-theme';
function setTheme(value) {
  document.body.dataset.theme = value;
  theme.textContent = value === 'dark' ? 'Light theme' : 'Dark theme';
  theme.setAttribute('aria-label', 'Switch to ' + (value === 'dark' ? 'light' : 'dark') + ' theme');
}
let saved;
try { saved = localStorage.getItem(key); } catch (_) { /* Storage is optional. */ }
setTheme(saved === 'light' || saved === 'dark' ? saved : document.body.classList.contains('video') ? 'dark' : 'light');
theme.addEventListener('click', () => {
  const next = document.body.dataset.theme === 'dark' ? 'light' : 'dark';
  setTheme(next);
  try { localStorage.setItem(key, next); } catch (_) { /* Theme still works without persistence. */ }
});
document.querySelector('#copy').addEventListener('click', async () => {
  const status = document.querySelector('#copy-status');
  try {
    await navigator.clipboard.writeText(document.querySelector('#command').textContent);
    status.textContent = 'Command copied. It previews the work without writing outputs.';
  } catch (_) {
    status.textContent = 'Copy unavailable. Select the command text and copy it manually.';
  }
});
