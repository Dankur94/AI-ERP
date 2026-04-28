<script setup>
import { ref, onMounted } from 'vue'
import { getReportSummary, getExportCsvUrl } from '../api.js'

const report = ref(null)
const loading = ref(false)
const error = ref(null)
const dateFrom = ref('')
const dateTo = ref('')

onMounted(loadReport)

async function loadReport() {
  loading.value = true
  error.value = null
  try {
    report.value = await getReportSummary({
      date_from: dateFrom.value || undefined,
      date_to: dateTo.value || undefined,
    })
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

function downloadCsv() {
  const url = getExportCsvUrl({
    date_from: dateFrom.value || undefined,
    date_to: dateTo.value || undefined,
  })
  window.open(url, '_blank')
}

function formatAmount(amount) {
  if (amount === null || amount === undefined) return '-'
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount)
}

function statusBadge(status) {
  switch (status) {
    case 'confirmed': return { label: 'Confirmed', class: 'badge-success' }
    case 'corrected': return { label: 'Corrected', class: 'badge-blue' }
    case 'extracted':
    default: return { label: 'Extracted', class: 'badge-warning' }
  }
}
</script>

<template>
  <div class="report-view fade-in">
    <div class="page-header">
      <div>
        <h1>Reports</h1>
        <p class="text-muted">Invoice summary and data export</p>
      </div>
      <button class="btn btn-primary" @click="downloadCsv">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="7 10 12 15 17 10" />
          <line x1="12" y1="15" x2="12" y2="3" />
        </svg>
        Export CSV
      </button>
    </div>

    <!-- Date Filter -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="filter-row">
          <div class="filter-group">
            <label class="form-label">Date from</label>
            <input v-model="dateFrom" type="date" class="form-input" />
          </div>
          <div class="filter-group">
            <label class="form-label">Date to</label>
            <input v-model="dateTo" type="date" class="form-input" />
          </div>
          <div class="filter-actions">
            <button class="btn btn-outline" @click="loadReport" :disabled="loading">
              Apply
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="report-state">
      <span class="spinner"></span>
      <span>Loading report...</span>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="report-state report-state--error">
      <p>{{ error }}</p>
      <button class="btn btn-outline mt-2" @click="loadReport">Try again</button>
    </div>

    <!-- Report Content -->
    <div v-else-if="report">
      <!-- KPI Cards -->
      <div class="kpi-grid">
        <div class="kpi-card card">
          <div class="kpi-label">Total Invoices</div>
          <div class="kpi-value">{{ report.total_count }}</div>
        </div>
        <div class="kpi-card card">
          <div class="kpi-label">Total Amount</div>
          <div class="kpi-value">{{ formatAmount(report.total_amount) }}</div>
        </div>
        <div class="kpi-card card">
          <div class="kpi-label">Suppliers</div>
          <div class="kpi-value">{{ report.by_supplier.length }}</div>
        </div>
        <div class="kpi-card card">
          <div class="kpi-label">Currencies</div>
          <div class="kpi-value">{{ report.by_currency.length }}</div>
        </div>
      </div>

      <!-- By Status -->
      <div class="report-grid mt-4">
        <div class="card">
          <div class="card-header"><h3>By Status</h3></div>
          <div v-if="report.by_status.length === 0" class="card-body text-muted">No data</div>
          <div v-else class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Status</th>
                  <th>Count</th>
                  <th>Total</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in report.by_status" :key="row.status">
                  <td>
                    <span class="badge" :class="statusBadge(row.status).class">
                      {{ statusBadge(row.status).label }}
                    </span>
                  </td>
                  <td>{{ row.count }}</td>
                  <td class="cell-amount">{{ formatAmount(row.total) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="card">
          <div class="card-header"><h3>By Currency</h3></div>
          <div v-if="report.by_currency.length === 0" class="card-body text-muted">No data</div>
          <div v-else class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Currency</th>
                  <th>Count</th>
                  <th>Total</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in report.by_currency" :key="row.currency">
                  <td class="cell-currency">{{ row.currency }}</td>
                  <td>{{ row.count }}</td>
                  <td class="cell-amount">{{ formatAmount(row.total) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- By Supplier -->
      <div class="card mt-4">
        <div class="card-header"><h3>By Supplier</h3></div>
        <div v-if="report.by_supplier.length === 0" class="card-body text-muted">No data</div>
        <div v-else class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Supplier</th>
                <th>Invoices</th>
                <th>Total Amount</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in report.by_supplier" :key="row.supplier">
                <td class="cell-supplier">{{ row.supplier }}</td>
                <td>{{ row.count }}</td>
                <td class="cell-amount">{{ formatAmount(row.total) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-header {
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.page-header h1 { margin-bottom: 4px; }

.filter-row {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}
.filter-group { min-width: 160px; }
.filter-actions { padding-bottom: 1px; }

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.kpi-card {
  padding: 20px;
  text-align: center;
}
.kpi-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 4px;
}
.kpi-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}

.report-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.cell-supplier { font-weight: 500; }
.cell-amount { font-variant-numeric: tabular-nums; white-space: nowrap; text-align: right; }
.cell-currency { font-weight: 600; }

.report-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 48px 24px;
  text-align: center;
  color: var(--text-secondary);
}
.report-state--error { color: var(--danger); }

@media (max-width: 768px) {
  .page-header { flex-direction: column; gap: 12px; }
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .report-grid { grid-template-columns: 1fr; }
  .filter-row { flex-direction: column; }
}
</style>
