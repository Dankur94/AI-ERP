const { app, BrowserWindow, ipcMain, clipboard, globalShortcut } = require('electron');
const path = require('path');
const fs = require('fs');
const { exec, spawn } = require('child_process');

const VAULT_DIR = path.join(__dirname, 'vault');
const NODES_DIR = path.join(VAULT_DIR, 'nodes');
const TREE_FILE = path.join(VAULT_DIR, 'tree.json');
const CONTEXT_FILE = path.join(VAULT_DIR, '.claude-context.md');

let treeWin = null;
let editorWin = null;
const PID_FILE = path.join(VAULT_DIR, '.pids');

// --- Marks State ---
// wordMarks: { [nodeId]: number[] } — indices of marked words per node
let wordMarks = {};

// --- Vault Initialization ---

function initVault() {
  if (!fs.existsSync(VAULT_DIR)) fs.mkdirSync(VAULT_DIR);
  if (!fs.existsSync(NODES_DIR)) fs.mkdirSync(NODES_DIR);
  if (!fs.existsSync(TREE_FILE)) {
    fs.writeFileSync(TREE_FILE, JSON.stringify({ nodes: [] }, null, 2));
  }
}

// --- Tree Helpers ---

function readTree() {
  try { return JSON.parse(fs.readFileSync(TREE_FILE, 'utf-8')); }
  catch { return { nodes: [] }; }
}

function findNodeById(nodes, id) {
  for (const n of nodes) {
    if (n.id === id) return n;
    if (n.children && n.children.length) {
      const f = findNodeById(n.children, id);
      if (f) return f;
    }
  }
  return null;
}

function collectDescendantIds(node) {
  let ids = [node.id];
  if (node.children) {
    for (const c of node.children) ids = ids.concat(collectDescendantIds(c));
  }
  return ids;
}

function getNodeNumbering(nodes, targetId, prefix) {
  for (let i = 0; i < nodes.length; i++) {
    const num = prefix ? `${prefix}.${i + 1}` : `${i + 1}`;
    if (nodes[i].id === targetId) return num;
    if (nodes[i].children) {
      const r = getNodeNumbering(nodes[i].children, targetId, num);
      if (r) return r;
    }
  }
  return null;
}

function getAllTitles(nodes) {
  let r = [];
  for (const n of nodes) {
    r.push({ id: n.id, title: n.title });
    if (n.children) r = r.concat(getAllTitles(n.children));
  }
  return r;
}

function readNodeContent(id) {
  const p = path.join(NODES_DIR, `${id}.md`);
  try { return fs.readFileSync(p, 'utf-8'); } catch { return ''; }
}

function tokenizeWords(text) {
  return text.match(/\S+/g) || [];
}

// --- Context Compilation ---

function compileAndSaveContext() {
  const tree = readTree();
  const allTitles = getAllTitles(tree.nodes);

  // Collect marked words and find matching branches
  const autoMarkedIds = new Set();
  const wordEntries = [];

  for (const [nodeId, indices] of Object.entries(wordMarks)) {
    if (!indices || indices.length === 0) continue;
    const content = readNodeContent(nodeId);
    const words = tokenizeWords(content);
    const node = findNodeById(tree.nodes, nodeId);
    const num = getNodeNumbering(tree.nodes, nodeId);

    for (const idx of indices) {
      const raw = words[idx];
      if (!raw) continue;
      const clean = raw.replace(/[^\w\-äöüÄÖÜß]/g, '');
      wordEntries.push(`- "${raw}" (in ${num || '?'} ${node ? node.title : '?'})`);

      // Check if word matches a node title → auto-include branch
      for (const t of allTitles) {
        if (t.title.toLowerCase() === clean.toLowerCase()) {
          const matched = findNodeById(tree.nodes, t.id);
          if (matched) {
            for (const did of collectDescendantIds(matched)) autoMarkedIds.add(did);
          }
        }
      }
    }
  }

  // Also include the nodes that have word marks
  for (const nodeId of Object.keys(wordMarks)) {
    if (wordMarks[nodeId] && wordMarks[nodeId].length > 0) {
      autoMarkedIds.add(nodeId);
    }
  }

  const lines = [];

  if (autoMarkedIds.size === 0 && wordEntries.length === 0) {
    lines.push('Keine Auswahl aktiv.');
  } else {
    lines.push('# Aktuelle Auswahl\n');

    if (wordEntries.length > 0) {
      lines.push('## Markierte Begriffe\n');
      lines.push(...wordEntries);
      lines.push('');
    }

    if (autoMarkedIds.size > 0) {
      lines.push('## Markierte Knoten und Inhalte\n');
      for (const nid of autoMarkedIds) {
        const node = findNodeById(tree.nodes, nid);
        const num = getNodeNumbering(tree.nodes, nid);
        if (!node) continue;
        const content = readNodeContent(nid);
        lines.push(`### ${num || '?'} ${node.title}`);
        lines.push(`Datei: \`vault/nodes/${nid}.md\`\n`);
        lines.push(content || '*(leer)*');
        lines.push('');
      }
    }

    lines.push('---');
    lines.push('Bearbeite die markierten Inhalte. Dateien: vault/nodes/<id>.md, Struktur: vault/tree.json');
  }

  const contextText = lines.join('\n');

  try {
    fs.writeFileSync(CONTEXT_FILE, contextText);
    clipboard.writeText(contextText);
  } catch (e) {
    console.error('Context save failed:', e);
  }

  // Send marks state to both windows
  const marksState = {
    markedNodeIds: [...autoMarkedIds],
    wordMarks: { ...wordMarks }
  };
  if (treeWin && !treeWin.isDestroyed()) treeWin.webContents.send('marks:updated', marksState);
  if (editorWin && !editorWin.isDestroyed()) {
    editorWin.webContents.send('marks:updated', marksState);
    editorWin.webContents.send('context:copied');
  }
}

// --- File Watcher ---

let watchDebounce = null;

function watchVault() {
  try {
    fs.watch(VAULT_DIR, { recursive: true }, (_event, filename) => {
      if (!filename) return;
      if (filename.startsWith('.claude')) return;
      if (watchDebounce) clearTimeout(watchDebounce);
      watchDebounce = setTimeout(() => {
        // If a node .md file changed, invalidate its word marks
        const mdMatch = filename.match(/nodes[/\\](.+)\.md$/);
        if (mdMatch) {
          const changedId = mdMatch[1];
          if (wordMarks[changedId]) {
            delete wordMarks[changedId];
            compileAndSaveContext();
          }
        }
        if (treeWin && !treeWin.isDestroyed()) treeWin.webContents.send('vault:refresh');
        if (editorWin && !editorWin.isDestroyed()) editorWin.webContents.send('vault:refresh');
      }, 300);
    });
  } catch (e) {
    console.error('File watcher failed:', e);
  }
}

// --- Window Creation ---

function createTreeWindow() {
  treeWin = new BrowserWindow({
    width: 400, height: 800, x: 100, y: 100,
    frame: false, resizable: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true, nodeIntegration: false
    }
  });
  treeWin.loadFile('tree/index.html');
  treeWin.on('closed', () => { treeWin = null; });
}

function createEditorWindow() {
  editorWin = new BrowserWindow({
    width: 900, height: 800, x: 520, y: 100,
    frame: false, resizable: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true, nodeIntegration: false
    }
  });
  editorWin.loadFile('editor/index.html');
  editorWin.on('closed', () => { editorWin = null; });
}

// --- IPC Handlers ---

// Vault
ipcMain.handle('vault:getTree', () => readTree());

ipcMain.handle('vault:saveTree', (_e, tree) => {
  fs.writeFileSync(TREE_FILE, JSON.stringify(tree, null, 2));
  return true;
});

ipcMain.handle('vault:getNodeContent', (_e, id) => readNodeContent(id));

ipcMain.handle('vault:saveNodeContent', (_e, id, content) => {
  fs.writeFileSync(path.join(NODES_DIR, `${id}.md`), content);
  return true;
});

ipcMain.handle('vault:deleteNodeFile', (_e, id) => {
  const p = path.join(NODES_DIR, `${id}.md`);
  if (fs.existsSync(p)) fs.unlinkSync(p);
  if (wordMarks[id]) delete wordMarks[id];
  return true;
});

// IPC relay: tree → editor
ipcMain.on('tree:nodeSelected', (_e, nodeId, nodeTitle) => {
  if (editorWin && !editorWin.isDestroyed()) {
    editorWin.webContents.send('editor:loadNode', nodeId, nodeTitle);
  }
});

ipcMain.on('tree:nodeRenamed', (_e, nodeId, newTitle) => {
  if (editorWin && !editorWin.isDestroyed()) {
    editorWin.webContents.send('editor:nodeRenamed', nodeId, newTitle);
  }
});

ipcMain.on('tree:nodeDeleted', (_e, nodeId) => {
  if (wordMarks[nodeId]) delete wordMarks[nodeId];
  if (editorWin && !editorWin.isDestroyed()) {
    editorWin.webContents.send('editor:nodeDeleted', nodeId);
  }
});

// Marks
ipcMain.handle('marks:toggleWord', (_e, nodeId, wordIndex) => {
  if (!wordMarks[nodeId]) wordMarks[nodeId] = [];
  const idx = wordMarks[nodeId].indexOf(wordIndex);
  if (idx === -1) {
    wordMarks[nodeId].push(wordIndex);
  } else {
    wordMarks[nodeId].splice(idx, 1);
  }
  compileAndSaveContext();
  return true;
});

ipcMain.handle('marks:clearWord', (_e, nodeId, wordIndex) => {
  if (wordMarks[nodeId]) {
    wordMarks[nodeId] = wordMarks[nodeId].filter(i => i !== wordIndex);
    if (wordMarks[nodeId].length === 0) delete wordMarks[nodeId];
  }
  compileAndSaveContext();
  return true;
});

ipcMain.handle('marks:clearAllInNode', (_e, nodeId) => {
  if (wordMarks[nodeId]) delete wordMarks[nodeId];
  compileAndSaveContext();
  return true;
});

ipcMain.handle('marks:clearAll', () => {
  wordMarks = {};
  compileAndSaveContext();
  return true;
});

ipcMain.handle('marks:getForNode', (_e, nodeId) => {
  return wordMarks[nodeId] || [];
});

// --- Claude PowerShell Management ---

function spawnClaude(isMain) {
  const projectDir = __dirname.replace(/\\/g, '/');
  const pidFilePath = PID_FILE.replace(/\\/g, '/');

  let cmd;
  if (isMain) {
    cmd = [
      `cd '${projectDir}'`,
      `Add-Content -Path '${pidFilePath}' -Value $PID`,
      "function sub { Write-Host 'Oeffne Sub-Claude...' -ForegroundColor Cyan; Start-Process pwsh '-NoExit','-Command',\"cd '" + projectDir + "'; Add-Content -Path '" + pidFilePath + "' -Value `$PID; claude --dangerously-skip-permissions\"; Write-Host 'Sub-Claude geoeffnet.' -ForegroundColor Green }",
      `Write-Host '--- LeanHierarchy Claude Code ---' -ForegroundColor Cyan`,
      `Write-Host 'Kontext: vault/.claude-context.md' -ForegroundColor DarkGray`,
      `Write-Host 'Funktion sub = weiteres Claude-Fenster' -ForegroundColor DarkGray`,
      `Write-Host ''`,
      `claude --dangerously-skip-permissions`
    ].join('; ');
  } else {
    cmd = `cd '${projectDir}'; Add-Content -Path '${pidFilePath}' -Value $PID; claude --dangerously-skip-permissions`;
  }

  exec(`start "" pwsh -NoExit -Command "${cmd}"`, { windowsHide: true });
}

ipcMain.handle('claude:openSub', () => {
  spawnClaude(false);
  return true;
});

ipcMain.handle('claude:openMain', () => {
  spawnClaude(true);
  return true;
});

// --- Quit All ---

function quitAll() {
  // Read tracked PIDs and kill process trees
  try {
    if (fs.existsSync(PID_FILE)) {
      const pids = fs.readFileSync(PID_FILE, 'utf-8').trim().split(/\r?\n/);
      for (const pid of pids) {
        if (pid.trim()) {
          try {
            exec(`taskkill /F /T /PID ${pid.trim()}`, { windowsHide: true });
          } catch {}
        }
      }
      fs.unlinkSync(PID_FILE);
    }
  } catch {}
  setTimeout(() => app.quit(), 300);
}

ipcMain.on('app:quitAll', () => quitAll());

// Window controls
ipcMain.on('window:close', (e) => {
  const win = BrowserWindow.fromWebContents(e.sender);
  if (win) win.close();
});

ipcMain.on('window:minimize', (e) => {
  const win = BrowserWindow.fromWebContents(e.sender);
  if (win) win.minimize();
});

// --- App Lifecycle ---

app.whenReady().then(() => {
  initVault();
  createTreeWindow();
  createEditorWindow();
  watchVault();
  spawnClaude(true);

  // Global shortcut: Ctrl+Shift+Q = Quit All
  globalShortcut.register('Ctrl+Shift+Q', quitAll);
});

app.on('will-quit', () => {
  globalShortcut.unregisterAll();
});

app.on('window-all-closed', () => { quitAll(); });
