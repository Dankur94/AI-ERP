<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getInvoices } from '../api.js'

const router = useRouter()
const invoices = ref([])
const loading = ref(true)
const error = ref(null)

async function loadInvoices() {
  loading.value = true
  error.value = null
  try {
    invoices.value = await getInvoices()
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
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

function formatAmount(amount, currency) {
  if (amount === null || amount === undefined) return '-'
  try {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency || 'EUR',
    }).format(amount)
  } catch {
    return `${amount} ${currency || 'EUR'}`
  }
}

function statusBadge(status) {
  switch (status) {
    case 'confirmed':
      return { label: 'Confirmed', class: 'badge-success' }
    case 'corrected':
      return { label: 'Corrected', class: 'badge-blue' }
    case 'extracted':
    default:
      return { label: 'Extracted', class: 'badge-warning' }
  }
}

onMounted(loadInvoices)
</script>

<template>
  <div class="invoice-list card">
    <div class="card-header">
      <h3>Invoices</h3>
      <button class="btn btn-outline" @click="loadInvoices" :disabled="loading">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="23 4 23 10 17 10" />
          <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
        </svg>
        Refresh
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="list-state">
      <span class="spinner"></span>
      <span>Loading...</span>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="list-state list-state--error">
      <p>{{ error }}</p>
      <button class="btn btn-outline mt-2" @click="loadInvoices">Try again</button>
    </div>

    <!-- Empty -->
    <div v-else-if="invoices.length === 0" class="list-state">
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="color: var(--text-muted)">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14 2 14 8 20 8" />
      </svg>
      <p class="text-muted">No invoices yet</p>
      <p class="text-muted" style="font-size: 13px">Upload a PDF invoice to get started.</p>
    </div>

    <!-- Table -->
    <div v-else class="table-wrap">
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
            v-for="invoice in invoices"
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
</template>

<style scoped>
.list-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 48px 24px;
  text-align: center;
  color: var(--text-secondary);
}

.list-state--error {
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
</style>
