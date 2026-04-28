const BASE_URL = '/api'

/**
 * Upload a PDF invoice file.
 * Returns the created invoice object from the API.
 */
export async function uploadInvoice(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${BASE_URL}/invoices/upload`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(`Upload failed (${response.status}): ${errorText}`)
  }

  return response.json()
}

/**
 * Get a list of all invoices.
 */
export async function getInvoices() {
  const response = await fetch(`${BASE_URL}/invoices`)

  if (!response.ok) {
    throw new Error(`Failed to load invoices (${response.status})`)
  }

  return response.json()
}

/**
 * Get a single invoice by ID, including line_items.
 */
export async function getInvoice(id) {
  const response = await fetch(`${BASE_URL}/invoices/${id}`)

  if (!response.ok) {
    throw new Error(`Failed to load invoice (${response.status})`)
  }

  return response.json()
}

/**
 * Update an invoice by ID.
 * data is a partial object with the fields to update.
 */
export async function updateInvoice(id, data) {
  const response = await fetch(`${BASE_URL}/invoices/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(`Save failed (${response.status}): ${errorText}`)
  }

  return response.json()
}

/**
 * Search invoices with filters.
 * params: { q, supplier, status, date_from, date_to, currency }
 */
export async function searchInvoices(params = {}) {
  const query = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== null && value !== undefined && value !== '') {
      query.append(key, value)
    }
  }

  const url = query.toString()
    ? `${BASE_URL}/invoices/search?${query}`
    : `${BASE_URL}/invoices/search`

  const response = await fetch(url)

  if (!response.ok) {
    throw new Error(`Search failed (${response.status})`)
  }

  return response.json()
}

/**
 * Get the URL for the PDF of an invoice.
 */
export function getPdfUrl(id) {
  return `${BASE_URL}/invoices/${id}/pdf`
}

// --- Modul 3: Matching ---

/**
 * Create a match between two invoices.
 */
export async function createMatch(invoiceAId, invoiceBId) {
  const response = await fetch(`${BASE_URL}/matches`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ invoice_a_id: invoiceAId, invoice_b_id: invoiceBId }),
  })

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(`Match failed (${response.status}): ${errorText}`)
  }

  return response.json()
}

/**
 * Get all matches.
 */
export async function getMatches() {
  const response = await fetch(`${BASE_URL}/matches`)
  if (!response.ok) throw new Error(`Failed to load matches (${response.status})`)
  return response.json()
}

/**
 * Get a single match with details.
 */
export async function getMatch(id) {
  const response = await fetch(`${BASE_URL}/matches/${id}`)
  if (!response.ok) throw new Error(`Failed to load match (${response.status})`)
  return response.json()
}

/**
 * Delete a match.
 */
export async function deleteMatch(id) {
  const response = await fetch(`${BASE_URL}/matches/${id}`, { method: 'DELETE' })
  if (!response.ok) throw new Error(`Failed to delete match (${response.status})`)
}

// --- Modul 4: Reports ---

/**
 * Get invoice summary report.
 */
export async function getReportSummary(params = {}) {
  const query = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value) query.append(key, value)
  }
  const url = query.toString()
    ? `${BASE_URL}/reports/summary?${query}`
    : `${BASE_URL}/reports/summary`

  const response = await fetch(url)
  if (!response.ok) throw new Error(`Failed to load report (${response.status})`)
  return response.json()
}

/**
 * Get CSV export URL.
 */
export function getExportCsvUrl(params = {}) {
  const query = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value) query.append(key, value)
  }
  return query.toString()
    ? `${BASE_URL}/reports/export/csv?${query}`
    : `${BASE_URL}/reports/export/csv`
}

// --- Modul 5: Alerts ---

/**
 * Get active alerts (overdue invoices).
 */
export async function getAlerts() {
  const response = await fetch(`${BASE_URL}/alerts`)
  if (!response.ok) throw new Error(`Failed to load alerts (${response.status})`)
  return response.json()
}
