<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getAlerts } from '../api.js'

const router = useRouter()
const alerts = ref(null)
const loading = ref(false)
const error = ref(null)

onMounted(loadAlerts)

async function loadAlerts() {
  loading.value = true
  error.value = null
  try {
    alerts.value = await getAlerts()
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
    return new Date(dateStr).toLocaleDateString('en-US', {
      day: '2-digit', month: '2-digit', year: 'numeric',
    })
  } catch { return dateStr }
}

function formatAmount(amount, currency) {
  if (amount === null || amount === undefined) return '-'
  try {
    return new Intl.NumberFormat('en-US', {
      style: 'currency', currency: currency || 'USD',
    }).format(amount)
  } catch { return `${amount} ${currency || 'USD'}` }
}

function daysOverdue(paymentDue) {
  if (!paymentDue) return 0
  const due = new Date(paymentDue)
  const now = new Date()
  return Math.floor((now - due) / (1000 * 60 * 60 * 24))
}
</script>

<template>
  <div class="alert-view fade-in">
    <div class="page-header">
      <h1>Alerts</h1>
      <p class="text-muted">Invoices that need your attention</p>
    </div>

    <div v-if="loading" class="state">
      <span class="spinner"></span>
      <span>Loading...</span>
    </div>

    <div v-else-if="error" class="state state--error">
      <p>{{ error }}</p>
      <button class="btn btn-outline mt-2" @click="loadAlerts">Try again</button>
    </div>

    <div v-else-if="alerts">
      <!-- Overdue -->
      <div class="card">
        <div class="card-header">
          <h3>
            Overdue Payments
            <span v-if="alerts.overdue.length > 0" class="badge badge-danger" style="margin-left: 8px">
              {{ alerts.overdue.length }}
            </span>
          </h3>
          <button class="btn btn-outline" @click="loadAlerts">Refresh</button>
        </div>

        <div v-if="alerts.overdue.length === 0" class="card-body state">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="color: var(--success)">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
            <polyline points="22 4 12 14.01 9 11.01" />
          </svg>
          <p style="color: var(--success); font-weight: 500">All clear — no overdue invoices</p>
        </div>

        <div v-else class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Supplier</th>
                <th>Invoice No.</th>
                <th>Amount</th>
                <th>Due Date</th>
                <th>Days Overdue</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="inv in alerts.overdue"
                :key="inv.id"
                class="alert-row"
                @click="navigateToInvoice(inv.id)"
              >
                <td class="cell-supplier">{{ inv.supplier || 'Unknown' }}</td>
                <td>{{ inv.invoice_number || '-' }}</td>
                <td class="cell-amount">{{ formatAmount(inv.total_amount, inv.currency) }}</td>
                <td>{{ formatDate(inv.payment_due) }}</td>
                <td>
                  <span class="badge" :class="daysOverdue(inv.payment_due) > 14 ? 'badge-danger' : 'badge-warning'">
                    {{ daysOverdue(inv.payment_due) }} days
                  </span>
                </td>
                <td>
                  <span class="badge badge-warning">{{ inv.status }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-header { margin-bottom: 24px; }
.page-header h1 { margin-bottom: 4px; }

.state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 48px 24px;
  text-align: center;
  color: var(--text-secondary);
}
.state--error { color: var(--danger); }

.alert-row {
  cursor: pointer;
  transition: background 0.1s;
}
.alert-row:hover {
  background: var(--danger-light) !important;
}

.cell-supplier { font-weight: 500; }
.cell-amount { font-variant-numeric: tabular-nums; white-space: nowrap; }
</style>
