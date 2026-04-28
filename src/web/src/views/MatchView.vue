<script setup>
import { ref, onMounted } from 'vue'
import { getInvoices, createMatch, getMatches, getMatch, deleteMatch } from '../api.js'

// State
const invoices = ref([])
const matches = ref([])
const selectedA = ref('')
const selectedB = ref('')
const activeMatch = ref(null)
const loading = ref(false)
const matchLoading = ref(false)
const error = ref(null)

onMounted(async () => {
  await loadData()
})

async function loadData() {
  loading.value = true
  error.value = null
  try {
    const [inv, mat] = await Promise.all([getInvoices(), getMatches()])
    invoices.value = inv
    matches.value = mat
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

async function runMatch() {
  if (!selectedA.value || !selectedB.value) return
  if (selectedA.value === selectedB.value) {
    error.value = 'Cannot match an invoice with itself'
    return
  }

  matchLoading.value = true
  error.value = null
  try {
    const result = await createMatch(selectedA.value, selectedB.value)
    activeMatch.value = result
    matches.value = await getMatches()
    selectedA.value = ''
    selectedB.value = ''
  } catch (err) {
    error.value = err.message
  } finally {
    matchLoading.value = false
  }
}

async function viewMatch(id) {
  matchLoading.value = true
  error.value = null
  try {
    activeMatch.value = await getMatch(id)
  } catch (err) {
    error.value = err.message
  } finally {
    matchLoading.value = false
  }
}

async function removeMatch(id) {
  try {
    await deleteMatch(id)
    matches.value = await getMatches()
    if (activeMatch.value && activeMatch.value.id === id) {
      activeMatch.value = null
    }
  } catch (err) {
    error.value = err.message
  }
}

function closeDetail() {
  activeMatch.value = null
}

function invoiceLabel(inv) {
  const supplier = inv.supplier || 'Unknown'
  const num = inv.invoice_number || '-'
  return `${supplier} — ${num}`
}

function statusClass(status) {
  switch (status) {
    case 'match': return 'detail-match'
    case 'mismatch': return 'detail-mismatch'
    case 'missing_a': return 'detail-missing'
    case 'missing_b': return 'detail-missing'
    default: return ''
  }
}

function statusLabel(status) {
  switch (status) {
    case 'match': return 'Match'
    case 'mismatch': return 'Mismatch'
    case 'missing_a': return 'Missing in A'
    case 'missing_b': return 'Missing in B'
    default: return status
  }
}

function matchStatusBadge(status) {
  return status === 'matched'
    ? { label: 'Matched', class: 'badge-success' }
    : { label: 'Discrepancy', class: 'badge-danger' }
}
</script>

<template>
  <div class="match-view fade-in">
    <div class="page-header">
      <h1>Match Invoices</h1>
      <p class="text-muted">Compare two invoices and highlight discrepancies</p>
    </div>

    <!-- Error -->
    <div v-if="error" class="error-banner">
      {{ error }}
      <button class="btn-close" @click="error = null">&times;</button>
    </div>

    <!-- Create Match -->
    <div class="card mb-4">
      <div class="card-header">
        <h3>New Comparison</h3>
      </div>
      <div class="card-body">
        <div class="match-select-row">
          <div class="match-select-group">
            <label class="form-label">Invoice A</label>
            <select v-model="selectedA" class="form-input">
              <option value="">Select invoice...</option>
              <option v-for="inv in invoices" :key="inv.id" :value="inv.id">
                {{ invoiceLabel(inv) }}
              </option>
            </select>
          </div>
          <div class="match-vs">vs</div>
          <div class="match-select-group">
            <label class="form-label">Invoice B</label>
            <select v-model="selectedB" class="form-input">
              <option value="">Select invoice...</option>
              <option v-for="inv in invoices" :key="inv.id" :value="inv.id">
                {{ invoiceLabel(inv) }}
              </option>
            </select>
          </div>
          <button
            class="btn btn-primary"
            @click="runMatch"
            :disabled="!selectedA || !selectedB || matchLoading"
          >
            <span v-if="matchLoading" class="spinner"></span>
            Compare
          </button>
        </div>
      </div>
    </div>

    <!-- Match Detail -->
    <div v-if="activeMatch" class="card mb-4">
      <div class="card-header">
        <h3>
          Comparison Result
          <span class="badge" :class="matchStatusBadge(activeMatch.status).class" style="margin-left: 8px">
            {{ matchStatusBadge(activeMatch.status).label }}
          </span>
        </h3>
        <button class="btn btn-outline" @click="closeDetail">Close</button>
      </div>
      <div class="card-body">
        <div v-if="activeMatch.total_diff !== null && activeMatch.total_diff !== undefined" class="total-diff" :class="activeMatch.total_diff === 0 ? 'diff-zero' : 'diff-nonzero'">
          Total difference: {{ activeMatch.total_diff >= 0 ? '+' : '' }}{{ activeMatch.total_diff.toFixed(2) }}
        </div>
        <p v-if="activeMatch.notes" class="text-muted mb-4" style="font-size: 13px">{{ activeMatch.notes }}</p>

        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Field</th>
                <th>Invoice A</th>
                <th>Invoice B</th>
                <th>Result</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="detail in activeMatch.details"
                :key="detail.id"
                :class="statusClass(detail.status)"
              >
                <td class="cell-field">{{ detail.field_name }}</td>
                <td>{{ detail.value_a ?? '-' }}</td>
                <td>{{ detail.value_b ?? '-' }}</td>
                <td>
                  <span class="badge" :class="{
                    'badge-success': detail.status === 'match',
                    'badge-danger': detail.status === 'mismatch',
                    'badge-warning': detail.status === 'missing_a' || detail.status === 'missing_b',
                  }">
                    {{ statusLabel(detail.status) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Match History -->
    <div class="card">
      <div class="card-header">
        <h3>Match History</h3>
        <button class="btn btn-outline" @click="loadData" :disabled="loading">Refresh</button>
      </div>

      <div v-if="loading" class="list-state">
        <span class="spinner"></span>
        <span>Loading...</span>
      </div>

      <div v-else-if="matches.length === 0" class="list-state">
        <p class="text-muted">No matches yet. Select two invoices above to compare.</p>
      </div>

      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Invoice A</th>
              <th>Invoice B</th>
              <th>Result</th>
              <th>Diff</th>
              <th>Date</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="m in matches" :key="m.id" class="match-row" @click="viewMatch(m.id)">
              <td>{{ m.supplier_a || 'Unknown' }} ({{ m.invoice_number_a || '-' }})</td>
              <td>{{ m.supplier_b || 'Unknown' }} ({{ m.invoice_number_b || '-' }})</td>
              <td>
                <span class="badge" :class="matchStatusBadge(m.status).class">
                  {{ matchStatusBadge(m.status).label }}
                </span>
              </td>
              <td class="cell-amount">{{ m.total_diff !== null ? m.total_diff.toFixed(2) : '-' }}</td>
              <td>{{ m.created_at?.slice(0, 10) }}</td>
              <td>
                <button class="btn-icon" @click.stop="removeMatch(m.id)" title="Delete">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-header { margin-bottom: 24px; }
.page-header h1 { margin-bottom: 4px; }

.error-banner {
  background: var(--danger-light);
  color: var(--danger);
  padding: 12px 16px;
  border-radius: var(--radius);
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.btn-close {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: inherit;
}

.match-select-row {
  display: flex;
  gap: 16px;
  align-items: flex-end;
  flex-wrap: wrap;
}
.match-select-group { flex: 1; min-width: 200px; }
.match-vs {
  font-weight: 600;
  color: var(--text-muted);
  padding-bottom: 8px;
}

.total-diff {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
}
.diff-zero { background: var(--success-light); color: var(--success); }
.diff-nonzero { background: var(--danger-light); color: var(--danger); }

.detail-mismatch td { background: #fef2f2; }
.detail-missing td { background: #fffbeb; }

.cell-field { font-weight: 500; font-family: monospace; font-size: 13px; }
.cell-amount { font-variant-numeric: tabular-nums; white-space: nowrap; }

.match-row { cursor: pointer; transition: background 0.1s; }
.match-row:hover { background: var(--primary-light) !important; }

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: var(--text-muted);
  border-radius: 4px;
  transition: all 0.15s;
}
.btn-icon:hover { color: var(--danger); background: var(--danger-light); }

.list-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 48px 24px;
  text-align: center;
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .match-select-row { flex-direction: column; }
  .match-vs { text-align: center; padding: 0; }
}
</style>
