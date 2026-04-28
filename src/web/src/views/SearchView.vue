<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { searchInvoices } from '../api.js'

const router = useRouter()

// Search state
const query = ref('')
const supplier = ref('')
const status = ref('')
const dateFrom = ref('')
const dateTo = ref('')
const currency = ref('')

// Results state
const results = ref([])
const loading = ref(false)
const error = ref(null)
const searched = ref(false)

// Debounce timer
let debounceTimer = null

function debounceSearch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(doSearch, 300)
}

// Watch free-text input for live search
watch(query, debounceSearch)

async function doSearch() {
  loading.value = true
  error.value = null
  searched.value = true
  try {
    results.value = await searchInvoices({
      q: query.value || null,
      supplier: supplier.value || null,
      status: status.value || null,
      date_from: dateFrom.value || null,
      date_to: dateTo.value || null,
      currency: currency.value || null,
    })
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

function clearFilters() {
  query.value = ''
  supplier.value = ''
  status.value = ''
  dateFrom.value = ''
  dateTo.value = ''
  currency.value = ''
  results.value = []
  searched.value = false
}

function navigateToInvoice(id) {
  router.push(`/invoice/${id}`)
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    })
  } catch {
    return dateStr
  }
}

function formatAmount(amount, cur) {
  if (amount === null || amount === undefined) return '-'
  try {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: cur || 'USD',
    }).format(amount)
  } catch {
    return `${amount} ${cur || 'USD'}`
  }
}

function statusBadge(s) {
  switch (s) {
    case 'confirmed':
      return { label: 'Confirmed', class: 'badge-success' }
    case 'corrected':
      return { label: 'Corrected', class: 'badge-blue' }
    case 'extracted':
    default:
      return { label: 'Extracted', class: 'badge-warning' }
  }
}
</script>

<template>
  <div class="search-view fade-in">
    <div class="page-header">
      <h1>Search Invoices</h1>
      <p class="text-muted">Find invoices by keyword, supplier, date, or status</p>
    </div>

    <!-- Search Bar -->
    <div class="search-bar card">
      <div class="card-body">
        <div class="search-input-row">
          <div class="search-input-wrap">
            <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input
              v-model="query"
              type="text"
              class="form-input search-input"
              placeholder="Search by supplier, invoice number, or filename..."
              @keyup.enter="doSearch"
            />
          </div>
          <button class="btn btn-primary" @click="doSearch" :disabled="loading">
            Search
          </button>
        </div>

        <!-- Filters -->
        <div class="filters-row">
          <div class="filter-group">
            <label class="form-label">Supplier</label>
            <input
              v-model="supplier"
              type="text"
              class="form-input"
              placeholder="e.g. Shanghai Electronics"
            />
          </div>
          <div class="filter-group">
            <label class="form-label">Status</label>
            <select v-model="status" class="form-input">
              <option value="">All</option>
              <option value="extracted">Extracted</option>
              <option value="corrected">Corrected</option>
              <option value="confirmed">Confirmed</option>
            </select>
          </div>
          <div class="filter-group">
            <label class="form-label">Date from</label>
            <input v-model="dateFrom" type="date" class="form-input" />
          </div>
          <div class="filter-group">
            <label class="form-label">Date to</label>
            <input v-model="dateTo" type="date" class="form-input" />
          </div>
          <div class="filter-group">
            <label class="form-label">Currency</label>
            <input
              v-model="currency"
              type="text"
              class="form-input"
              placeholder="e.g. USD"
              maxlength="3"
            />
          </div>
          <div class="filter-actions">
            <button class="btn btn-outline" @click="clearFilters">Clear</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Results -->
    <div class="mt-4">
      <!-- Loading -->
      <div v-if="loading" class="results-state">
        <span class="spinner"></span>
        <span>Searching...</span>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="results-state results-state--error">
        <p>{{ error }}</p>
        <button class="btn btn-outline mt-2" @click="doSearch">Try again</button>
      </div>

      <!-- Results table -->
      <div v-else-if="results.length > 0" class="card">
        <div class="card-header">
          <h3>{{ results.length }} result{{ results.length !== 1 ? 's' : '' }}</h3>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Supplier</th>
                <th>Invoice No.</th>
                <th>Date</th>
                <th>Amount</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="invoice in results"
                :key="invoice.id"
                class="invoice-row"
                @click="navigateToInvoice(invoice.id)"
              >
                <td class="cell-supplier">{{ invoice.supplier || 'Unknown' }}</td>
                <td>{{ invoice.invoice_number || '-' }}</td>
                <td>{{ formatDate(invoice.invoice_date) }}</td>
                <td class="cell-amount">{{ formatAmount(invoice.total_amount, invoice.currency) }}</td>
                <td>
                  <span class="badge" :class="statusBadge(invoice.status).class">
                    {{ statusBadge(invoice.status).label }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- No results -->
      <div v-else-if="searched" class="results-state">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="color: var(--text-muted)">
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <p class="text-muted">No invoices match your search</p>
        <button class="btn btn-outline mt-2" @click="clearFilters">Clear filters</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  margin-bottom: 4px;
}

.search-input-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-input-wrap {
  flex: 1;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  pointer-events: none;
}

.search-input {
  padding-left: 40px;
}

.filters-row {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.filter-group {
  flex: 1;
  min-width: 140px;
}

.filter-actions {
  display: flex;
  align-items: flex-end;
  padding-bottom: 1px;
}

.results-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 48px 24px;
  text-align: center;
  color: var(--text-secondary);
}

.results-state--error {
  color: var(--danger);
}

.invoice-row {
  cursor: pointer;
  transition: background 0.1s ease;
}

.invoice-row:hover {
  background: var(--primary-light) !important;
}

.cell-supplier {
  font-weight: 500;
}

.cell-amount {
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

@media (max-width: 768px) {
  .filters-row {
    flex-direction: column;
  }

  .filter-group {
    min-width: 100%;
  }
}
</style>
