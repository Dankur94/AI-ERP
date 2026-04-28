<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getInvoice } from '../api.js'
import SplitView from '../components/SplitView.vue'

const props = defineProps({
  id: {
    type: String,
    required: true,
  },
})

const router = useRouter()
const invoice = ref(null)
const loading = ref(true)
const error = ref(null)

async function loadInvoice() {
  loading.value = true
  error.value = null
  try {
    invoice.value = await getInvoice(props.id)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

function handleUpdated(updatedInvoice) {
  invoice.value = updatedInvoice
}

onMounted(loadInvoice)
</script>

<template>
  <div class="invoice-view fade-in">
    <!-- Back Navigation -->
    <div class="back-nav">
      <button class="btn btn-outline" @click="router.push('/')">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="15 18 9 12 15 6" />
        </svg>
        All Invoices
      </button>
      <span v-if="invoice" class="invoice-title">
        {{ invoice.supplier || 'Unknown Supplier' }}
        <span v-if="invoice.invoice_number" class="text-muted">&mdash; {{ invoice.invoice_number }}</span>
      </span>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="state-message">
      <span class="spinner"></span>
      <span>Loading invoice...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="state-message state-error">
      <p>{{ error }}</p>
      <button class="btn btn-outline mt-2" @click="loadInvoice">Try again</button>
    </div>

    <!-- Loaded -->
    <SplitView
      v-else-if="invoice"
      :invoice="invoice"
      @updated="handleUpdated"
    />
  </div>
</template>

<style scoped>
.back-nav {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.invoice-title {
  font-size: 16px;
  font-weight: 600;
}

.state-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 64px 24px;
  text-align: center;
  color: var(--text-secondary);
}

.state-error {
  color: var(--danger);
}
</style>
