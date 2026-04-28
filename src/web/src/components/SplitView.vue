<script setup>
import PdfViewer from './PdfViewer.vue'
import InvoiceForm from './InvoiceForm.vue'

const props = defineProps({
  invoice: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['updated'])

function handleUpdated(updatedInvoice) {
  emit('updated', updatedInvoice)
}
</script>

<template>
  <div class="split-view">
    <div class="split-left">
      <PdfViewer :invoice-id="invoice.id" />
    </div>
    <div class="split-right">
      <InvoiceForm :invoice="invoice" @updated="handleUpdated" />
    </div>
  </div>
</template>

<style scoped>
.split-view {
  display: flex;
  gap: 20px;
  height: calc(100vh - 140px);
  min-height: 500px;
}

.split-left {
  flex: 1;
  min-width: 0;
}

.split-right {
  flex: 1;
  min-width: 0;
  overflow-y: auto;
}

@media (max-width: 1024px) {
  .split-view {
    flex-direction: column;
    height: auto;
  }

  .split-left {
    height: 500px;
  }

  .split-right {
    height: auto;
  }
}
</style>
