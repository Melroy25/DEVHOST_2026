// frontend/src/api.js — API client with X-User-Id header support

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function getHeaders(customHeaders = {}) {
  const headers = { ...customHeaders };
  const userId = localStorage.getItem('app_user_id');
  if (userId) {
    headers['X-User-Id'] = userId;
  }
  return headers;
}

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

  async listUsers() {
    const res = await fetch(`${API_BASE}/users`);
    return handleResponse(res);
  },

  async getMe() {
    const res = await fetch(`${API_BASE}/me`, {
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  async getMyPatients() {
    const res = await fetch(`${API_BASE}/me/patients`, {
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  async getPatient(pid) {
    const res = await fetch(`${API_BASE}/patients/${pid}`, {
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  async listCaretakers(pid) {
    const res = await fetch(`${API_BASE}/patients/${pid}/caretakers`, {
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  async addCaretaker(pid, caretakerUserId, permission = 'view') {
    const res = await fetch(`${API_BASE}/patients/${pid}/caretakers`, {
      method: 'POST',
      headers: getHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({
        caretaker_user_id: caretakerUserId,
        permission,
      }),
    });
    return handleResponse(res);
  },

  async updateCaretakerPermission(pid, linkId, permission) {
    const res = await fetch(`${API_BASE}/patients/${pid}/caretakers/${linkId}`, {
      method: 'PATCH',
      headers: getHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ permission }),
    });
    return handleResponse(res);
  },

  async revokeCaretaker(pid, linkId) {
    const res = await fetch(`${API_BASE}/patients/${pid}/caretakers/${linkId}`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  async listDocuments(pid) {
    const res = await fetch(`${API_BASE}/patients/${pid}/documents`, {
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  async uploadDocument(pid, file, docType = 'other') {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('doc_type', docType);

    const res = await fetch(`${API_BASE}/patients/${pid}/documents`, {
      method: 'POST',
      headers: getHeaders(), // Note: do not set Content-Type for FormData
      body: formData,
    });
    return handleResponse(res);
  },

  async getDocumentPages(did) {
    const res = await fetch(`${API_BASE}/documents/${did}/pages`, {
      headers: getHeaders(),
    });
    return handleResponse(res);
  },
};
