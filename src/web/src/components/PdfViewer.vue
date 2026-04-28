<script setup>
import { computed } from 'vue'
import { getPdfUrl } from '../api.js'

const props = defineProps({
  invoiceId: {
    type: [String, Number],
    required: true,
  },
})

const pdfSrc = computed(() => getPdfUrl(props.invoiceId))
</script>

<template>
  <div class="pdf-viewer card">
    <div class="card-header">
      <h3>PDF Preview</h3>
      <a :href="pdfSrc" target="_blank" class="btn btn-outline btn-sm">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
          <polyline points="15 3 21 3 21 9" />
          <line x1="10" y1="14" x2="21" y2="3" />
        </svg>
        Open in new tab
      </a>
    </div>
    <div class="pdf-frame-container">
      <object
        :data="pdfSrc"
        type="application/pdf"
        class="pdf-frame"
      >
        <div class="pdf-fallback">
          <p>PDF preview not available in this browser.</p>
          <a :href="pdfSrc" target="_blank" class="btn btn-primary">
            Open PDF
          </a>
        </div>
      </object>
    </div>
  </div>
</template>

<style scoped>
.pdf-viewer {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.pdf-frame-container {
  flex: 1;
  min-height: 500px;
}

.pdf-frame {
  width: 100%;
  height: 100%;
  min-height: 500px;
  border: none;
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
  background: var(--bg);
}

.pdf-fallback {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  height: 400px;
  color: var(--text-secondary);
}

.btn-sm {
  padding: 4px 10px;
  font-size: 13px;
}
</style>
