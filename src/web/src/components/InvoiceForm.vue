<script setup>
import { ref, watch } from 'vue'
import { updateInvoice } from '../api.js'

const props = defineProps({
  invoice: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['updated'])

// Editable form state
const form = ref(createFormData(props.invoice))
const lineItems = ref(createLineItems(props.invoice))
const saving = ref(false)
const confirming = ref(false)
const saveMessage = ref(null)
const saveError = ref(null)

// Watch for external changes (e.g., after save returns updated data)
watch(() => props.invoice, (newVal) => {
  form.value = createFormData(newVal)
  lineItems.value = createLineItems(newVal)
}, { deep: true })

function createFormData(invoice) {
  return {
    supplier: invoice.supplier || '',
    invoice_number: invoice.invoice_number || '',
    invoice_date: invoice.invoice_date || '',
    currency: invoice.currency || 'EUR',
    total_amount: invoice.total_amount ?? '',
    payment_due: invoice.payment_due || '',
  }
}

function createLineItems(invoice) {
  if (!invoice.line_items || invoice.line_items.length === 0) return []
  return invoice.line_items.map(item => ({
    description: item.description || '',
    quantity: item.quantity ?? '',
    unit_price: item.unit_price ?? '',
    amount: item.amount ?? '',
  }))
}

// Field definitions with labels and confidence mappings
const fields = [
  { key: 'supplier', label: 'Supplier', type: 'text', confidenceKey: 'supplier_confidence' },
  { key: 'invoice_number', label: 'Invoice Number', type: 'text', confidenceKey: 'invoice_number_confidence' },
  { key: 'invoice_date', label: 'Date', type: 'date', confidenceKey: 'invoice_date_confidence' },
  { key: 'currency', label: 'Currency', type: 'text', confidenceKey: 'currency_confidence' },
  { key: 'total_amount', label: 'Total Amount', type: 'number', confidenceKey: 'total_amount_confidence' },
  { key: 'payment_due', label: 'Payment Due', type: 'date', confidenceKey: 'payment_due_confidence' },
]

function getConfidence(confidenceKey) {
  const value = props.invoice[confidenceKey]
  if (value === undefined || value === null) return null
  return value
}

function confidenceBadge(confidenceKey) {
  const value = getConfidence(confidenceKey)
  if (value === null) return null

  if (value >= 0.95) {
    return { label: 'Confident', class: 'badge-success' }
  } else if (value >= 0.80) {
    return { label: 'Review', class: 'badge-warning' }
  } else {
    return { label: 'Uncertain', class: 'badge-danger' }
  }
}

function confidencePercent(confidenceKey) {
  const value = getConfidence(confidenceKey)
  if (value === null) return ''
  return `${Math.round(value * 100)}%`
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

async function handleSave() {
  saving.value = true
  saveMessage.value = null
  saveError.value = null

  try {
    const payload = {
      ...form.value,
      total_amount: form.value.total_amount !== '' ? Number(form.value.total_amount) : null,
      line_items: lineItems.value.map(item => ({
        ...item,
        quantity: item.quantity !== '' ? Number(item.quantity) : null,
        unit_price: item.unit_price !== '' ? Number(item.unit_price) : null,
        amount: item.amount !== '' ? Number(item.amount) : null,
      })),
      status: 'corrected',
    }

    const result = await updateInvoice(props.invoice.id, payload)
    saveMessage.value = 'Changes saved.'
    emit('updated', result)
    clearMessageAfterDelay()
  } catch (err) {
    saveError.value = err.message
  } finally {
    saving.value = false
  }
}

async function handleConfirm() {
  confirming.value = true
  saveMessage.value = null
  saveError.value = null

  try {
    const payload = {
      ...form.value,
      total_amount: form.value.total_amount !== '' ? Number(form.value.total_amount) : null,
      line_items: lineItems.value.map(item => ({
        ...item,
        quantity: item.quantity !== '' ? Number(item.quantity) : null,
        unit_price: item.unit_price !== '' ? Number(item.unit_price) : null,
        amount: item.amount !== '' ? Number(item.amount) : null,
      })),
      status: 'confirmed',
    }

    const result = await updateInvoice(props.invoice.id, payload)
    saveMessage.value = 'Invoice confirmed.'
    emit('updated', result)
    clearMessageAfterDelay()
  } catch (err) {
    saveError.value = err.message
  } finally {
    confirming.value = false
  }
}

function clearMessageAfterDelay() {
  setTimeout(() => {
    saveMessage.value = null
  }, 3000)
}
</script>

<template>
  <div class="invoice-form card">
    <div class="card-header">
      <h3>Invoice Data</h3>
      <span class="badge" :class="statusBadge(invoice.status).class">
        {{ statusBadge(invoice.status).label }}
      </span>
    </div>

    <div class="card-body">
      <!-- Invoice Fields -->
      <div class="fields-grid">
        <div v-for="field in fields" :key="field.key" class="form-group">
          <label class="form-label">
            {{ field.label }}
            <span
              v-if="confidenceBadge(field.confidenceKey)"
              class="badge badge-sm"
              :class="confidenceBadge(field.confidenceKey).class"
              :title="'Confidence: ' + confidencePercent(field.confidenceKey)"
            >
              {{ confidenceBadge(field.confidenceKey).label }}
              {{ confidencePercent(field.confidenceKey) }}
            </span>
          </label>
          <input
            v-model="form[field.key]"
            :type="field.type"
            class="form-input"
            :step="field.type === 'number' ? '0.01' : undefined"
          />
        </div>
      </div>

      <!-- Line Items -->
      <div v-if="lineItems.length > 0" class="line-items-section">
        <h3 class="section-title">Line Items</h3>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th style="width: 50%">Description</th>
                <th style="width: 12%">Quantity</th>
                <th style="width: 18%">Unit Price</th>
                <th style="width: 20%">Amount</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in lineItems" :key="index">
                <td>
                  <input
                    v-model="item.description"
                    type="text"
                    class="form-input form-input--table"
                  />
                </td>
                <td>
                  <input
                    v-model="item.quantity"
                    type="number"
                    step="0.01"
                    class="form-input form-input--table"
                  />
                </td>
                <td>
                  <input
                    v-model="item.unit_price"
                    type="number"
                    step="0.01"
                    class="form-input form-input--table"
                  />
                </td>
                <td>
                  <input
                    v-model="item.amount"
                    type="number"
                    step="0.01"
                    class="form-input form-input--table"
                  />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-else class="no-line-items text-muted text-center mt-4">
        No line items detected.
      </div>

      <!-- Action Buttons -->
      <div class="form-actions">
        <button
          class="btn btn-primary"
          :disabled="saving || confirming"
          @click="handleSave"
        >
          <span v-if="saving" class="spinner"></span>
          <span v-else>Save</span>
        </button>
        <button
          class="btn btn-success"
          :disabled="saving || confirming"
          @click="handleConfirm"
        >
          <span v-if="confirming" class="spinner"></span>
          <span v-else>Confirm</span>
        </button>
      </div>

      <!-- Messages -->
      <div v-if="saveMessage" class="form-message form-message--success fade-in">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="20 6 9 17 4 12" />
        </svg>
        {{ saveMessage }}
      </div>
      <div v-if="saveError" class="form-message form-message--error fade-in">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10" />
          <line x1="15" y1="9" x2="9" y2="15" />
          <line x1="9" y1="9" x2="15" y2="15" />
        </svg>
        {{ saveError }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.invoice-form {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.invoice-form .card-body {
  flex: 1;
  overflow-y: auto;
}

.fields-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0 20px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.badge-sm {
  font-size: 11px;
  padding: 1px 6px;
}

.section-title {
  margin-top: 24px;
  margin-bottom: 12px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.form-input--table {
  padding: 6px 8px;
  font-size: 13px;
}

.no-line-items {
  padding: 24px;
  font-size: 14px;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.form-message {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 10px 16px;
  border-radius: var(--radius-sm);
  font-size: 14px;
}

.form-message--success {
  background: var(--success-light);
  color: var(--success);
}

.form-message--error {
  background: var(--danger-light);
  color: var(--danger);
}

@media (max-width: 640px) {
  .fields-grid {
    grid-template-columns: 1fr;
  }
}
</style>
