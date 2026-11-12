import React, { useState, useEffect } from 'react';
import { api } from './api';

export default function App() {
  const [health, setHealth] = useState({ status: 'checking', version: '' });
  const [patients, setPatients] = useState([]);
  const [selectedPatientId, setSelectedPatientId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Poll health on mount
  useEffect(() => {
    api.checkHealth()
      .then(res => setHealth({ status: 'online', version: res.version }))
      .catch(() => setHealth({ status: 'offline', version: '' }));
  }, []);

  // Load patients
  const loadPatients = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.listPatients();
      setPatients(data);
    } catch (err) {
      setError(`Failed to load patients: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPatients();
  }, []);

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-brand">
          <div className="brand-logo">🩺</div>
          <div>
            <h1>One Patient, Many Records</h1>
            <p className="subtitle">Verified Clinical History & Document Intelligence</p>
          </div>
        </div>
        <div className="header-meta">
          <div className={`status-pill ${health.status}`}>
            <span className="status-dot"></span>
            Backend: {health.status === 'online' ? `Online (v${health.version})` : 'Offline'}
          </div>
        </div>
      </header>

      {error && (
        <div className="global-error-banner">
          <span>⚠️ {error}</span>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      <main className="app-main">
        {!selectedPatientId ? (
          <PatientListView
            patients={patients}
            loading={loading}
            onRefresh={loadPatients}
            onSelectPatient={(id) => setSelectedPatientId(id)}
          />
        ) : (
          <PatientDetailView
            patientId={selectedPatientId}
            onBack={() => {
              setSelectedPatientId(null);
              loadPatients();
            }}
          />
        )}
      </main>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Patient List View
// ---------------------------------------------------------------------------

function PatientListView({ patients, loading, onRefresh, onSelectPatient }) {
  const [name, setName] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);

  const handleAddPatient = async (e) => {
    e.preventDefault();
    if (!name.trim()) return;

    try {
      setSubmitting(true);
      setFormError(null);
      await api.createPatient(name.trim());
      setName('');
      await onRefresh();
    } catch (err) {
      setFormError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="patient-list-view">
      <div className="section-header">
        <div>
          <h2>Patients Directory</h2>
          <p className="section-desc">Manage patient profiles and inspect multi-source health records</p>
        </div>
        <button className="btn btn-secondary" onClick={onRefresh} disabled={loading}>
          🔄 Refresh
        </button>
      </div>

      <div className="content-grid-two-col">
        {/* Create Patient Card */}
        <div className="card form-card">
          <div className="card-header">
            <h3>Add New Patient</h3>
          </div>
          <form onSubmit={handleAddPatient} className="card-body">
            <div className="form-group">
              <label htmlFor="patientName">Full Name</label>
              <input
                id="patientName"
                type="text"
                className="input-field"
                placeholder="e.g. Alice Johnson, Bob Smith"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={submitting}
                required
              />
            </div>
            {formError && <p className="error-text">{formError}</p>}
            <button type="submit" className="btn btn-primary" disabled={submitting || !name.trim()}>
              {submitting ? 'Registering...' : '+ Register Patient'}
            </button>
          </form>
        </div>

        {/* Existing Patients List */}
        <div className="card">
          <div className="card-header">
            <h3>Registered Patients ({patients.length})</h3>
          </div>
          <div className="card-body">
            {loading && patients.length === 0 ? (
              <p className="muted-text">Loading patients...</p>
            ) : patients.length === 0 ? (
              <div className="empty-state">
                <p>No patients registered yet.</p>
                <p className="muted-text">Add your first patient using the form on the left.</p>
              </div>
            ) : (
              <ul className="patient-cards-list">
                {patients.map((p) => (
                  <li key={p.id} className="patient-card-item">
                    <div className="patient-card-info">
                      <span className="patient-avatar">👤</span>
                      <div>
                        <strong className="patient-name">{p.name}</strong>
                        <div className="patient-id-badge">ID: {p.id.slice(0, 8)}...</div>
                        <div className="patient-date">Registered: {new Date(p.created_at).toLocaleDateString()}</div>
                      </div>
                    </div>
                    <button
                      className="btn btn-primary btn-sm"
                      onClick={() => onSelectPatient(p.id)}
                    >
                      Open Record →
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Patient Detail View
// ---------------------------------------------------------------------------

function PatientDetailView({ patientId, onBack }) {
  const [patient, setPatient] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [selectedDocId, setSelectedDocId] = useState(null);
  const [docPages, setDocPages] = useState([]);
  const [selectedPageNo, setSelectedPageNo] = useState(1);
  const [loadingDocText, setLoadingDocText] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Upload state
  const [uploadFile, setUploadFile] = useState(null);
  const [docType, setDocType] = useState('other');
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [pat, docs] = await Promise.all([
        api.getPatient(patientId),
        api.listDocuments(patientId),
      ]);
      setPatient(pat);
      setDocuments(docs);
      if (docs.length > 0 && !selectedDocId) {
        setSelectedDocId(docs[0].id);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [patientId]);

  // Load document pages when selectedDocId changes
  useEffect(() => {
    if (!selectedDocId) {
      setDocPages([]);
      return;
    }
    setLoadingDocText(true);
    api.getDocumentPages(selectedDocId)
      .then(pages => {
        setDocPages(pages);
        setSelectedPageNo(1);
      })
      .catch(err => {
        setDocPages([{ page_no: 1, text: `Failed to load text: ${err.message}` }]);
      })
      .finally(() => setLoadingDocText(false));
  }, [selectedDocId]);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!uploadFile) return;

    try {
      setUploading(true);
      setUploadError(null);
      const newDoc = await api.uploadDocument(patientId, uploadFile, docType);
      setUploadFile(null);
      // Reset input element
      const fileInput = document.getElementById('docFileInput');
      if (fileInput) fileInput.value = '';

      // Reload docs and select the newly uploaded one
      const updatedDocs = await api.listDocuments(patientId);
      setDocuments(updatedDocs);
      setSelectedDocId(newDoc.id);
    } catch (err) {
      setUploadError(`Upload failed: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  const selectedDoc = documents.find(d => d.id === selectedDocId);
  const currentPage = docPages.find(p => p.page_no === selectedPageNo) || docPages[0];

  return (
    <div className="patient-detail-view">
      {/* Top Banner Navigation */}
      <div className="patient-top-bar">
        <button className="btn btn-secondary btn-sm" onClick={onBack}>
          ← Back to All Patients
        </button>
        {patient && (
          <div className="patient-identity-chip">
            <span className="patient-chip-name">Patient: <strong>{patient.name}</strong></span>
            <span className="patient-chip-id">ID: {patient.id}</span>
          </div>
        )}
      </div>

      {error && <div className="error-text mb-4">⚠️ {error}</div>}

      <div className="detail-layout">
        {/* Left Column: Documents & Text Extraction */}
        <div className="detail-column left-pane">
          {/* Upload Box */}
          <div className="card">
            <div className="card-header">
              <h3>Upload Document</h3>
            </div>
            <form onSubmit={handleUpload} className="card-body">
              <div className="form-group">
                <label htmlFor="docFileInput">Select File (PDF, DOCX, TXT, Image)</label>
                <input
                  id="docFileInput"
                  type="file"
                  className="input-file"
                  accept=".pdf,.docx,.doc,.txt,.png,.jpg,.jpeg"
                  onChange={(e) => setUploadFile(e.target.files[0] || null)}
                  disabled={uploading}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="docTypeSelect">Document Category</label>
                <select
                  id="docTypeSelect"
                  className="input-field"
                  value={docType}
                  onChange={(e) => setDocType(e.target.value)}
                  disabled={uploading}
                >
                  <option value="other">Other / General Note</option>
                  <option value="lab_report">Lab Report</option>
                  <option value="prescription">Prescription</option>
                  <option value="discharge_summary">Discharge Summary</option>
                </select>
              </div>

              {uploadError && <p className="error-text">{uploadError}</p>}

              <button
                type="submit"
                className="btn btn-primary w-full"
                disabled={uploading || !uploadFile}
              >
                {uploading ? 'Processing & Extracting...' : 'Upload & Extract'}
              </button>
            </form>
          </div>

          {/* Document List */}
          <div className="card mt-4">
            <div className="card-header flex-between">
              <h3>Uploaded Documents ({documents.length})</h3>
              <button
                className="btn btn-secondary btn-xs"
                onClick={loadData}
                disabled={loading}
              >
                ↻ Refresh
              </button>
            </div>
            <div className="card-body">
              {documents.length === 0 ? (
                <p className="muted-text">No documents uploaded yet. Upload one above.</p>
              ) : (
                <ul className="doc-list">
                  {documents.map((doc) => {
                    const isSelected = doc.id === selectedDocId;
                    return (
                      <li
                        key={doc.id}
                        className={`doc-list-item ${isSelected ? 'selected' : ''}`}
                        onClick={() => setSelectedDocId(doc.id)}
                      >
                        <div className="doc-item-title">
                          <span className="doc-icon">📄</span>
                          <span className="doc-name">{doc.filename}</span>
                        </div>
                        <div className="doc-meta-tags">
                          <span className={`badge badge-${doc.doc_type}`}>
                            {doc.doc_type.replace('_', ' ')}
                          </span>
                          <span className="badge badge-gray">{doc.page_count} page{doc.page_count > 1 ? 's' : ''}</span>
                        </div>
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>
          </div>

          {/* Document Page Viewer */}
          {selectedDoc && (
            <div className="card mt-4">
              <div className="card-header flex-between">
                <div>
                  <h3>Document Page Viewer</h3>
                  <p className="muted-text small">{selectedDoc.filename}</p>
                </div>
                {docPages.length > 1 && (
                  <div className="page-nav">
                    <button
                      className="btn btn-secondary btn-xs"
                      disabled={selectedPageNo <= 1}
                      onClick={() => setSelectedPageNo(p => Math.max(1, p - 1))}
                    >
                      ← Prev
                    </button>
                    <span className="page-indicator">
                      Page {selectedPageNo} of {docPages.length}
                    </span>
                    <button
                      className="btn btn-secondary btn-xs"
                      disabled={selectedPageNo >= docPages.length}
                      onClick={() => setSelectedPageNo(p => Math.min(docPages.length, p + 1))}
                    >
                      Next →
                    </button>
                  </div>
                )}
              </div>
              <div className="card-body">
                {loadingDocText ? (
                  <p className="muted-text">Loading extracted page text...</p>
                ) : !currentPage ? (
                  <p className="muted-text">No page content found.</p>
                ) : (
                  <pre className="extracted-text-box">
                    {currentPage.text || '(Page contains no extractable text)'}
                  </pre>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Clinical Intelligence & Placeholders */}
        <div className="detail-column right-pane">
          <div className="placeholder-banner">
            <h3>Clinical Synthesis & Analysis</h3>
            <p>Phase 0/1 foundation is active. Ingestion pipeline is running on SQLite and ready for extraction.</p>
          </div>

          {/* Medication Timeline Placeholder */}
          <div className="card placeholder-card">
            <div className="card-header">
              <div className="card-title-icon">💊</div>
              <div>
                <h4>Medication Timeline</h4>
                <span className="tag-coming-soon">Coming Soon</span>
              </div>
            </div>
            <div className="card-body">
              <p className="placeholder-desc">
                Derived lifecycle of all patient medications (started, changed, stopped, current list)
                with exact source passage citations.
              </p>
              <div className="mock-timeline">
                <div className="mock-event">
                  <div className="mock-dot green"></div>
                  <div><strong>Metformin 500mg</strong> — Started March 2021</div>
                </div>
                <div className="mock-event">
                  <div className="mock-dot blue"></div>
                  <div><strong>Lisinopril 10mg</strong> — Current prescription</div>
                </div>
              </div>
            </div>
          </div>

          {/* Clinical Facts & Quotes Placeholder */}
          <div className="card placeholder-card mt-4">
            <div className="card-header">
              <div className="card-title-icon">🔍</div>
              <div>
                <h4>Verified Facts & Quotes</h4>
                <span className="tag-coming-soon">Coming Soon</span>
              </div>
            </div>
            <div className="card-body">
              <p className="placeholder-desc">
                Structured clinical facts (conditions, labs, allergies) with verbatim quote verification against raw pages.
              </p>
              <div className="mock-fact-pill">
                <span>HbA1c: <strong>7.2%</strong> (March 2024)</span>
                <span className="quote-badge">"HbA1c 7.2% (March 2024)"</span>
              </div>
            </div>
          </div>

          {/* Safety & Contradiction Flags Placeholder */}
          <div className="card placeholder-card mt-4">
            <div className="card-header">
              <div className="card-title-icon">🚩</div>
              <div>
                <h4>Quality & Safety Flags</h4>
                <span className="tag-coming-soon">Coming Soon</span>
              </div>
            </div>
            <div className="card-body">
              <p className="placeholder-desc">
                Rule-based flags for allergy contradictions, dosage mismatches, stale medications, and missing dates.
              </p>
              <div className="mock-flag-box">
                <span className="flag-icon">⚠️</span>
                <span>Flag engine detects conflicts without silently guessing.</span>
              </div>
            </div>
          </div>

          {/* Grounded Q&A Box Placeholder */}
          <div className="card placeholder-card mt-4">
            <div className="card-header">
              <div className="card-title-icon">💬</div>
              <div>
                <h4>Grounded Clinical Q&A</h4>
                <span className="tag-coming-soon">Coming Soon</span>
              </div>
            </div>
            <div className="card-body">
              <div className="mock-qa-input">
                <input
                  type="text"
                  className="input-field"
                  placeholder="Ask a question about this patient's records..."
                  disabled
                />
                <button className="btn btn-secondary" disabled>Ask</button>
              </div>
              <p className="muted-text small mt-2">
                Answers cite fact IDs; questions asking for diagnosis or treatment advice are declined by contract.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
