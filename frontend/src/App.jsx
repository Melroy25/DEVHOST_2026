import React, { useState, useEffect } from 'react';
import { api } from './api';
import {
  Activity,
  FileText,
  Users,
  Shield,
  Search,
  Bell,
  LogOut,
  Layers,
  Sparkles,
  ChevronRight,
  ChevronLeft,
  RotateCw,
  FolderOpen,
  UserCheck,
  Eye,
  Edit3,
  CheckCircle2,
  AlertTriangle,
  FileUp,
  TrendingUp,
  Settings,
  ArrowRight
} from 'lucide-react';

export default function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [loadingAuth, setLoadingAuth] = useState(true);
  const [health, setHealth] = useState({ status: 'checking', version: '' });
  const [activeTab, setActiveTab] = useState('documents'); // 'documents' | 'caretakers' | 'clinical'
  const [searchQuery, setSearchQuery] = useState('');

  // Initial auth and health check
  useEffect(() => {
    api.checkHealth()
      .then(res => setHealth({ status: 'online', version: res.version }))
      .catch(() => setHealth({ status: 'offline', version: '' }));

    const savedUserId = localStorage.getItem('app_user_id');
    if (savedUserId) {
      api.getMe()
        .then(user => setCurrentUser(user))
        .catch(() => {
          localStorage.removeItem('app_user_id');
          setCurrentUser(null);
        })
        .finally(() => setLoadingAuth(false));
    } else {
      setLoadingAuth(false);
    }
  }, []);

  const handleLogin = (user) => {
    localStorage.setItem('app_user_id', user.id);
    setCurrentUser(user);
    setActiveTab('documents');
  };

  const handleLogout = () => {
    localStorage.removeItem('app_user_id');
    setCurrentUser(null);
  };

  if (loadingAuth) {
    return (
      <div className="app-loading-screen">
        <div className="spinner"></div>
        <p>Loading application...</p>
      </div>
    );
  }

  return (
    <div className="app-outer-canvas">
      {/* Centered White Site Container (FyniteCare aesthetic) */}
      <div className="app-frame">
        {/* ===================================================================
            NAVBAR (Height 85px, horizontal padding, logo + nav links + actions)
            =================================================================== */}
        <header className="app-navbar">
          <div className="navbar-inner">
            {/* Left: Logo (Green cross & leaves + Brand name) */}
            <div className="brand-link" onClick={() => setActiveTab('documents')}>
              <div className="brand-icon-leaf">
                <svg width="28" height="28" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect x="13.5" y="4" width="5" height="15" rx="2" fill="#76A63F" />
                  <rect x="8.5" y="9" width="15" height="5" rx="2" fill="#76A63F" />
                  <path d="M16 26C16 26 11 25 8.5 20.5C6.5 16.5 9.5 14 12 15C14.5 16 15.5 19.5 16 26Z" fill="#76A63F" />
                  <path d="M16 26C16 26 21 25 23.5 20.5C25.5 16.5 22.5 14 20 15C17.5 16 16.5 19.5 16 26Z" fill="#76A63F" />
                </svg>
              </div>
              <div className="brand-text">
                <span className="brand-text-black">One Patient</span>
                <span className="brand-text-green">, Many Records</span>
              </div>
            </div>

            {/* Center: Navigation Links with active 5px green dot */}
            <nav className="nav-links-center">
              {!currentUser ? (
                <button className="nav-link-btn active">
                  <span>Demo Accounts</span>
                  <span className="nav-active-dot" />
                </button>
              ) : currentUser.role === 'patient' ? (
                <>
                  <button
                    className={`nav-link-btn ${activeTab === 'documents' ? 'active' : ''}`}
                    onClick={() => setActiveTab('documents')}
                  >
                    <span>Documents & Pages</span>
                    {activeTab === 'documents' && <span className="nav-active-dot" />}
                  </button>

                  <button
                    className={`nav-link-btn ${activeTab === 'caretakers' ? 'active' : ''}`}
                    onClick={() => setActiveTab('caretakers')}
                  >
                    <span>Caretaker Access</span>
                    {activeTab === 'caretakers' && <span className="nav-active-dot" />}
                  </button>

                  <button
                    className={`nav-link-btn ${activeTab === 'clinical' ? 'active' : ''}`}
                    onClick={() => setActiveTab('clinical')}
                  >
                    <span>Clinical Intelligence</span>
                    {activeTab === 'clinical' && <span className="nav-active-dot" />}
                  </button>
                </>
              ) : (
                <>
                  <button
                    className={`nav-link-btn ${activeTab === 'documents' ? 'active' : ''}`}
                    onClick={() => setActiveTab('documents')}
                  >
                    <span>Records & Documents</span>
                    {activeTab === 'documents' && <span className="nav-active-dot" />}
                  </button>

                  <button
                    className={`nav-link-btn ${activeTab === 'clinical' ? 'active' : ''}`}
                    onClick={() => setActiveTab('clinical')}
                  >
                    <span>Clinical Intelligence</span>
                    {activeTab === 'clinical' && <span className="nav-active-dot" />}
                  </button>
                </>
              )}
            </nav>

            {/* Right: Search + Status Badge + User Profile */}
            <div className="navbar-right">
              {/* Search box in header */}
              <div className="navbar-search-box">
                <Search size={14} color="#6B6B6B" strokeWidth={2} />
                <input
                  type="text"
                  className="navbar-search-input"
                  placeholder="Search records or files..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>

              {/* Backend Status indicator */}
              <div className="stat-badge stat-badge-positive" title="FastAPI Backend Health">
                <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#76A63F' }}></span>
                <span>{health.status === 'online' ? `Online (v${health.version || '0.3.0'})` : 'Offline'}</span>
              </div>

              {/* User Avatar Chip or Demo Pill */}
              {currentUser ? (
                <div className="nav-user-chip">
                  <div className="nav-user-avatar">
                    {currentUser.name.charAt(0).toUpperCase()}
                  </div>
                  <span className="nav-user-name">{currentUser.name}</span>
                  <span className={`role-tag role-${currentUser.role}`}>{currentUser.role}</span>
                  <button
                    className="btn btn-secondary btn-xs"
                    onClick={handleLogout}
                    title="Log out of current demo persona"
                  >
                    <LogOut size={11} strokeWidth={2.2} />
                    Log out
                  </button>
                </div>
              ) : (
                <div className="stat-badge stat-badge-neutral">
                  Demo Portals
                </div>
              )}
            </div>
          </div>

          {/* 1px light gray divider line #DADADA inset 60px */}
          <div className="navbar-divider" />
        </header>

        {/* ===================================================================
            MAIN APP BODY
            =================================================================== */}
        <main className="app-content-body">
          {/* Hero Badge Pill */}
          <div className="hero-badge-pill">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#76A63F" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
              <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
              <path d="M3.22 12H9.5l1.5-3 2 6 1.5-3h6.28" />
            </svg>
            <span>Smart Healthcare, Just for You</span>
          </div>

          {/* Hero Title & Subtitle */}
          <div className="hero-header-row">
            <div>
              <h1 className="hero-title-main">
                Your Health, Our <span className="hero-title-green">Priority</span>
              </h1>
              <p className="hero-subtitle">
                Advanced technology and compassionate care come together to deliver a healthier, happier you.
              </p>
            </div>
          </div>

          {/* Content Router */}
          {!currentUser ? (
            <LoginScreen onLogin={handleLogin} health={health} />
          ) : currentUser.role === 'patient' ? (
            <PatientPortal
              currentUser={currentUser}
              health={health}
              activeTab={activeTab}
              setActiveTab={setActiveTab}
              searchQuery={searchQuery}
            />
          ) : (
            <CaretakerPortal
              currentUser={currentUser}
              health={health}
              activeTab={activeTab}
              setActiveTab={setActiveTab}
              searchQuery={searchQuery}
            />
          )}
        </main>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// 1. Login Screen (Demo User Selection)
// ---------------------------------------------------------------------------

function LoginScreen({ onLogin, health }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.listUsers()
      .then(data => setUsers(data))
      .catch(err => setError(`Failed to fetch demo users: ${err.message}`))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="login-screen-wrapper">
      {/* 4 Stat Cards */}
      <div className="stat-cards-grid" style={{ marginBottom: '24px' }}>
        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-label">Demo Personas</span>
            <div className="stat-icon-chip"><Users size={16} strokeWidth={2.2} /></div>
          </div>
          <div className="stat-card-number">{users.length || 3}</div>
          <div className="stat-card-footer">
            <span className="stat-badge stat-badge-positive"><TrendingUp size={10} /> Active</span>
            <span className="stat-subtext">Pre-seeded users</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-label">Portal Roles</span>
            <div className="stat-icon-chip"><Shield size={16} strokeWidth={2.2} /></div>
          </div>
          <div className="stat-card-number">2 Roles</div>
          <div className="stat-card-footer">
            <span className="stat-badge stat-badge-neutral">Patient & Caretaker</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-label">Access Control</span>
            <div className="stat-icon-chip"><CheckCircle2 size={16} strokeWidth={2.2} /></div>
          </div>
          <div className="stat-card-number">v0.3.0</div>
          <div className="stat-card-footer">
            <span className="stat-badge stat-badge-positive">RBAC Protected</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-label">Pipeline Health</span>
            <div className="stat-icon-chip"><Activity size={16} strokeWidth={2.2} /></div>
          </div>
          <div className="stat-card-number">
            {health.status === 'online' ? '100%' : 'Offline'}
          </div>
          <div className="stat-card-footer">
            <span className={health.status === 'online' ? 'stat-badge stat-badge-positive' : 'stat-badge stat-badge-warning'}>
              {health.status === 'online' ? 'Optimal' : 'Checking'}
            </span>
            <span className="stat-subtext">Port 8000</span>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <div>
            <h2>Select Demo Persona</h2>
            <p className="muted-text small">Choose an account to explore the Patient or Caretaker portal</p>
          </div>
        </div>
        <div className="card-body">
          {loading ? (
            <p className="muted-text text-center">Loading demo users...</p>
          ) : error ? (
            <div className="error-text text-center">{error}</div>
          ) : (
            <div className="user-select-grid">
              {users.map(u => (
                <div
                  key={u.id}
                  className="user-select-card"
                  onClick={() => onLogin(u)}
                >
                  <div className="user-card-icon">
                    {u.role === 'patient' ? '👤' : '🧑‍⚕️'}
                  </div>
                  <div className="user-card-details">
                    <h3>{u.name}</h3>
                    <span className={`badge badge-role-${u.role}`}>{u.role.toUpperCase()}</span>
                    <p className="user-desc">
                      {u.role === 'patient'
                        ? 'Owns health records, manages caretaker access, uploads files'
                        : 'Views or contributes to patient records shared by patients'}
                    </p>
                  </div>
                  <button className="btn btn-primary btn-sm mt-4">
                    <span>Enter as {u.name}</span>
                    <ArrowRight size={13} strokeWidth={2.2} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// 2. Patient Portal (/patient)
// ---------------------------------------------------------------------------

function PatientPortal({ currentUser, health, activeTab, setActiveTab, searchQuery }) {
  const [myPatients, setMyPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const items = await api.getMyPatients();
      setMyPatients(items);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return <p className="muted-text p-4">Loading your patient record...</p>;
  }

  if (error) {
    return <div className="error-text p-4">⚠️ {error}</div>;
  }

  const primaryItem = myPatients[0];
  if (!primaryItem) {
    return (
      <div className="empty-state card p-4">
        <h3>No patient record found for your account.</h3>
      </div>
    );
  }

  return (
    <div className="portal-container patient-portal">
      <PatientRecordView
        currentUser={currentUser}
        patientId={primaryItem.patient.id}
        initialPermission={primaryItem.permission}
        health={health}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        searchQuery={searchQuery}
      />
    </div>
  );
}

// ---------------------------------------------------------------------------
// 3. Caretaker Portal (/caretaker)
// ---------------------------------------------------------------------------

function CaretakerPortal({ currentUser, health, activeTab, setActiveTab, searchQuery }) {
  const [sharedPatients, setSharedPatients] = useState([]);
  const [selectedPatientId, setSelectedPatientId] = useState(null);
  const [selectedPermission, setSelectedPermission] = useState('view');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadPatients = async () => {
    try {
      setLoading(true);
      setError(null);
      const items = await api.getMyPatients();
      setSharedPatients(items);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPatients();
  }, []);

  if (loading) {
    return <p className="muted-text p-4">Loading shared patient records...</p>;
  }

  if (error) {
    return <div className="error-text p-4">⚠️ {error}</div>;
  }

  // If a patient is selected, open the shared PatientRecordView
  if (selectedPatientId) {
    return (
      <div className="portal-container caretaker-portal">
        <div className="back-bar">
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => {
              setSelectedPatientId(null);
              loadPatients();
            }}
          >
            ← Back to My Patients
          </button>
        </div>
        <PatientRecordView
          currentUser={currentUser}
          patientId={selectedPatientId}
          initialPermission={selectedPermission}
          health={health}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          searchQuery={searchQuery}
          onBack={() => {
            setSelectedPatientId(null);
            loadPatients();
          }}
        />
      </div>
    );
  }

  return (
    <div className="portal-container caretaker-dashboard">
      {/* Stat Cards for Caretaker Overview */}
      <div className="stat-cards-grid" style={{ marginBottom: '24px' }}>
        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-label">Linked Patients</span>
            <div className="stat-icon-chip"><Users size={16} strokeWidth={2.2} /></div>
          </div>
          <div className="stat-card-number">{sharedPatients.length}</div>
          <div className="stat-card-footer">
            <span className="stat-badge stat-badge-positive"><TrendingUp size={10} /> Active</span>
            <span className="stat-subtext">Authorized records</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-label">Current Persona</span>
            <div className="stat-icon-chip"><UserCheck size={16} strokeWidth={2.2} /></div>
          </div>
          <div className="stat-card-number">{currentUser.name}</div>
          <div className="stat-card-footer">
            <span className="stat-badge stat-badge-neutral">Role: Caretaker</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-label">Access Control</span>
            <div className="stat-icon-chip"><Shield size={16} strokeWidth={2.2} /></div>
          </div>
          <div className="stat-card-number">Scoped</div>
          <div className="stat-card-footer">
            <span className="stat-badge stat-badge-positive">Verified RBAC</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-label">Pipeline Health</span>
            <div className="stat-icon-chip"><Activity size={16} strokeWidth={2.2} /></div>
          </div>
          <div className="stat-card-number">
            {health.status === 'online' ? '100%' : 'Offline'}
          </div>
          <div className="stat-card-footer">
            <span className={health.status === 'online' ? 'stat-badge stat-badge-positive' : 'stat-badge stat-badge-warning'}>
              {health.status === 'online' ? 'Optimal' : 'Checking'}
            </span>
            <span className="stat-subtext">v{health.version || '0.3.0'}</span>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header flex-between">
          <div>
            <h2>My Patients</h2>
            <p className="muted-text small">Patients who have granted you access to their medical records</p>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={loadPatients}>
            <RotateCw size={13} strokeWidth={2} /> Refresh
          </button>
        </div>

        <div className="card-body">
          {sharedPatients.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">🤝</div>
              <h3>No patients have shared records with you yet.</h3>
              <p className="muted-text">
                When a patient adds you as a caretaker from their portal, their records and documents will appear here.
              </p>
            </div>
          ) : (
            <div className="caretaker-patient-grid">
              {sharedPatients.map(({ patient, permission }) => (
                <div key={patient.id} className="card patient-access-card">
                  <div className="card-header flex-between">
                    <span className="patient-avatar-large">👤</span>
                    <span className={`badge badge-perm-${permission}`}>
                      {permission === 'view' ? '👁️ View Only' : '✏️ Can Contribute'}
                    </span>
                  </div>
                  <div className="card-body">
                    <h3>{patient.name}</h3>
                    <p className="patient-id-label">ID: {patient.id.slice(0, 8)}...</p>
                    <div className="patient-permission-desc">
                      {permission === 'view'
                        ? 'Read-only access to documents, timeline, and reports.'
                        : 'Authorized to review records and upload medical documents.'}
                    </div>
                    <button
                      className="btn btn-primary w-full mt-4"
                      onClick={() => {
                        setSelectedPatientId(patient.id);
                        setSelectedPermission(permission);
                      }}
                    >
                      <span>Open Record</span>
                      <ArrowRight size={13} strokeWidth={2.2} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// 4. SHARED Patient Record View Component (Built ONCE)
// ---------------------------------------------------------------------------

function PatientRecordView({
  currentUser,
  patientId,
  initialPermission,
  health,
  activeTab = 'documents',
  setActiveTab,
  searchQuery = ''
}) {
  const [patient, setPatient] = useState(null);
  const [permission, setPermission] = useState(initialPermission || 'view');
  const [documents, setDocuments] = useState([]);
  const [selectedDocId, setSelectedDocId] = useState(null);
  const [docPages, setDocPages] = useState([]);
  const [selectedPageNo, setSelectedPageNo] = useState(1);
  const [loadingDocText, setLoadingDocText] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Upload form state
  const [uploadFile, setUploadFile] = useState(null);
  const [docType, setDocType] = useState('other');
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);

  // Caretaker management state (Owner only)
  const [caretakers, setCaretakers] = useState([]);
  const [allUsers, setAllUsers] = useState([]);
  const [selectedCaretakerUserId, setSelectedCaretakerUserId] = useState('');
  const [newCaretakerPerm, setNewCaretakerPerm] = useState('view');
  const [caretakerActionError, setCaretakerActionError] = useState(null);

  const isOwner = permission === 'owner' || currentUser.role === 'patient';
  const canUpload = permission === 'owner' || permission === 'contribute';

  const loadPatientData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [pRes, docsRes] = await Promise.all([
        api.getPatient(patientId),
        api.listDocuments(patientId),
      ]);
      setPatient(pRes.patient);
      setPermission(pRes.permission);
      setDocuments(docsRes);
      if (docsRes.length > 0 && !selectedDocId) {
        setSelectedDocId(docsRes[0].id);
      }

      // If owner, load caretaker links and users list
      if (pRes.permission === 'owner') {
        const [links, users] = await Promise.all([
          api.listCaretakers(patientId),
          api.listUsers(),
        ]);
        setCaretakers(links);
        setAllUsers(users.filter(u => u.role === 'caretaker'));
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPatientData();
  }, [patientId]);

  // Load pages when selectedDocId changes
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

  // Upload handler
  const handleUpload = async (e) => {
    e.preventDefault();
    if (!uploadFile) return;

    try {
      setUploading(true);
      setUploadError(null);
      const newDoc = await api.uploadDocument(patientId, uploadFile, docType);
      setUploadFile(null);
      const inputEl = document.getElementById('recordFileInput');
      if (inputEl) inputEl.value = '';

      const updatedDocs = await api.listDocuments(patientId);
      setDocuments(updatedDocs);
      setSelectedDocId(newDoc.id);
    } catch (err) {
      setUploadError(err.message);
    } finally {
      setUploading(false);
    }
  };

  // Add Caretaker handler (Owner only)
  const handleAddCaretaker = async (e) => {
    e.preventDefault();
    if (!selectedCaretakerUserId) return;
    try {
      setCaretakerActionError(null);
      await api.addCaretaker(patientId, selectedCaretakerUserId, newCaretakerPerm);
      setSelectedCaretakerUserId('');
      const updated = await api.listCaretakers(patientId);
      setCaretakers(updated);
    } catch (err) {
      setCaretakerActionError(err.message);
    }
  };

  // Update Caretaker permission handler (Owner only)
  const handleTogglePermission = async (link) => {
    try {
      setCaretakerActionError(null);
      const nextPerm = link.permission === 'view' ? 'contribute' : 'view';
      await api.updateCaretakerPermission(patientId, link.id, nextPerm);
      const updated = await api.listCaretakers(patientId);
      setCaretakers(updated);
    } catch (err) {
      setCaretakerActionError(err.message);
    }
  };

  // Revoke Caretaker handler (Owner only)
  const handleRevokeCaretaker = async (linkId) => {
    if (!window.confirm('Are you sure you want to revoke this caretaker access?')) return;
    try {
      setCaretakerActionError(null);
      await api.revokeCaretaker(patientId, linkId);
      const updated = await api.listCaretakers(patientId);
      setCaretakers(updated);
    } catch (err) {
      setCaretakerActionError(err.message);
    }
  };

  const selectedDoc = documents.find(d => d.id === selectedDocId);
  const currentPage = docPages.find(p => p.page_no === selectedPageNo) || docPages[0];

  // Filter documents by searchQuery
  const filteredDocuments = documents.filter(doc =>
    doc.filename.toLowerCase().includes((searchQuery || '').toLowerCase()) ||
    doc.doc_type.toLowerCase().includes((searchQuery || '').toLowerCase())
  );

  const totalPagesCount = documents.reduce((acc, d) => acc + (d.page_count || 1), 0);

  return (
    <div className="patient-record-view">
      {/* 4 Stat Cards across top (FyniteCare design) */}
      <div className="stat-cards-grid" style={{ marginBottom: '24px' }}>
        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-label">Uploaded Documents</span>
            <div className="stat-icon-chip"><FileText size={16} strokeWidth={2.2} /></div>
          </div>
          <div className="stat-card-number">{documents.length}</div>
          <div className="stat-card-footer">
            <span className="stat-badge stat-badge-positive"><TrendingUp size={10} /> +100% active</span>
            <span className="stat-subtext">Ingested files</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-label">Extracted Pages</span>
            <div className="stat-icon-chip"><Layers size={16} strokeWidth={2.2} /></div>
          </div>
          <div className="stat-card-number">{totalPagesCount}</div>
          <div className="stat-card-footer">
            <span className="stat-badge stat-badge-neutral">OCR & Parsed</span>
            <span className="stat-subtext">Multi-format verified</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-label">Access Permission</span>
            <div className="stat-icon-chip"><Shield size={16} strokeWidth={2.2} /></div>
          </div>
          <div className="stat-card-number" style={{ fontSize: '18px', textTransform: 'capitalize' }}>
            {permission}
          </div>
          <div className="stat-card-footer">
            <span className="stat-badge stat-badge-positive">Authorized</span>
            <span className="stat-subtext">{isOwner ? `${caretakers.length} linked` : 'RBAC Protected'}</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-label">System Health</span>
            <div className="stat-icon-chip"><Activity size={16} strokeWidth={2.2} /></div>
          </div>
          <div className="stat-card-number">
            {health?.status === 'online' ? '100%' : 'Offline'}
          </div>
          <div className="stat-card-footer">
            <span className={health?.status === 'online' ? 'stat-badge stat-badge-positive' : 'stat-badge stat-badge-warning'}>
              {health?.status === 'online' ? 'Optimal' : 'Checking'}
            </span>
            <span className="stat-subtext">v{health?.version || '0.3.0'}</span>
          </div>
        </div>
      </div>

      {/* Access Permission Banner */}
      {permission === 'view' && (
        <div className="permission-banner banner-view">
          <AlertTriangle size={16} />
          <span><strong>View-only access:</strong> Records shared by patient. Document upload and editing controls are disabled.</span>
        </div>
      )}
      {permission === 'contribute' && (
        <div className="permission-banner banner-contribute">
          <Edit3 size={16} />
          <span><strong>Contributor access:</strong> You are authorized to review records and upload medical documents on behalf of the patient.</span>
        </div>
      )}

      {/* Patient Meta Banner */}
      <div className="patient-meta-header">
        <div className="patient-header-left">
          <span className="patient-avatar-badge">👤</span>
          <div>
            <h2>{patient ? patient.name : 'Patient Record'}</h2>
            <p className="patient-id-sub">Patient ID: <code>{patientId}</code></p>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="tab-pill-group">
          <button
            className={`tab-btn ${activeTab === 'documents' ? 'active' : ''}`}
            onClick={() => setActiveTab('documents')}
          >
            <FileText size={14} /> Documents & Pages ({documents.length})
          </button>

          {isOwner && (
            <button
              className={`tab-btn ${activeTab === 'caretakers' ? 'active' : ''}`}
              onClick={() => setActiveTab('caretakers')}
            >
              <Users size={14} /> Caretaker Access ({caretakers.length})
            </button>
          )}

          <button
            className={`tab-btn ${activeTab === 'clinical' ? 'active' : ''}`}
            onClick={() => setActiveTab('clinical')}
          >
            <Activity size={14} /> Clinical Intelligence
          </button>
        </div>
      </div>

      {error && <div className="error-text p-4">⚠️ {error}</div>}

      {/* Tab 1: Documents & Page Viewer */}
      {activeTab === 'documents' && (
        <div className="dashboard-main-grid">
          {/* Main 2-column detail layout */}
          <div className="detail-layout">
            {/* Left Column: Upload + Document List */}
            <div className="detail-column">
              {/* Upload Box (Shown only if write permission: Owner or Contribute) */}
              {canUpload ? (
                <div className="card">
                  <div className="card-header">
                    <h3>Upload Medical Document</h3>
                  </div>
                  <form onSubmit={handleUpload} className="card-body">
                    <div className="form-group">
                      <label htmlFor="recordFileInput">Choose Document (PDF, DOCX, TXT, Image)</label>
                      <input
                        id="recordFileInput"
                        type="file"
                        className="input-file"
                        accept=".pdf,.docx,.doc,.txt,.png,.jpg,.jpeg"
                        onChange={(e) => setUploadFile(e.target.files[0] || null)}
                        disabled={uploading}
                        required
                      />
                    </div>

                    <div className="form-group">
                      <label htmlFor="docTypeSelect">Document Type</label>
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
                      <FileUp size={14} />
                      <span>{uploading ? 'Parsing & Saving...' : 'Upload & Ingest'}</span>
                      <ArrowRight size={14} strokeWidth={2.4} />
                    </button>
                  </form>
                </div>
              ) : (
                <div className="card view-only-upload-card">
                  <div className="card-body muted-text">
                    🔒 Document uploading is disabled for view-only caretakers.
                  </div>
                </div>
              )}

              {/* Document List */}
              <div className="card mt-4">
                <div className="card-header flex-between">
                  <h3>Uploaded Documents ({filteredDocuments.length})</h3>
                  <button className="btn btn-secondary btn-xs" onClick={loadPatientData} disabled={loading}>
                    <RotateCw size={12} /> Refresh
                  </button>
                </div>
                <div className="card-body">
                  {filteredDocuments.length === 0 ? (
                    <p className="muted-text">
                      {searchQuery ? 'No documents match your search.' : 'No documents uploaded yet.'}
                    </p>
                  ) : (
                    <ul className="doc-list">
                      {filteredDocuments.map((doc) => {
                        const isSelected = doc.id === selectedDocId;
                        return (
                          <li
                            key={doc.id}
                            className={`doc-list-item ${isSelected ? 'selected' : ''}`}
                            onClick={() => setSelectedDocId(doc.id)}
                          >
                            <div className="doc-item-title">
                              <span className="doc-icon"><FileText size={15} color="#76A63F" /></span>
                              <span className="doc-name">{doc.filename}</span>
                            </div>
                            <div className="doc-meta-tags">
                              <span className={`badge badge-${doc.doc_type}`}>
                                {doc.doc_type.replace('_', ' ')}
                              </span>
                              <span className="badge badge-gray">{doc.page_count} p</span>
                            </div>
                          </li>
                        );
                      })}
                    </ul>
                  )}
                </div>
              </div>
            </div>

            {/* Right Column: Page Text Viewer */}
            <div className="detail-column">
              {selectedDoc ? (
                <div className="card">
                  <div className="card-header flex-between">
                    <div>
                      <h3>Page Text Viewer</h3>
                      <p className="muted-text small">{selectedDoc.filename}</p>
                    </div>
                    {docPages.length > 1 && (
                      <div className="page-nav">
                        <button
                          className="btn btn-secondary btn-xs"
                          disabled={selectedPageNo <= 1}
                          onClick={() => setSelectedPageNo(p => Math.max(1, p - 1))}
                        >
                          <ChevronLeft size={13} /> Prev
                        </button>
                        <span className="page-indicator">
                          Page {selectedPageNo} of {docPages.length}
                        </span>
                        <button
                          className="btn btn-secondary btn-xs"
                          disabled={selectedPageNo >= docPages.length}
                          onClick={() => setSelectedPageNo(p => Math.min(docPages.length, p + 1))}
                        >
                          Next <ChevronRight size={13} />
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
              ) : (
                <div className="card empty-state">
                  <p className="muted-text">Select a document on the left to inspect extracted page text.</p>
                </div>
              )}
            </div>
          </div>

          {/* Right Column: Promo Card + Clinical Status */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div className="promo-card">
              <div className="promo-card-icon">
                <Sparkles size={18} strokeWidth={2} />
              </div>
              <div>
                <h3>Clinical Intelligence Engine</h3>
                <p>
                  Deterministic safety rules, medication lifecycle tracking, and verified clinical citations.
                </p>
              </div>
              <button
                className="promo-card-btn"
                onClick={() => setActiveTab('clinical')}
              >
                Explore Clinical Tab →
              </button>
            </div>

            <div className="card">
              <div className="card-header">
                <h4>Pipeline Verification</h4>
              </div>
              <div className="card-body">
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '12px', color: '#6B6B6B' }}>Text Ingestion</span>
                    <span className="badge badge-lab_report">Active</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '12px', color: '#6B6B6B' }}>RBAC Scopes</span>
                    <span className="badge badge-prescription">Enforced</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '12px', color: '#6B6B6B' }}>Vision OCR</span>
                    <span className="badge badge-perm-contribute">Active</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '12px', color: '#6B6B6B' }}>Deterministic Engine</span>
                    <span className="badge badge-perm-view">Phase 1 Ready</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Caretaker Access Management (OWNER ONLY) */}
      {activeTab === 'caretakers' && isOwner && (
        <div className="caretakers-tab-layout">
          <div className="content-grid-two-col">
            {/* Add Caretaker Card */}
            <div className="card">
              <div className="card-header">
                <h3>Grant Caretaker Access</h3>
              </div>
              <form onSubmit={handleAddCaretaker} className="card-body">
                <div className="form-group">
                  <label htmlFor="caretakerSelect">Choose Registered Caretaker</label>
                  <select
                    id="caretakerSelect"
                    className="input-field"
                    value={selectedCaretakerUserId}
                    onChange={(e) => setSelectedCaretakerUserId(e.target.value)}
                    required
                  >
                    <option value="">-- Select Caretaker User --</option>
                    {allUsers.map(u => (
                      <option key={u.id} value={u.id}>
                        {u.name} (Caretaker)
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="permSelect">Permission Level</label>
                  <select
                    id="permSelect"
                    className="input-field"
                    value={newCaretakerPerm}
                    onChange={(e) => setNewCaretakerPerm(e.target.value)}
                  >
                    <option value="view">View (Read-only access to records)</option>
                    <option value="contribute">Contribute (Can view and upload documents)</option>
                  </select>
                </div>

                {caretakerActionError && <p className="error-text">{caretakerActionError}</p>}

                <button
                  type="submit"
                  className="btn btn-primary w-full"
                  disabled={!selectedCaretakerUserId}
                >
                  + Grant Access
                </button>
              </form>
            </div>

            {/* Caretaker Links List */}
            <div className="card">
              <div className="card-header">
                <h3>Authorized Caretakers ({caretakers.length})</h3>
              </div>
              <div className="card-body">
                {caretakers.length === 0 ? (
                  <div className="empty-state">
                    <p>No caretakers have access to your records yet.</p>
                    <p className="muted-text">Grant access to family or caretakers using the form on the left.</p>
                  </div>
                ) : (
                  <ul className="caretaker-links-list">
                    {caretakers.map((link) => {
                      const userObj = allUsers.find(u => u.id === link.caretaker_user_id);
                      const name = userObj ? userObj.name : `Caretaker (${link.caretaker_user_id.slice(0, 8)})`;
                      return (
                        <li key={link.id} className="caretaker-link-item">
                          <div className="caretaker-link-info">
                            <span className="caretaker-avatar">🧑‍⚕️</span>
                            <div>
                              <strong style={{ color: '#0A0A0A' }}>{name}</strong>
                              <div className="caretaker-perm-badge-row">
                                <span className={`badge badge-perm-${link.permission}`}>
                                  {link.permission === 'view' ? '👁️ View Only' : '✏️ Can Contribute'}
                                </span>
                                <span className="small muted-text">
                                  Granted: {new Date(link.created_at).toLocaleDateString()}
                                </span>
                              </div>
                            </div>
                          </div>

                          <div className="caretaker-link-actions">
                            <button
                              className="btn btn-secondary btn-xs"
                              onClick={() => handleTogglePermission(link)}
                              title="Toggle between View and Contribute"
                            >
                              Switch to {link.permission === 'view' ? 'Contribute' : 'View'}
                            </button>
                            <button
                              className="btn btn-danger-outline btn-xs"
                              onClick={() => handleRevokeCaretaker(link.id)}
                            >
                              Revoke
                            </button>
                          </div>
                        </li>
                      );
                    })}
                  </ul>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Clinical Intelligence Placeholders */}
      {activeTab === 'clinical' && (
        <div className="clinical-tab-layout">
          <div className="placeholder-banner">
            <h3>Clinical Synthesis & Quality Engine</h3>
            <p>Phase 0 & Auth layers are active. Fact extraction, verification, and timeline logic will populate this section.</p>
          </div>

          <div className="placeholder-cards-grid">
            {/* Facts and Timeline Placeholder */}
            <div className="card placeholder-card">
              <div className="card-header flex-between">
                <h4>Verified Facts & Medication Timeline</h4>
                <span className="tag-coming-soon">Coming soon</span>
              </div>
              <div className="card-body">
                <p className="placeholder-desc">
                  Dated clinical facts (conditions, allergies, lab values) extracted with verbatim quote verification,
                  plus lifecycle tracking for medications (started, changed, stopped).
                </p>
                <div className="placeholder-wireframe">
                  <div className="wireframe-line w-75"></div>
                  <div className="wireframe-line w-50"></div>
                </div>
              </div>
            </div>

            {/* Quality & Safety Flags Placeholder */}
            <div className="card placeholder-card">
              <div className="card-header flex-between">
                <h4>Quality & Safety Flags</h4>
                <span className="tag-coming-soon">Coming soon</span>
              </div>
              <div className="card-body">
                <p className="placeholder-desc">
                  Deterministic rule-based flags for medication conflicts, allergy contradictions, missing dates,
                  and unit discrepancies.
                </p>
                <div className="placeholder-wireframe">
                  <div className="wireframe-line w-90"></div>
                  <div className="wireframe-line w-40"></div>
                </div>
              </div>
            </div>

            {/* Grounded Q&A Box Placeholder */}
            <div className="card placeholder-card">
              <div className="card-header flex-between">
                <h4>Grounded Clinical Q&A</h4>
                <span className="tag-coming-soon">Coming soon</span>
              </div>
              <div className="card-body">
                <p className="placeholder-desc">
                  Question answering restricted strictly to extracted facts with sentence-level citations. Refuses to diagnose or provide medical advice.
                </p>
                <div className="placeholder-wireframe">
                  <div className="wireframe-line w-100"></div>
                </div>
              </div>
            </div>

            {/* Patient Summary Placeholder */}
            <div className="card placeholder-card">
              <div className="card-header flex-between">
                <h4>Patient Clinical Summary</h4>
                <span className="tag-coming-soon">Coming soon</span>
              </div>
              <div className="card-body">
                <p className="placeholder-desc">
                  Evidence-based synthesis of chronic conditions, active treatments, and recent observations.
                </p>
                <div className="placeholder-wireframe">
                  <div className="wireframe-line w-60"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
