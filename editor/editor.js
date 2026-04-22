// --- State ---
let currentNodeId = null;
let currentTitle = '';
let markedIndices = new Set(); // word indices marked in current node

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

      // Left click → toggle mark
      span.addEventListener('click', (e) => {
        e.preventDefault();
        toggleMark(span, parseInt(span.dataset.index));
      });

      // Right click → remove mark
      span.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        if (markedIndices.has(parseInt(span.dataset.index))) {
          removeMark(span, parseInt(span.dataset.index));
        }
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

// Right-click on background → clear all marks in current node
contentEl.addEventListener('contextmenu', (e) => {
  if (e.target === contentEl) {
    e.preventDefault();
    clearAllMarksInNode();
  }
});

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

// --- Window controls ---
document.getElementById('btn-close').addEventListener('click', () => window.api.closeWindow());
document.getElementById('btn-quit').addEventListener('click', () => window.api.quitAll());
document.getElementById('btn-sub-claude').addEventListener('click', () => window.api.openSubClaude());
document.getElementById('btn-new-claude').addEventListener('click', () => window.api.openMainClaude());
