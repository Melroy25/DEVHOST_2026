// frontend/src/api.js — API client for FastAPI backend

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function handleResponse(res) {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const data = await res.json();
      detail = data.detail || detail;
    } catch {
      // ignore
    }
    throw new Error(detail);
  }
  return res.json();
}

export const api = {
  baseUrl: API_BASE,

  async checkHealth() {
    const res = await fetch(`${API_BASE}/health`);
    return handleResponse(res);
  },

  async listPatients() {
    const res = await fetch(`${API_BASE}/patients`);
    return handleResponse(res);
  },

  async createPatient(name) {
    const res = await fetch(`${API_BASE}/patients`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name }),
    });
    return handleResponse(res);
  },

  async getPatient(pid) {
    const res = await fetch(`${API_BASE}/patients/${pid}`);
    return handleResponse(res);
  },

  async listDocuments(pid) {
    const res = await fetch(`${API_BASE}/patients/${pid}/documents`);
    return handleResponse(res);
  },

  async uploadDocument(pid, file, docType = 'other') {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('doc_type', docType);

    const res = await fetch(`${API_BASE}/patients/${pid}/documents`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse(res);
  },

  async getDocumentPage(did, pageNo) {
    const res = await fetch(`${API_BASE}/documents/${did}/page/${pageNo}`);
    return handleResponse(res);
  },

  async getDocumentPages(did) {
    const res = await fetch(`${API_BASE}/documents/${did}/pages`);
    return handleResponse(res);
  },
};
