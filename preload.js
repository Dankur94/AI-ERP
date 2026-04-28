const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  // Vault
  getTree: () => ipcRenderer.invoke('vault:getTree'),
  saveTree: (tree) => ipcRenderer.invoke('vault:saveTree', tree),
  getNodeContent: (id) => ipcRenderer.invoke('vault:getNodeContent', id),
  saveNodeContent: (id, content) => ipcRenderer.invoke('vault:saveNodeContent', id, content),
  deleteNodeFile: (id) => ipcRenderer.invoke('vault:deleteNodeFile', id),

  // Tree → Editor relay
  selectNode: (nodeId, nodeTitle) => ipcRenderer.send('tree:nodeSelected', nodeId, nodeTitle),
  notifyNodeRenamed: (nodeId, newTitle) => ipcRenderer.send('tree:nodeRenamed', nodeId, newTitle),
  notifyNodeDeleted: (nodeId) => ipcRenderer.send('tree:nodeDeleted', nodeId),

  // Editor receives
  onLoadNode: (cb) => ipcRenderer.on('editor:loadNode', (_e, nodeId, nodeTitle) => cb(nodeId, nodeTitle)),
  onNodeRenamed: (cb) => ipcRenderer.on('editor:nodeRenamed', (_e, nodeId, newTitle) => cb(nodeId, newTitle)),
  onNodeDeleted: (cb) => ipcRenderer.on('editor:nodeDeleted', (_e, nodeId) => cb(nodeId)),

  // Marks
  toggleWord: (nodeId, wordIndex) => ipcRenderer.invoke('marks:toggleWord', nodeId, wordIndex),
  clearWord: (nodeId, wordIndex) => ipcRenderer.invoke('marks:clearWord', nodeId, wordIndex),
  clearAllInNode: (nodeId) => ipcRenderer.invoke('marks:clearAllInNode', nodeId),
  clearAllMarks: () => ipcRenderer.invoke('marks:clearAll'),
  getMarksForNode: (nodeId) => ipcRenderer.invoke('marks:getForNode', nodeId),

  // Highlights (Textmarker)
  setHighlightsForNode: (nodeId, indices) => ipcRenderer.invoke('highlights:setForNode', nodeId, indices),
  getHighlightsForNode: (nodeId) => ipcRenderer.invoke('highlights:getForNode', nodeId),
  clearHighlightsInNode: (nodeId) => ipcRenderer.invoke('highlights:clearAllInNode', nodeId),

  // Marks events
  onMarksUpdated: (cb) => ipcRenderer.on('marks:updated', (_e, state) => cb(state)),
  onContextCopied: (cb) => ipcRenderer.on('context:copied', () => cb()),

  // Highlight indicators (nodes with textmarker highlights)
  onHighlightedNodesUpdated: (cb) => ipcRenderer.on('highlights:nodesUpdated', (_e, ids) => cb(ids)),

  // Multi-tree
  getTrees: () => ipcRenderer.invoke('vault:getTrees'),
  getActiveTree: () => ipcRenderer.invoke('vault:getActiveTree'),
  switchTree: (id) => ipcRenderer.invoke('vault:switchTree', id),
  createTree: (label) => ipcRenderer.invoke('vault:createTree', label),
  deleteTree: (id) => ipcRenderer.invoke('vault:deleteTree', id),
  renameTree: (id, label) => ipcRenderer.invoke('vault:renameTree', id, label),
  onTreeSwitched: (cb) => ipcRenderer.on('vault:treeSwitched', (_e, id) => cb(id)),

  // File watcher refresh
  onVaultRefresh: (cb) => ipcRenderer.on('vault:refresh', () => cb()),

  // Claude windows
  openSubClaude: () => ipcRenderer.invoke('claude:openSub'),
  openMainClaude: () => ipcRenderer.invoke('claude:openMain'),

  // Window controls
  closeWindow: () => ipcRenderer.send('window:close'),
  minimizeWindow: () => ipcRenderer.send('window:minimize'),
  quitAll: () => ipcRenderer.send('app:quitAll')
});
