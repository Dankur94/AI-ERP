<script setup>
import UploadZone from '../components/UploadZone.vue'
import InvoiceList from '../components/InvoiceList.vue'
import { ref } from 'vue'

const listKey = ref(0)

function onUploadComplete() {
  // Force InvoiceList to re-fetch by changing its key
  listKey.value++
}
</script>

<template>
  <div class="upload-view fade-in">
    <div class="page-header">
      <h1>Upload Invoices</h1>
      <p class="text-muted">Upload PDF invoices for automatic data extraction</p>
    </div>

    <UploadZone @upload-complete="onUploadComplete" />

    <div class="mt-6">
      <InvoiceList :key="listKey" />
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
</style>
