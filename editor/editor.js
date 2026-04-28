// --- State ---
let currentNodeId = null;
let currentTitle = '';
let markedIndices = new Set(); // word indices marked in current node
let hlNormal = new Set();  // normal highlights (yellow)
let hlHeading = new Set(); // heading highlights (yellow + underline)

// Textmarker drag state
let tmDragging = false;
let tmPending = false;
let tmStartX = 0;
let tmStartY = 0;
let tmShift = false; // true = heading mode
let lastHighlightedIdx = -1;
const TM_THRESHOLD = 5;

const placeholder = document.getElementById('placeholder');
const viewerContent = document.getElementById('viewer-content');
const titleEl = document.getElementById('node-title');
const contentEl = document.getElementById('node-content');
const toast = document.getElementById('context-toast');

// --- Display node content as clickable words ---

async function displayNode(nodeId, nodeTitle) {
  currentNodeId = nodeId;
  currentTitle = nodeTitle;
  titleEl.textContent = nodeTitle;

  const content = await window.api.getNodeContent(nodeId);
  const marks = await window.api.getMarksForNode(nodeId);
  markedIndices = new Set(marks);
  const hl = await window.api.getHighlightsForNode(nodeId);
  hlNormal = new Set(hl.normal || []);
  hlHeading = new Set(hl.heading || []);

  renderContent(content);

  placeholder.style.display = 'none';
  viewerContent.classList.remove('hidden');
}

function renderContent(text) {
  contentEl.innerHTML = '';
  if (!text) {
    contentEl.textContent = '(leer)';
    return;
  }

  // Tokenize: split into words and whitespace, preserving structure
  const tokens = text.match(/\S+|\s+/g) || [];
  let wordIndex = 0;

  tokens.forEach(token => {
    if (/^\s+$/.test(token)) {
      // Whitespace — insert as text node
      contentEl.appendChild(document.createTextNode(token));
    } else {
      // Word — create clickable span
      const span = document.createElement('span');
      span.className = 'word';
      span.textContent = token;
      span.dataset.index = wordIndex;

      if (markedIndices.has(wordIndex)) {
        span.classList.add('marked');
      }
      if (hlNormal.has(wordIndex)) {
        span.classList.add('highlighted');
      }
      if (hlHeading.has(wordIndex)) {
        span.classList.add('hl-heading');
      }

      // Left click → toggle mark
      span.addEventListener('click', (e) => {
        e.preventDefault();
        toggleMark(span, parseInt(span.dataset.index));
      });

      contentEl.appendChild(span);
      wordIndex++;
    }
  });
}

// --- Marking ---

async function toggleMark(span, index) {
  if (markedIndices.has(index)) {
    markedIndices.delete(index);
    span.classList.remove('marked');
  } else {
    markedIndices.add(index);
    span.classList.add('marked');
  }
  await window.api.toggleWord(currentNodeId, index);
}

async function removeMark(span, index) {
  markedIndices.delete(index);
  span.classList.remove('marked');
  await window.api.clearWord(currentNodeId, index);
}

// --- Textmarker: right-click drag to highlight ---

// Prevent native context menu on the content area
contentEl.addEventListener('contextmenu', (e) => {
  e.preventDefault();
});

// Right mouse down → start pending drag
contentEl.addEventListener('mousedown', (e) => {
  if (e.button !== 2) return;
  tmPending = true;
  tmDragging = false;
  tmShift = e.shiftKey;
  tmStartX = e.clientX;
  tmStartY = e.clientY;
  lastHighlightedIdx = -1;
});

// Mouse move → check threshold, highlight words
contentEl.addEventListener('mousemove', (e) => {
  if (!tmPending && !tmDragging) return;
  if (tmPending) {
    const dx = e.clientX - tmStartX;
    const dy = e.clientY - tmStartY;
    if (Math.abs(dx) < TM_THRESHOLD && Math.abs(dy) < TM_THRESHOLD) return;
    // Crossed threshold → start dragging
    tmPending = false;
    tmDragging = true;
    contentEl.classList.add('tm-dragging');
  }
  if (tmDragging) {
    const target = e.target.closest('.word');
    if (!target) return;
    const idx = parseInt(target.dataset.index);
    const set = tmShift ? hlHeading : hlNormal;
    const cls = tmShift ? 'hl-heading' : 'highlighted';
    if (set.has(idx)) return; // already highlighted
    // Fill gaps between last and current index
    if (lastHighlightedIdx >= 0 && Math.abs(idx - lastHighlightedIdx) > 1) {
      const lo = Math.min(lastHighlightedIdx, idx);
      const hi = Math.max(lastHighlightedIdx, idx);
      for (let i = lo; i <= hi; i++) {
        if (!set.has(i)) {
          set.add(i);
          const w = contentEl.querySelector(`.word[data-index="${i}"]`);
          if (w) w.classList.add(cls);
        }
      }
    } else {
      set.add(idx);
      target.classList.add(cls);
    }
    lastHighlightedIdx = idx;
  }
});

// Mouse up → finish drag or handle click
document.addEventListener('mouseup', async (e) => {
  if (e.button !== 2) return;
  if (!tmPending && !tmDragging) return;

  const wasDragging = tmDragging;
  tmPending = false;
  tmDragging = false;
  contentEl.classList.remove('tm-dragging');

  if (wasDragging) {
    // Save highlights after drag
    if (currentNodeId) {
      await saveHighlightsToMain();
    }
  } else {
    // Was a simple right-click (no drag)
    const target = e.target.closest('.word');
    if (e.ctrlKey) {
      // Ctrl+Right-click on highlighted/heading word → remove highlight
      if (target) {
        const idx = parseInt(target.dataset.index);
        let changed = false;
        if (hlHeading.has(idx)) {
          hlHeading.delete(idx);
          target.classList.remove('hl-heading');
          changed = true;
        }
        if (hlNormal.has(idx)) {
          hlNormal.delete(idx);
          target.classList.remove('highlighted');
          changed = true;
        }
        if (changed) await saveHighlightsToMain();
      } else {
        // Ctrl+Right-click on background → clear all highlights in node
        if (currentNodeId) {
          hlNormal.clear();
          hlHeading.clear();
          contentEl.querySelectorAll('.word.highlighted').forEach(el => el.classList.remove('highlighted'));
          contentEl.querySelectorAll('.word.hl-heading').forEach(el => el.classList.remove('hl-heading'));
          await window.api.clearHighlightsInNode(currentNodeId);
        }
      }
    } else {
      // Simple right-click → remove Claude mark (existing behavior)
      if (target) {
        const idx = parseInt(target.dataset.index);
        if (markedIndices.has(idx)) {
          removeMark(target, idx);
        }
      } else if (e.target === contentEl) {
        // Right-click on background → clear all marks in node
        clearAllMarksInNode();
      }
    }
  }
});

async function saveHighlightsToMain() {
  await window.api.setHighlightsForNode(currentNodeId, {
    normal: [...hlNormal],
    heading: [...hlHeading]
  });
}

async function clearAllMarksInNode() {
  if (!currentNodeId) return;
  markedIndices.clear();
  contentEl.querySelectorAll('.word.marked').forEach(el => el.classList.remove('marked'));
  await window.api.clearAllInNode(currentNodeId);
}

// Clear all marks button
document.getElementById('btn-clear-marks').addEventListener('click', async () => {
  markedIndices.clear();
  contentEl.querySelectorAll('.word.marked').forEach(el => el.classList.remove('marked'));
  await window.api.clearAllMarks();
});

// --- Toast ---

function showToast() {
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 1500);
}

// --- IPC listeners ---

window.api.onLoadNode((nodeId, nodeTitle) => {
  displayNode(nodeId, nodeTitle);
});

window.api.onNodeRenamed((nodeId, newTitle) => {
  if (nodeId === currentNodeId) {
    currentTitle = newTitle;
    titleEl.textContent = newTitle;
  }
});

window.api.onNodeDeleted((nodeId) => {
  if (nodeId === currentNodeId) {
    currentNodeId = null;
    viewerContent.classList.add('hidden');
    placeholder.style.display = 'flex';
  }
});

window.api.onContextCopied(() => {
  showToast();
});

// File watcher: reload current node content
window.api.onVaultRefresh(async () => {
  if (currentNodeId) {
    const content = await window.api.getNodeContent(currentNodeId);
    const marks = await window.api.getMarksForNode(currentNodeId);
    markedIndices = new Set(marks);
    const hl = await window.api.getHighlightsForNode(currentNodeId);
    hlNormal = new Set(hl.normal || []);
    hlHeading = new Set(hl.heading || []);
    renderContent(content);

    // Also refresh title from tree
    const tree = await window.api.getTree();
    const node = findInTree(tree.nodes, currentNodeId);
    if (node) {
      currentTitle = node.title;
      titleEl.textContent = node.title;
    }
  }
});

function findInTree(nodes, id) {
  for (const n of nodes) {
    if (n.id === id) return n;
    if (n.children) { const f = findInTree(n.children, id); if (f) return f; }
  }
  return null;
}

// --- Tree switched: clear current node ---
window.api.onTreeSwitched(() => {
  currentNodeId = null;
  currentTitle = '';
  markedIndices.clear();
  hlNormal.clear();
  hlHeading.clear();
  viewerContent.classList.add('hidden');
  placeholder.style.display = 'flex';
});

// --- Window controls ---
document.getElementById('btn-close').addEventListener('click', () => window.api.closeWindow());
document.getElementById('btn-quit').addEventListener('click', () => window.api.quitAll());
document.getElementById('btn-sub-claude').addEventListener('click', () => window.api.openSubClaude());
document.getElementById('btn-new-claude').addEventListener('click', () => window.api.openMainClaude());
