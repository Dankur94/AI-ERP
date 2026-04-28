// --- State ---
let treeData = { nodes: [] };
let selectedId = null;
let focusedId = null;
let collapsedSet = new Set();
let contextNodeIds = new Set(); // nodes in current context (from marks)
let highlightedNodeIds = new Set(); // nodes with textmarker highlights

const container = document.getElementById('tree-container');
const contextMenu = document.getElementById('context-menu');
const treeSelector = document.getElementById('tree-selector');

// --- Init ---
async function init() {
  await populateTreeSelector();
  treeData = await window.api.getTree();
  render();
}

// --- Tree Selector ---
async function populateTreeSelector() {
  const trees = await window.api.getTrees();
  const activeId = await window.api.getActiveTree();
  treeSelector.innerHTML = '';
  for (const t of trees) {
    const opt = document.createElement('option');
    opt.value = t.id;
    opt.textContent = t.label;
    if (t.id === activeId) opt.selected = true;
    treeSelector.appendChild(opt);
  }
}

treeSelector.addEventListener('change', async () => {
  await window.api.switchTree(treeSelector.value);
});

document.getElementById('btn-add-tree').addEventListener('click', async () => {
  const label = prompt('Name for new tree:');
  if (!label || !label.trim()) return;
  const result = await window.api.createTree(label.trim());
  if (result) {
    await populateTreeSelector();
    await window.api.switchTree(result.id);
  }
});

// Right-click on tree selector → rename/delete
treeSelector.addEventListener('contextmenu', (e) => {
  e.preventDefault();
  const activeId = treeSelector.value;
  const items = [
    { label: 'Rename Tree', action: () => renameCurrentTree(activeId) },
    { label: 'Delete Tree', action: () => deleteCurrentTree(activeId), disabled: treeSelector.options.length <= 1 },
  ];
  contextMenu.innerHTML = '';
  items.forEach(item => {
    const el = document.createElement('div');
    el.className = 'context-menu-item' + (item.disabled ? ' disabled' : '');
    el.textContent = item.label;
    if (!item.disabled) {
      el.addEventListener('click', () => { hideContextMenu(); item.action(); });
    }
    contextMenu.appendChild(el);
  });
  contextMenu.classList.remove('hidden');
  contextMenu.style.left = Math.min(e.clientX, window.innerWidth - 170) + 'px';
  contextMenu.style.top = Math.min(e.clientY, window.innerHeight - items.length * 30 - 10) + 'px';
});

async function renameCurrentTree(id) {
  const current = [...treeSelector.options].find(o => o.value === id);
  const newLabel = prompt('Rename tree:', current ? current.textContent : '');
  if (!newLabel || !newLabel.trim()) return;
  await window.api.renameTree(id, newLabel.trim());
  await populateTreeSelector();
}

async function deleteCurrentTree(id) {
  if (!confirm('Delete this tree and all its nodes?')) return;
  // Switch to another tree first
  const otherOpt = [...treeSelector.options].find(o => o.value !== id);
  if (!otherOpt) return;
  await window.api.switchTree(otherOpt.value);
  await window.api.deleteTree(id);
  await populateTreeSelector();
}

// --- Tree switched event ---
window.api.onTreeSwitched(async () => {
  selectedId = null;
  focusedId = null;
  collapsedSet.clear();
  contextNodeIds.clear();
  highlightedNodeIds.clear();
  treeData = await window.api.getTree();
  await populateTreeSelector();
  render();
});

// --- UUID ---
function uuid() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = Math.random() * 16 | 0;
    return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
  });
}

// --- Find node in tree ---
function findNode(nodes, id) {
  for (const node of nodes) {
    if (node.id === id) return node;
    if (node.children) {
      const found = findNode(node.children, id);
      if (found) return found;
    }
  }
  return null;
}

// --- Find parent array + index ---
function findParent(nodes, id, parent) {
  for (let i = 0; i < nodes.length; i++) {
    if (nodes[i].id === id) return { arr: nodes, index: i, parent };
    if (nodes[i].children) {
      const found = findParent(nodes[i].children, id, nodes[i]);
      if (found) return found;
    }
  }
  return null;
}

// --- Collect all descendant IDs ---
function collectIds(node) {
  let ids = [node.id];
  if (node.children) {
    for (const child of node.children) ids = ids.concat(collectIds(child));
  }
  return ids;
}

// --- Save tree ---
async function saveTree() {
  await window.api.saveTree(treeData);
}

// --- Get visible (flattened) nodes ---
function getVisibleNodes() {
  const result = [];
  function walk(nodes, prefix) {
    nodes.forEach((node, i) => {
      const num = prefix ? `${prefix}.${i + 1}` : `${i + 1}`;
      result.push({ node, num });
      if (node.children && node.children.length > 0 && !collapsedSet.has(node.id)) {
        walk(node.children, num);
      }
    });
  }
  walk(treeData.nodes, '');
  return result;
}

// --- Render ---
function render() {
  container.innerHTML = '';
  renderNodes(treeData.nodes, container, '');
}

function renderNodes(nodes, parentEl, prefix) {
  nodes.forEach((node, index) => {
    const num = prefix ? `${prefix}.${index + 1}` : `${index + 1}`;
    const depth = num.split('.').length;
    const hasChildren = node.children && node.children.length > 0;
    const isCollapsed = collapsedSet.has(node.id);

    const nodeEl = document.createElement('div');
    nodeEl.className = 'tree-node';
    nodeEl.dataset.id = node.id;

    const row = document.createElement('div');
    row.className = 'tree-row';
    if (node.id === selectedId) row.classList.add('selected');
    if (node.id === focusedId) row.classList.add('focused');
    if (contextNodeIds.has(node.id)) row.classList.add('in-context');

    // Chevron
    const chevron = document.createElement('span');
    chevron.className = 'chevron' + (hasChildren ? '' : ' invisible');
    chevron.textContent = hasChildren ? (isCollapsed ? '\u25B8' : '\u25BE') : '';
    chevron.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleCollapse(node.id);
    });

    // Number
    const numSpan = document.createElement('span');
    numSpan.className = 'node-number';
    numSpan.textContent = num;

    // Title
    const titleSpan = document.createElement('span');
    titleSpan.className = 'node-title';
    titleSpan.textContent = node.title;

    row.appendChild(chevron);
    row.appendChild(numSpan);

    // Yellow dot for nodes with textmarker highlights
    if (highlightedNodeIds.has(node.id)) {
      const dot = document.createElement('span');
      dot.className = 'highlight-dot';
      row.appendChild(dot);
    }

    row.appendChild(titleSpan);

    // Click → select + open in viewer
    row.addEventListener('click', () => selectNode(node.id));

    // Right-click → context menu
    row.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      e.stopPropagation();
      selectNode(node.id);
      showContextMenu(e.clientX, e.clientY, node.id, depth);
    });

    nodeEl.appendChild(row);

    if (hasChildren) {
      const childContainer = document.createElement('div');
      childContainer.className = 'tree-children' + (isCollapsed ? ' collapsed' : '');
      renderNodes(node.children, childContainer, num);
      nodeEl.appendChild(childContainer);
    }

    parentEl.appendChild(nodeEl);
  });
}

// --- Toggle collapse ---
function toggleCollapse(id) {
  if (collapsedSet.has(id)) collapsedSet.delete(id);
  else collapsedSet.add(id);
  render();
}

// --- Select node ---
function selectNode(id) {
  selectedId = id;
  focusedId = id;
  const node = findNode(treeData.nodes, id);
  if (node) window.api.selectNode(id, node.title);
  render();
  container.focus();
}

// --- Context menu ---
function showContextMenu(x, y, nodeId, depth) {
  const items = [
    { label: 'Add Child', action: () => addChild(nodeId), disabled: depth >= 4 },
    { label: 'Rename', action: () => startRename(nodeId) },
    { label: 'Delete', action: () => deleteNode(nodeId) },
    { label: 'Move Up', action: () => moveNode(nodeId, -1) },
    { label: 'Move Down', action: () => moveNode(nodeId, 1) },
  ];

  contextMenu.innerHTML = '';
  items.forEach(item => {
    const el = document.createElement('div');
    el.className = 'context-menu-item' + (item.disabled ? ' disabled' : '');
    el.textContent = item.label;
    if (!item.disabled) {
      el.addEventListener('click', () => { hideContextMenu(); item.action(); });
    }
    contextMenu.appendChild(el);
  });

  contextMenu.classList.remove('hidden');
  contextMenu.style.left = Math.min(x, window.innerWidth - 170) + 'px';
  contextMenu.style.top = Math.min(y, window.innerHeight - items.length * 30 - 10) + 'px';
}

function hideContextMenu() { contextMenu.classList.add('hidden'); }

document.addEventListener('click', hideContextMenu);
document.addEventListener('contextmenu', (e) => {
  if (!e.target.closest('.tree-row')) hideContextMenu();
});

// --- Add root node ---
document.getElementById('btn-add-root').addEventListener('click', async () => {
  const id = uuid();
  treeData.nodes.push({ id, title: 'New Node', children: [] });
  await saveTree();
  render();
  startRename(id);
});

// --- Add child ---
async function addChild(parentId) {
  const parent = findNode(treeData.nodes, parentId);
  if (!parent) return;
  if (!parent.children) parent.children = [];
  const id = uuid();
  parent.children.push({ id, title: 'New Node', children: [] });
  collapsedSet.delete(parentId);
  await saveTree();
  render();
  startRename(id);
}

// --- Rename ---
function startRename(nodeId) {
  const node = findNode(treeData.nodes, nodeId);
  if (!node) return;
  selectedId = nodeId;
  focusedId = nodeId;
  render();

  const rows = container.querySelectorAll('.tree-row');
  for (const row of rows) {
    const nodeEl = row.closest('.tree-node');
    if (nodeEl && nodeEl.dataset.id === nodeId) {
      const titleSpan = row.querySelector('.node-title');
      const input = document.createElement('input');
      input.type = 'text';
      input.className = 'rename-input';
      input.value = node.title;
      titleSpan.replaceWith(input);
      input.focus();
      input.select();

      const finish = async () => {
        const newTitle = input.value.trim() || node.title;
        node.title = newTitle;
        await saveTree();
        window.api.notifyNodeRenamed(nodeId, newTitle);
        render();
      };

      input.addEventListener('blur', finish);
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') input.blur();
        if (e.key === 'Escape') { input.value = node.title; input.blur(); }
      });
      break;
    }
  }
}

// --- Delete ---
async function deleteNode(nodeId) {
  const info = findParent(treeData.nodes, nodeId, null);
  if (!info) return;
  const node = info.arr[info.index];
  const ids = collectIds(node);
  for (const id of ids) await window.api.deleteNodeFile(id);
  info.arr.splice(info.index, 1);
  if (selectedId === nodeId || ids.includes(selectedId)) {
    selectedId = null;
    focusedId = null;
    window.api.notifyNodeDeleted(nodeId);
  }
  await saveTree();
  render();
}

// --- Move ---
async function moveNode(nodeId, direction) {
  const info = findParent(treeData.nodes, nodeId, null);
  if (!info) return;
  const newIndex = info.index + direction;
  if (newIndex < 0 || newIndex >= info.arr.length) return;
  [info.arr[info.index], info.arr[newIndex]] = [info.arr[newIndex], info.arr[info.index]];
  await saveTree();
  render();
}

// --- Keyboard Navigation ---
container.setAttribute('tabindex', '0');

document.addEventListener('keydown', (e) => {
  if (document.querySelector('.rename-input')) return;

  const visible = getVisibleNodes();
  if (visible.length === 0) return;
  let focusIdx = visible.findIndex(v => v.node.id === focusedId);

  switch (e.key) {
    case 'ArrowDown':
      e.preventDefault();
      if (focusIdx < visible.length - 1) { focusedId = visible[focusIdx + 1].node.id; render(); }
      break;
    case 'ArrowUp':
      e.preventDefault();
      if (focusIdx > 0) { focusedId = visible[focusIdx - 1].node.id; render(); }
      break;
    case 'ArrowRight':
      e.preventDefault();
      if (focusedId && collapsedSet.has(focusedId)) { collapsedSet.delete(focusedId); render(); }
      break;
    case 'ArrowLeft':
      e.preventDefault();
      if (focusedId) {
        const node = findNode(treeData.nodes, focusedId);
        if (node && node.children && node.children.length > 0 && !collapsedSet.has(focusedId)) {
          collapsedSet.add(focusedId);
          render();
        }
      }
      break;
    case 'Enter':
      e.preventDefault();
      if (focusedId) selectNode(focusedId);
      break;
    case 'F2':
      e.preventDefault();
      if (focusedId) startRename(focusedId);
      break;
  }
});

// --- Marks highlight from main process ---
window.api.onMarksUpdated((state) => {
  contextNodeIds = new Set(state.markedNodeIds || []);
  render();
});

// --- Highlight dots from main process ---
window.api.onHighlightedNodesUpdated((ids) => {
  highlightedNodeIds = new Set(ids || []);
  render();
});

// --- File watcher: reload tree ---
window.api.onVaultRefresh(async () => {
  treeData = await window.api.getTree();
  render();
});

// --- Window controls ---
document.getElementById('btn-close').addEventListener('click', () => window.api.closeWindow());
document.getElementById('btn-quit').addEventListener('click', () => window.api.quitAll());
document.getElementById('btn-sub-claude').addEventListener('click', () => window.api.openSubClaude());
document.getElementById('btn-new-claude').addEventListener('click', () => window.api.openMainClaude());

// --- Start ---
init();
