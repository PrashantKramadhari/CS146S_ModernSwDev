async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) {
    if (res.status === 204) return null; // No content for DELETE
    throw new Error(await res.text());
  }
  if (res.status === 204) return null; // No content for DELETE
  return res.json();
}

async function loadNotes(query = null) {
  const list = document.getElementById('notes');
  list.innerHTML = '';
  const url = query ? `/notes/search?q=${encodeURIComponent(query)}` : '/notes/';
  const notes = await fetchJSON(url);
  for (const n of notes) {
    const li = document.createElement('li');
    const span = document.createElement('span');
    span.textContent = `${n.title}: ${n.content}`;
    li.appendChild(span);

    // Edit button
    const editBtn = document.createElement('button');
    editBtn.textContent = 'Edit';
    editBtn.onclick = async () => {
      const newTitle = prompt('Enter new title:', n.title);
      const newContent = prompt('Enter new content:', n.content);
      if (newTitle && newContent) {
        await fetchJSON(`/notes/${n.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title: newTitle, content: newContent }),
        });
        loadNotes(query);
      }
    };
    li.appendChild(editBtn);

    // Delete button
    const delBtn = document.createElement('button');
    delBtn.textContent = 'Delete';
    delBtn.onclick = async () => {
      if (confirm('Are you sure you want to delete this note?')) {
        await fetchJSON(`/notes/${n.id}`, { method: 'DELETE' });
        loadNotes(query);
      }
    };
    li.appendChild(delBtn);

    list.appendChild(li);
  }
}

async function loadActions() {
  const list = document.getElementById('actions');
  list.innerHTML = '';
  const items = await fetchJSON('/action-items/');
  for (const a of items) {
    const li = document.createElement('li');
    const span = document.createElement('span');
    span.textContent = `${a.description} [${a.completed ? 'done' : 'open'}]`;
    li.appendChild(span);

    if (!a.completed) {
      const completeBtn = document.createElement('button');
      completeBtn.textContent = 'Complete';
      completeBtn.onclick = async () => {
        await fetchJSON(`/action-items/${a.id}/complete`, { method: 'PUT' });
        loadActions();
      };
      li.appendChild(completeBtn);
    }

    // Delete button
    const delBtn = document.createElement('button');
    delBtn.textContent = 'Delete';
    delBtn.onclick = async () => {
      if (confirm('Are you sure you want to delete this action item?')) {
        await fetchJSON(`/action-items/${a.id}`, { method: 'DELETE' });
        loadActions();
      }
    };
    li.appendChild(delBtn);

    list.appendChild(li);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('note-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('note-title').value;
    const content = document.getElementById('note-content').value;
    await fetchJSON('/notes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content }),
    });
    e.target.reset();
    loadNotes();
  });

  document.getElementById('action-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const description = document.getElementById('action-desc').value;
    await fetchJSON('/action-items/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description }),
    });
    e.target.reset();
    loadActions();
  });

  // Search functionality
  document.getElementById('search-btn').addEventListener('click', () => {
    const query = document.getElementById('search-input').value;
    loadNotes(query);
  });

  document.getElementById('clear-search-btn').addEventListener('click', () => {
    document.getElementById('search-input').value = '';
    loadNotes();
  });

  document.getElementById('search-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      const query = document.getElementById('search-input').value;
      loadNotes(query);
    }
  });

  loadNotes();
  loadActions();
});
