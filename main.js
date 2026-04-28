const { app, BrowserWindow, ipcMain, clipboard, globalShortcut, screen, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const { exec, spawn } = require('child_process');

// --- Paths ---
const VAULT_DIR = path.join(__dirname, 'vault');
const TREES_DIR = path.join(VAULT_DIR, 'trees');
const TREES_REGISTRY = path.join(VAULT_DIR, 'trees.json');
const TRASH_DIR = path.join(VAULT_DIR, '.trash');
const CONTEXT_FILE = path.join(VAULT_DIR, '.claude-context.md');

let treeWin = null;
let editorWin = null;
const PID_FILE = path.join(VAULT_DIR, '.pids');

// --- Registry Helpers ---

function readRegistry() {
  try { return JSON.parse(fs.readFileSync(TREES_REGISTRY, 'utf-8')); }
  catch { return { active: 'main', trees: [{ id: 'main', label: 'AI ERP' }] }; }
}

function saveRegistry(reg) {
  fs.writeFileSync(TREES_REGISTRY, JSON.stringify(reg, null, 2));
}

function getActiveTreeId() {
  return readRegistry().active;
}

function getActiveTreeDir() {
  return path.join(TREES_DIR, getActiveTreeId());
}

function getTreeFile() {
  return path.join(getActiveTreeDir(), 'tree.json');
}

function getNodesDir() {
  return path.join(getActiveTreeDir(), 'nodes');
}

function getHighlightsFile() {
  return path.join(getActiveTreeDir(), '.highlights.json');
}

// --- Marks State ---
// wordMarks: { [nodeId]: number[] } — indices of marked words per node
let wordMarks = {};

// --- Highlights State (Textmarker, persistent) ---
// wordHighlights: { [nodeId]: { normal: number[], heading: number[] } }
let wordHighlights = {};

function loadHighlights() {
  try {
    const f = getHighlightsFile();
    if (fs.existsSync(f)) {
      wordHighlights = JSON.parse(fs.readFileSync(f, 'utf-8'));
    } else {
      wordHighlights = {};
    }
  } catch { wordHighlights = {}; }
}

function saveHighlights() {
  try {
    fs.writeFileSync(getHighlightsFile(), JSON.stringify(wordHighlights, null, 2));
  } catch (e) {
    console.error('Highlights save failed:', e);
  }
  sendHighlightedNodes();
}

function sendHighlightedNodes() {
  const directIds = Object.keys(wordHighlights).filter(id => {
    const h = wordHighlights[id];
    return (h.normal && h.normal.length > 0) || (h.heading && h.heading.length > 0);
  });
  // Collect parent chain for each highlighted node
  const tree = readTree();
  const allIds = new Set(directIds);
  for (const id of directIds) {
    collectAncestors(tree.nodes, id, allIds);
  }
  if (treeWin && !treeWin.isDestroyed()) {
    treeWin.webContents.send('highlights:nodesUpdated', [...allIds]);
  }
}

function collectAncestors(nodes, targetId, result) {
  for (const node of nodes) {
    if (node.id === targetId) return true;
    if (node.children && node.children.length > 0) {
      if (collectAncestors(node.children, targetId, result)) {
        result.add(node.id);
        return true;
      }
    }
  }
  return false;
}

// --- Vault Initialization + Migration ---

function initVault() {
  if (!fs.existsSync(VAULT_DIR)) fs.mkdirSync(VAULT_DIR);

  // Check if migration needed (old flat structure → multi-tree)
  if (!fs.existsSync(TREES_REGISTRY)) {
    const oldTreeFile = path.join(VAULT_DIR, 'tree.json');
    const oldNodesDir = path.join(VAULT_DIR, 'nodes');
    const oldHighlights = path.join(VAULT_DIR, '.highlights.json');

    const mainDir = path.join(TREES_DIR, 'main');
    const mainNodes = path.join(mainDir, 'nodes');
    fs.mkdirSync(mainNodes, { recursive: true });

    // Migrate existing tree.json
    if (fs.existsSync(oldTreeFile)) {
      fs.copyFileSync(oldTreeFile, path.join(mainDir, 'tree.json'));
      fs.unlinkSync(oldTreeFile);
    } else {
      fs.writeFileSync(path.join(mainDir, 'tree.json'), JSON.stringify({ nodes: [] }, null, 2));
    }

    // Migrate existing nodes/
    if (fs.existsSync(oldNodesDir)) {
      const nodeFiles = fs.readdirSync(oldNodesDir);
      for (const f of nodeFiles) {
        fs.copyFileSync(path.join(oldNodesDir, f), path.join(mainNodes, f));
      }
      fs.rmSync(oldNodesDir, { recursive: true, force: true });
    }

    // Migrate existing .highlights.json
    if (fs.existsSync(oldHighlights)) {
      fs.copyFileSync(oldHighlights, path.join(mainDir, '.highlights.json'));
      fs.unlinkSync(oldHighlights);
    }

    // Create registry
    saveRegistry({ active: 'main', trees: [{ id: 'main', label: 'AI ERP' }] });
  }

  // Ensure active tree dir exists
  const activeDir = getActiveTreeDir();
  const activeNodes = path.join(activeDir, 'nodes');
  if (!fs.existsSync(activeDir)) fs.mkdirSync(activeDir, { recursive: true });
  if (!fs.existsSync(activeNodes)) fs.mkdirSync(activeNodes);
  if (!fs.existsSync(path.join(activeDir, 'tree.json'))) {
    fs.writeFileSync(path.join(activeDir, 'tree.json'), JSON.stringify({ nodes: [] }, null, 2));
  }
}

// --- Tree Helpers ---

function readTree() {
  try { return JSON.parse(fs.readFileSync(getTreeFile(), 'utf-8')); }
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
  const p = path.join(getNodesDir(), `${id}.md`);
  try { return fs.readFileSync(p, 'utf-8'); } catch { return ''; }
}

function tokenizeWords(text) {
  return text.match(/\S+/g) || [];
}

// --- Context Compilation ---

function compileAndSaveContext() {
  const tree = readTree();
  const allTitles = getAllTitles(tree.nodes);
  const activeTreeId = getActiveTreeId();

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
        lines.push(`Datei: \`vault/trees/${activeTreeId}/nodes/${nid}.md\`\n`);
        lines.push(content || '*(leer)*');
        lines.push('');
      }
    }

    lines.push('---');
    lines.push(`Bearbeite die markierten Inhalte. Dateien: vault/trees/${activeTreeId}/nodes/<id>.md, Struktur: vault/trees/${activeTreeId}/tree.json`);
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
      const normalized = filename.replace(/\\/g, '/');
      if (normalized.startsWith('.claude') || normalized === '.pids' || normalized === '.sub-context.md') return;
      if (normalized.endsWith('.highlights.json')) return;

      // Only react to changes in the active tree directory (or trees.json)
      const activePrefix = `trees/${getActiveTreeId()}/`;
      if (normalized !== 'trees.json' && !normalized.startsWith(activePrefix)) return;

      if (watchDebounce) clearTimeout(watchDebounce);
      watchDebounce = setTimeout(() => {
        // If a node .md file changed, invalidate its word marks
        const mdMatch = normalized.match(/nodes\/(.+)\.md$/);
        if (mdMatch) {
          const changedId = mdMatch[1];
          if (wordMarks[changedId]) {
            delete wordMarks[changedId];
            compileAndSaveContext();
          }
          if (wordHighlights[changedId]) {
            delete wordHighlights[changedId];
            saveHighlights();
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

function createTreeWindow(bounds) {
  treeWin = new BrowserWindow({
    ...bounds,
    frame: false, resizable: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true, nodeIntegration: false
    }
  });
  treeWin.loadFile('tree/index.html');
  treeWin.webContents.on('did-finish-load', () => sendHighlightedNodes());
  treeWin.on('closed', () => { treeWin = null; });
}

function createEditorWindow(bounds) {
  editorWin = new BrowserWindow({
    ...bounds,
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
  fs.writeFileSync(getTreeFile(), JSON.stringify(tree, null, 2));
  return true;
});

ipcMain.handle('vault:getNodeContent', (_e, id) => readNodeContent(id));

ipcMain.handle('vault:saveNodeContent', (_e, id, content) => {
  fs.writeFileSync(path.join(getNodesDir(), `${id}.md`), content);
  return true;
});

ipcMain.handle('vault:deleteNodeFile', (_e, id) => {
  const p = path.join(getNodesDir(), `${id}.md`);
  if (fs.existsSync(p)) fs.unlinkSync(p);
  if (wordMarks[id]) delete wordMarks[id];
  if (wordHighlights[id]) { delete wordHighlights[id]; saveHighlights(); }
  return true;
});

// Multi-tree management
ipcMain.handle('vault:getTrees', () => {
  const reg = readRegistry();
  return reg.trees;
});

ipcMain.handle('vault:getActiveTree', () => {
  return getActiveTreeId();
});

ipcMain.handle('vault:switchTree', (_e, id) => {
  const reg = readRegistry();
  if (!reg.trees.find(t => t.id === id)) return false;
  reg.active = id;
  saveRegistry(reg);

  // Reset in-memory state
  wordMarks = {};
  loadHighlights();

  // Notify windows
  if (treeWin && !treeWin.isDestroyed()) treeWin.webContents.send('vault:treeSwitched', id);
  if (editorWin && !editorWin.isDestroyed()) editorWin.webContents.send('vault:treeSwitched', id);

  return true;
});

ipcMain.handle('vault:createTree', (_e, label) => {
  const reg = readRegistry();
  const id = label.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || ('tree-' + Date.now());

  // Ensure unique ID
  let finalId = id;
  let counter = 2;
  while (reg.trees.find(t => t.id === finalId)) {
    finalId = `${id}-${counter++}`;
  }

  const treeDir = path.join(TREES_DIR, finalId);
  fs.mkdirSync(path.join(treeDir, 'nodes'), { recursive: true });
  fs.writeFileSync(path.join(treeDir, 'tree.json'), JSON.stringify({ nodes: [] }, null, 2));

  reg.trees.push({ id: finalId, label });
  saveRegistry(reg);

  return { id: finalId, label };
});

ipcMain.handle('vault:deleteTree', (_e, id) => {
  const reg = readRegistry();
  if (reg.active === id) return false; // Cannot delete active tree
  const treeEntry = reg.trees.find(t => t.id === id);
  if (!treeEntry) return false;

  const treeDir = path.join(TREES_DIR, id);
  if (fs.existsSync(treeDir)) {
    // Soft delete: move to .trash/ with timestamp
    fs.mkdirSync(TRASH_DIR, { recursive: true });
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const trashName = `${id}_${timestamp}`;
    const trashDest = path.join(TRASH_DIR, trashName);
    // Save metadata for potential recovery
    const meta = { id, label: treeEntry.label, deletedAt: new Date().toISOString() };
    fs.renameSync(treeDir, trashDest);
    fs.writeFileSync(path.join(trashDest, '.deleted-meta.json'), JSON.stringify(meta, null, 2));
  }

  reg.trees = reg.trees.filter(t => t.id !== id);
  saveRegistry(reg);

  return true;
});

ipcMain.handle('vault:renameTree', (_e, id, newLabel) => {
  const reg = readRegistry();
  const tree = reg.trees.find(t => t.id === id);
  if (!tree) return false;
  tree.label = newLabel;
  saveRegistry(reg);
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
  if (wordHighlights[nodeId]) { delete wordHighlights[nodeId]; saveHighlights(); }
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

// Highlights (Textmarker — persistent)
ipcMain.handle('highlights:setForNode', (_e, nodeId, data) => {
  const hasNormal = data.normal && data.normal.length > 0;
  const hasHeading = data.heading && data.heading.length > 0;
  if (hasNormal || hasHeading) {
    wordHighlights[nodeId] = {
      normal: data.normal || [],
      heading: data.heading || []
    };
  } else {
    delete wordHighlights[nodeId];
  }
  saveHighlights();
  return true;
});

ipcMain.handle('highlights:getForNode', (_e, nodeId) => {
  return wordHighlights[nodeId] || { normal: [], heading: [] };
});

ipcMain.handle('highlights:clearAllInNode', (_e, nodeId) => {
  if (wordHighlights[nodeId]) delete wordHighlights[nodeId];
  saveHighlights();
  return true;
});

// --- Claude PowerShell Management ---

function spawnClaude(isMain, bounds) {
  const projectDir = __dirname.replace(/\\/g, '/');
  const pidFilePath = PID_FILE.replace(/\\/g, '/');

  // Write positioning script if bounds provided
  let posCmd = '';
  if (bounds) {
    const posScript = path.join(app.getPath('temp'), 'lean-pos-console.ps1');
    fs.writeFileSync(posScript, [
      "try { Add-Type -TypeDefinition @'",
      'using System; using System.Runtime.InteropServices;',
      'public class ConsolePos {',
      '    [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint);',
      '    [DllImport("kernel32.dll")] public static extern IntPtr GetConsoleWindow();',
      '}',
      "'@ } catch {}",
      `[ConsolePos]::MoveWindow([ConsolePos]::GetConsoleWindow(), ${bounds.x}, ${bounds.y}, ${bounds.width}, ${bounds.height}, $true) | Out-Null`,
    ].join('\n'));
    posCmd = `. '${posScript.replace(/\\/g, '/')}'`;
  }

  let cmd;
  if (isMain) {
    cmd = [
      `cd '${projectDir}'`,
      posCmd,
      `Add-Content -Path '${pidFilePath}' -Value $PID`,
      "function sub { Write-Host 'Oeffne Sub-Claude...' -ForegroundColor Cyan; Start-Process pwsh '-NoExit','-Command',\"cd '" + projectDir + "'; Add-Content -Path '" + pidFilePath + "' -Value `$PID; claude --dangerously-skip-permissions\"; Write-Host 'Sub-Claude geoeffnet.' -ForegroundColor Green }",
      `Write-Host '--- LeanHierarchy Claude Code ---' -ForegroundColor Cyan`,
      `Write-Host 'Kontext: vault/.claude-context.md' -ForegroundColor DarkGray`,
      `Write-Host 'Funktion sub = weiteres Claude-Fenster' -ForegroundColor DarkGray`,
      `Write-Host ''`,
      `claude --dangerously-skip-permissions`
    ].filter(Boolean).join('; ');
  } else {
    cmd = [
      `cd '${projectDir}'`,
      posCmd,
      `Add-Content -Path '${pidFilePath}' -Value $PID`,
      `claude --dangerously-skip-permissions`
    ].filter(Boolean).join('; ');
  }

  exec(`start "" pwsh -NoExit -Command "${cmd}"`, { windowsHide: true });
}

// --- Sub-Claude with Context ---

const SESSIONS_DIR = path.join(require('os').homedir(), '.claude', 'projects', 'C--Projects-AI-ERP');

function getActiveSessions() {
  try {
    const files = fs.readdirSync(SESSIONS_DIR)
      .filter(f => f.endsWith('.jsonl'))
      .map(f => {
        const stat = fs.statSync(path.join(SESSIONS_DIR, f));
        return { file: f, id: f.replace('.jsonl', ''), mtime: stat.mtime, size: stat.size };
      })
      .sort((a, b) => b.mtime - a.mtime);

    // Only sessions modified in last 24h
    const cutoff = Date.now() - 24 * 60 * 60 * 1000;
    return files.filter(f => f.mtime.getTime() > cutoff);
  } catch { return []; }
}

function getSessionPreview(sessionId) {
  try {
    const lines = fs.readFileSync(path.join(SESSIONS_DIR, sessionId + '.jsonl'), 'utf-8').split('\n').filter(Boolean);
    let firstUserMsg = '';
    let msgCount = 0;
    for (const line of lines) {
      try {
        const obj = JSON.parse(line);
        if (obj.type === 'user' && obj.message && obj.message.content) {
          msgCount++;
          if (!firstUserMsg) firstUserMsg = String(obj.message.content).slice(0, 100);
        }
      } catch {}
    }
    return { firstMsg: firstUserMsg, msgCount };
  } catch { return { firstMsg: '?', msgCount: 0 }; }
}

function extractSessionSummary(sessionId) {
  try {
    const lines = fs.readFileSync(path.join(SESSIONS_DIR, sessionId + '.jsonl'), 'utf-8').split('\n').filter(Boolean);
    const messages = [];

    for (const line of lines) {
      try {
        const obj = JSON.parse(line);
        if (obj.type === 'user' && obj.message && obj.message.content) {
          const text = String(obj.message.content).slice(0, 500);
          if (text && text !== '[object Object]') {
            messages.push('USER: ' + text);
          }
        } else if (obj.message && obj.message.role === 'assistant' && Array.isArray(obj.message.content)) {
          for (const block of obj.message.content) {
            if (block.type === 'text' && block.text) {
              messages.push('CLAUDE: ' + block.text.slice(0, 800));
            }
          }
        }
      } catch {}
    }

    // Take last 30 messages max, trim to ~8000 chars total
    const recent = messages.slice(-30);
    let summary = '';
    for (const m of recent) {
      if (summary.length + m.length > 8000) break;
      summary += m + '\n\n';
    }
    return summary;
  } catch { return ''; }
}

function writeSubContext(sessionId) {
  const summary = extractSessionSummary(sessionId);
  const contextPath = path.join(VAULT_DIR, '.sub-context.md');
  const header = `# Kontext aus Haupt-Claude Session\nSession: ${sessionId}\nZeit: ${new Date().toISOString()}\n\n---\n\n`;
  fs.writeFileSync(contextPath, header + summary);
  return contextPath;
}

ipcMain.handle('claude:openSub', async () => {
  const sessions = getActiveSessions();

  if (sessions.length === 0) {
    spawnClaude(false);
    return true;
  }

  // Build session choices
  const choices = sessions.slice(0, 5).map(s => {
    const preview = getSessionPreview(s.id);
    const time = s.mtime.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' });
    const label = `[${time}] ${preview.firstMsg.slice(0, 60)}... (${preview.msgCount} msgs)`;
    return { id: s.id, label };
  });

  if (choices.length === 1) {
    // Only one session, use it directly
    writeSubContext(choices[0].id);
    spawnSubWithContext();
    return true;
  }

  // Show selection dialog
  const { response } = await dialog.showMessageBox(treeWin || editorWin, {
    type: 'question',
    title: 'Sub-Claude: Welches Fenster?',
    message: 'Kontext von welchem Claude-Fenster laden?',
    buttons: [...choices.map(c => c.label), 'Ohne Kontext'],
    defaultId: 0,
    cancelId: choices.length
  });

  if (response < choices.length) {
    writeSubContext(choices[response].id);
    spawnSubWithContext();
  } else {
    spawnClaude(false);
  }

  return true;
});

function spawnSubWithContext() {
  const projectDir = __dirname.replace(/\\/g, '/');
  const pidFilePath = PID_FILE.replace(/\\/g, '/');
  const contextPath = path.join(VAULT_DIR, '.sub-context.md');

  // Read the context file and pass as system prompt
  let contextContent = '';
  try { contextContent = fs.readFileSync(contextPath, 'utf-8'); } catch {}

  const systemPrompt = `Du bist ein Sub-Claude-Fenster. Du hast Kontext aus dem Haupt-Claude-Fenster erhalten. Fasse zu Beginn kurz (3-5 Saetze) zusammen woran das Haupt-Fenster arbeitet, und frage den Benutzer was er wissen oder tun moechte.\n\n${contextContent}`;

  // Write system prompt to temp file to avoid shell escaping issues
  const tmpFile = path.join(app.getPath('temp'), 'sub-claude-prompt.txt');
  fs.writeFileSync(tmpFile, systemPrompt);
  const tmpFilePath = tmpFile.replace(/\\/g, '/');

  const cmd = [
    `cd '${projectDir}'`,
    `Add-Content -Path '${pidFilePath}' -Value $PID`,
    `$sp = Get-Content '${tmpFilePath}' -Raw`,
    `claude --dangerously-skip-permissions --append-system-prompt $sp`
  ].join('; ');

  exec(`start "" pwsh -NoExit -Command "${cmd}"`, { windowsHide: true });
}

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

// --- Auto-Backup on Start ---

const BACKUP_TARGETS = [
  path.join(__dirname, '.backups'),
  'D:\\Projects_Backup\\AI-ERP',
  path.join(require('os').homedir(), 'iCloudDrive', 'AI-ERP-Backup')
];

const BACKUP_FILES = [
  'CLAUDE.md',
  'CHANGELOG.md',
  'main.js',
  'preload.js',
  'package.json',
  'start.ps1',
  'deploy.sh',
  'editor/editor.js',
  'editor/editor.css',
  'tree/tree.js',
  'tree/tree.css'
];

const MAX_BACKUPS = 10;

function copyDirRecursive(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      copyDirRecursive(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

function runBackup() {
  const now = new Date();
  const stamp = now.toISOString().replace(/T/, '_').replace(/:/g, '-').slice(0, 16);
  const srcDir = __dirname;

  for (const target of BACKUP_TARGETS) {
    try {
      // Check if target drive/path is accessible
      const targetRoot = path.parse(target).root;
      if (!fs.existsSync(targetRoot)) {
        console.log(`Backup skip: ${targetRoot} not available`);
        continue;
      }

      const backupDir = path.join(target, stamp);
      fs.mkdirSync(backupDir, { recursive: true });

      // Copy vault/ (critical)
      const vaultBackup = path.join(backupDir, 'vault');
      fs.mkdirSync(vaultBackup, { recursive: true });

      // vault root files
      for (const f of ['trees.json', '.claude-context.md']) {
        const src = path.join(VAULT_DIR, f);
        if (fs.existsSync(src)) fs.copyFileSync(src, path.join(vaultBackup, f));
      }

      // vault/trees/ (all trees recursively)
      if (fs.existsSync(TREES_DIR)) {
        copyDirRecursive(TREES_DIR, path.join(vaultBackup, 'trees'));
      }

      // Copy important files
      for (const relPath of BACKUP_FILES) {
        const src = path.join(srcDir, relPath);
        if (!fs.existsSync(src)) continue;
        const dest = path.join(backupDir, relPath);
        fs.mkdirSync(path.dirname(dest), { recursive: true });
        fs.copyFileSync(src, dest);
      }

      // Prune old backups (keep MAX_BACKUPS)
      try {
        const entries = fs.readdirSync(target)
          .filter(e => fs.statSync(path.join(target, e)).isDirectory())
          .sort()
          .reverse();
        for (let i = MAX_BACKUPS; i < entries.length; i++) {
          fs.rmSync(path.join(target, entries[i]), { recursive: true, force: true });
        }
      } catch {}

      console.log(`Backup OK: ${backupDir}`);
    } catch (e) {
      console.error(`Backup failed for ${target}:`, e.message);
    }
  }
}

// --- App Lifecycle ---

app.whenReady().then(() => {
  initVault();
  loadHighlights();
  runBackup();

  // Tiled layout based on screen work area
  const { workArea } = screen.getPrimaryDisplay();
  const treeW = Math.round(workArea.width * 0.18);
  const psH = Math.round(workArea.height * 0.35);

  createTreeWindow({
    x: workArea.x,
    y: workArea.y,
    width: treeW,
    height: workArea.height
  });

  createEditorWindow({
    x: workArea.x + treeW,
    y: workArea.y,
    width: workArea.width - treeW,
    height: workArea.height - psH
  });

  watchVault();

  spawnClaude(true, {
    x: workArea.x + treeW,
    y: workArea.y + workArea.height - psH,
    width: workArea.width - treeW,
    height: psH
  });

  // Global shortcut: Ctrl+Shift+Q = Quit All
  globalShortcut.register('Ctrl+Shift+Q', quitAll);
});

app.on('will-quit', () => {
  globalShortcut.unregisterAll();
});

app.on('window-all-closed', () => { quitAll(); });
