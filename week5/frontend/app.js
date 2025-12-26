let notesPage = 1;
let actionsPage = 1;
const PAGE_SIZE = 5;

async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  const json = await res.json();
  if (!res.ok || json.ok === false) {
    const message = json?.error?.message || JSON.stringify(json);
    throw new Error(message);
  }
  return json.data;
}

async function loadNotes() {
  const list = document.getElementById('notes');
  list.innerHTML = '';
  const result = await fetchJSON(`/notes/?page=${notesPage}&page_size=${PAGE_SIZE}`);
  const { items, total, page, page_size } = result;
  for (const n of items) {
    const li = document.createElement('li');
    li.textContent = `${n.title}: ${n.content}`;
    list.appendChild(li);
  }
  const info = document.getElementById('notes-page-info');
  const totalPages = total === 0 ? 1 : Math.ceil(total / page_size);
  info.textContent = `Page ${page} of ${totalPages}`;
  document.getElementById('notes-prev').disabled = page <= 1;
  document.getElementById('notes-next').disabled = page >= totalPages;
}

async function loadActions() {
  const list = document.getElementById('actions');
  list.innerHTML = '';
  const result = await fetchJSON(`/action-items/?page=${actionsPage}&page_size=${PAGE_SIZE}`);
  const { items, total, page, page_size } = result;
  for (const a of items) {
    const li = document.createElement('li');
    li.textContent = `${a.description} [${a.completed ? 'done' : 'open'}]`;
    if (!a.completed) {
      const btn = document.createElement('button');
      btn.textContent = 'Complete';
      btn.onclick = async () => {
        await fetchJSON(`/action-items/${a.id}/complete`, { method: 'PUT' });
        await loadActions();
      };
      li.appendChild(btn);
    }
    list.appendChild(li);
  }
  const info = document.getElementById('actions-page-info');
  const totalPages = total === 0 ? 1 : Math.ceil(total / page_size);
  info.textContent = `Page ${page} of ${totalPages}`;
  document.getElementById('actions-prev').disabled = page <= 1;
  document.getElementById('actions-next').disabled = page >= totalPages;
}

window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('note-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('note-title').value;
    const content = document.getElementById('note-content').value;
    const created = await fetchJSON('/notes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content }),
    });
    e.target.reset();
    const lastNoteEl = document.getElementById('last-note');
    lastNoteEl.textContent = `${created.title}: ${created.content}`;
    notesPage = 1;
    await loadNotes();
  });

  document.getElementById('action-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const description = document.getElementById('action-desc').value;
    const created = await fetchJSON('/action-items/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description }),
    });
    e.target.reset();
    const lastActionEl = document.getElementById('last-action');
    lastActionEl.textContent = `${created.description} [${created.completed ? 'done' : 'open'}]`;
    actionsPage = 1;
    await loadActions();
  });

  document.getElementById('notes-prev').addEventListener('click', async () => {
    if (notesPage > 1) {
      notesPage -= 1;
      await loadNotes();
    }
  });

  document.getElementById('notes-next').addEventListener('click', async () => {
    notesPage += 1;
    await loadNotes();
  });

  document.getElementById('actions-prev').addEventListener('click', async () => {
    if (actionsPage > 1) {
      actionsPage -= 1;
      await loadActions();
    }
  });

  document.getElementById('actions-next').addEventListener('click', async () => {
    actionsPage += 1;
    await loadActions();
  });

  loadNotes();
  loadActions();
});
