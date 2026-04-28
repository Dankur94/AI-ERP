<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { uploadInvoice } from '../api.js'

const emit = defineEmits(['upload-complete'])
const router = useRouter()

const isDragging = ref(false)
const uploading = ref(false)
const uploadQueue = ref([])
const currentFile = ref(null)
const uploadError = ref(null)
const uploadSuccess = ref(null)

const fileInput = ref(null)

function openFilePicker() {
  if (uploading.value) return
  fileInput.value?.click()
}

function handleFileSelect(event) {
  const files = Array.from(event.target.files || [])
  processFiles(files)
  // Reset input so the same file can be selected again
  event.target.value = ''
}

function handleDragOver(event) {
  event.preventDefault()
  isDragging.value = true
}

function handleDragLeave() {
  isDragging.value = false
}

function handleDrop(event) {
  event.preventDefault()
  isDragging.value = false
  const files = Array.from(event.dataTransfer.files || [])
  processFiles(files)
}

function processFiles(files) {
  const pdfFiles = files.filter(f => f.type === 'application/pdf' || f.name.toLowerCase().endsWith('.pdf'))

  if (pdfFiles.length === 0) {
    uploadError.value = 'Please upload PDF files only.'
    return
  }

  uploadError.value = null
  uploadSuccess.value = null

  // Add files to queue and start processing
  uploadQueue.value.push(...pdfFiles)
  if (!uploading.value) {
    processQueue()
  }
}

async function processQueue() {
  if (uploadQueue.value.length === 0) {
    uploading.value = false
    currentFile.value = null
    return
  }

  uploading.value = true
  const file = uploadQueue.value.shift()
  currentFile.value = file.name

  try {
    const result = await uploadInvoice(file)
    uploadSuccess.value = `"${file.name}" uploaded successfully.`
    uploadError.value = null
    emit('upload-complete')

    // If this was the only/last file, navigate to the invoice
    if (uploadQueue.value.length === 0) {
      setTimeout(() => {
        router.push(`/invoice/${result.id}`)
      }, 600)
    }
  } catch (err) {
    uploadError.value = `Error uploading "${file.name}": ${err.message}`
  }

  // Process next file in queue
  await processQueue()
}
</script>

<template>
  <div class="upload-zone-wrapper">
    <div
      class="upload-zone"
      :class="{
        'upload-zone--dragging': isDragging,
        'upload-zone--uploading': uploading,
      }"
      @click="openFilePicker"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @drop="handleDrop"
    >
      <input
        ref="fileInput"
        type="file"
        accept=".pdf,application/pdf"
        multiple
        hidden
        @change="handleFileSelect"
      />

      <!-- Uploading State -->
      <div v-if="uploading" class="upload-zone-content">
        <span class="spinner spinner-lg"></span>
        <p class="upload-zone-label">Uploading...</p>
        <p class="upload-zone-hint">{{ currentFile }}</p>
        <p v-if="uploadQueue.length > 0" class="upload-zone-hint">
          {{ uploadQueue.length }} file(s) remaining in queue
        </p>
      </div>

      <!-- Default State -->
      <div v-else class="upload-zone-content">
        <svg class="upload-zone-icon" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="17 8 12 3 7 8" />
          <line x1="12" y1="3" x2="12" y2="15" />
        </svg>
        <p class="upload-zone-label">Drop PDF here or click to upload</p>
        <p class="upload-zone-hint">Only PDF files accepted</p>
      </div>
    </div>

    <!-- Status Messages -->
    <div v-if="uploadSuccess" class="upload-message upload-message--success fade-in">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="20 6 9 17 4 12" />
      </svg>
      {{ uploadSuccess }}
    </div>
    <div v-if="uploadError" class="upload-message upload-message--error fade-in">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10" />
        <line x1="15" y1="9" x2="9" y2="15" />
        <line x1="9" y1="9" x2="15" y2="15" />
      </svg>
      {{ uploadError }}
    </div>
  </div>
</template>

<style scoped>
.upload-zone {
  border: 2px dashed var(--border-color);
  border-radius: var(--radius-lg);
  padding: 48px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  background: var(--bg-card);
}

.upload-zone:hover {
  border-color: var(--primary);
  background: var(--primary-light);
}

.upload-zone--dragging {
  border-color: var(--primary);
  background: var(--primary-light);
  border-style: solid;
}

.upload-zone--uploading {
  cursor: default;
  border-color: var(--border-color);
  background: var(--bg-card);
}

.upload-zone-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.upload-zone-icon {
  color: var(--text-muted);
  margin-bottom: 8px;
}

.upload-zone:hover .upload-zone-icon {
  color: var(--primary);
}

.upload-zone-label {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
}

.upload-zone-hint {
  font-size: 13px;
  color: var(--text-muted);
}

.spinner-lg {
  width: 32px;
  height: 32px;
  border-width: 3px;
  margin-bottom: 8px;
}

.upload-message {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 10px 16px;
  border-radius: var(--radius-sm);
  font-size: 14px;
}

.upload-message--success {
  background: var(--success-light);
  color: var(--success);
}

.upload-message--error {
  background: var(--danger-light);
  color: var(--danger);
}
</style>
