import React, { useState, useEffect } from 'react';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function App() {
  const [knowledgeEntries, setKnowledgeEntries] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [categories, setCategories] = useState([]);
  const [stats, setStats] = useState({});
  const [showAddEntry, setShowAddEntry] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const [loading, setLoading] = useState(false);
  const [expandedEntryId, setExpandedEntryId] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [adminUser, setAdminUser] = useState('');

  // Form states
  const [newEntry, setNewEntry] = useState({
    question: '',
    answer: '',
    category: '',
    tags: []
  });

  const [loginData, setLoginData] = useState({
    username: '',
    password: ''
  });

  useEffect(() => {
    fetchKnowledgeEntries();
    fetchCategories();
    fetchStats();
    checkAdminStatus();
  }, []);

  const checkAdminStatus = async () => {
    const token = localStorage.getItem('admin_token');
    if (token) {
      try {
        const response = await fetch(`${BACKEND_URL}/api/admin/verify`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          setIsAdmin(true);
          setAdminUser(data.username);
        } else {
          localStorage.removeItem('admin_token');
        }
      } catch (error) {
        console.error('Error verifying admin status:', error);
        localStorage.removeItem('admin_token');
      }
    }
  };

  const fetchKnowledgeEntries = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/knowledge`);
      const data = await response.json();
      setKnowledgeEntries(data);
    } catch (error) {
      console.error('Error fetching knowledge entries:', error);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/categories`);
      const data = await response.json();
      setCategories(data.categories);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/stats`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/admin/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(loginData)
      });
      
      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('admin_token', data.access_token);
        setIsAdmin(true);
        setAdminUser(data.username);
        setShowLogin(false);
        setLoginData({ username: '', password: '' });
      } else {
        alert('Ungültige Anmeldedaten');
      }
    } catch (error) {
      console.error('Error during login:', error);
      alert('Anmeldung fehlgeschlagen');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    setIsAdmin(false);
    setAdminUser('');
  };

  const handleSearch = async () => {
    if (!searchQuery.trim() && !selectedCategory) {
      fetchKnowledgeEntries();
      return;
    }
    
    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery,
          category: selectedCategory || null
        })
      });
      const data = await response.json();
      setKnowledgeEntries(data);
    } catch (error) {
      console.error('Error searching knowledge:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCategoryFilter = (category) => {
    setSelectedCategory(category);
    setSearchQuery('');
    if (category) {
      setLoading(true);
      fetch(`${BACKEND_URL}/api/knowledge?category=${category}`)
        .then(response => response.json())
        .then(data => {
          setKnowledgeEntries(data);
          setLoading(false);
        })
        .catch(error => {
          console.error('Error filtering by category:', error);
          setLoading(false);
        });
    } else {
      fetchKnowledgeEntries();
    }
  };

  const handleAddEntry = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const token = localStorage.getItem('admin_token');
      const tagsArray = newEntry.tags.length > 0 ? newEntry.tags.split(',').map(tag => tag.trim()) : [];
      
      const response = await fetch(`${BACKEND_URL}/api/knowledge`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          ...newEntry,
          tags: tagsArray
        })
      });
      
      if (response.ok) {
        setNewEntry({ question: '', answer: '', category: '', tags: [] });
        setShowAddEntry(false);
        fetchKnowledgeEntries();
        fetchCategories();
        fetchStats();
      } else {
        alert('Fehler beim Hinzufügen des Eintrags');
      }
    } catch (error) {
      console.error('Error adding entry:', error);
      alert('Fehler beim Hinzufügen des Eintrags');
    } finally {
      setLoading(false);
    }
  };

  const toggleExpanded = (entryId) => {
    setExpandedEntryId(expandedEntryId === entryId ? null : entryId);
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'IT-Support':
        return '💻';
      case 'Produktion':
        return '🔧';
      case 'Qualitätskontrolle':
        return '🔍';
      case 'Verwaltung':
        return '📋';
      case 'Wartung':
        return '⚙️';
      default:
        return '📘';
    }
  };

  const getCategoryColor = (category) => {
    switch (category) {
      case 'IT-Support':
        return 'bg-blue-100 text-blue-800 border-blue-500';
      case 'Produktion':
        return 'bg-green-100 text-green-800 border-green-500';
      case 'Qualitätskontrolle':
        return 'bg-purple-100 text-purple-800 border-purple-500';
      case 'Verwaltung':
        return 'bg-orange-100 text-orange-800 border-orange-500';
      case 'Wartung':
        return 'bg-red-100 text-red-800 border-red-500';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-500';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-lg border-b-4 border-blue-600">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-3 rounded-full">
                <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-800">Böttcher Wiki</h1>
                <p className="text-blue-600 font-medium">Fahrradmanufaktur Wissensdatenbank</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="hidden md:block">
                <img 
                  src="https://images.unsplash.com/photo-1606857521015-7f9fcf423740?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODF8MHwxfHNlYXJjaHwxfHxwcm9mZXNzaW9uYWwlMjBvZmZpY2V8ZW58MHx8fHwxNzUyODU2MTI2fDA&ixlib=rb-4.1.0&q=85" 
                  alt="Professional Office" 
                  className="w-32 h-20 object-cover rounded-lg shadow-md"
                />
              </div>
              {isAdmin ? (
                <div className="flex items-center space-x-3">
                  <span className="text-sm font-medium text-gray-700">
                    👨‍💼 {adminUser}
                  </span>
                  <button
                    onClick={handleLogout}
                    className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                  >
                    Abmelden
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setShowLogin(true)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  🔐 Admin Login
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div className="bg-white rounded-lg p-6 shadow-md border-l-4 border-blue-500">
            <div className="flex items-center">
              <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-3 rounded-full mr-4">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z"/>
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Gesamt Einträge</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_entries || 0}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg p-6 shadow-md border-l-4 border-green-500">
            <div className="flex items-center">
              <div className="bg-gradient-to-r from-green-500 to-green-600 text-white p-3 rounded-full mr-4">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Kategorien</p>
                <p className="text-2xl font-bold text-gray-900">{stats.categories_count || 0}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Category Filter Buttons */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">Nach Kategorie filtern</h3>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => handleCategoryFilter('')}
              className={`px-4 py-2 rounded-full transition-colors ${
                selectedCategory === '' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              🏠 Alle
            </button>
            {categories.map(category => (
              <button
                key={category}
                onClick={() => handleCategoryFilter(category)}
                className={`px-4 py-2 rounded-full transition-colors ${
                  selectedCategory === category 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {getCategoryIcon(category)} {category}
              </button>
            ))}
          </div>
        </div>

        {/* Search Bar */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <input
                type="text"
                placeholder="Suche nach Fragen oder Lösungen..."
                className="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <svg className="w-5 h-5 absolute left-3 top-2.5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
              </svg>
            </div>
            <button
              onClick={handleSearch}
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {loading ? 'Suche...' : 'Suchen'}
            </button>
          </div>
        </div>

        {/* Admin Add Entry Button - nur für eingeloggte Admins */}
        {isAdmin && (
          <div className="mb-6">
            <button
              onClick={() => setShowAddEntry(true)}
              className="px-6 py-3 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg hover:from-green-700 hover:to-green-800 transition-all transform hover:scale-105 shadow-md"
            >
              ➕ Neue Frage/Antwort hinzufügen
            </button>
          </div>
        )}

        {/* Knowledge Entries */}
        <div className="space-y-4">
          {knowledgeEntries.length === 0 ? (
            <div className="bg-white rounded-lg shadow-md p-8 text-center">
              <div className="text-gray-500">
                <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z"/>
                </svg>
                <p className="text-lg font-medium mb-2">Keine Einträge gefunden</p>
                <p className="text-gray-400">Versuchen Sie andere Suchbegriffe oder wählen Sie eine andere Kategorie.</p>
              </div>
            </div>
          ) : (
            knowledgeEntries.map(entry => (
              <div key={entry.id} className={`bg-white rounded-lg shadow-md p-6 border-l-4 transition-all duration-200 hover:shadow-lg ${getCategoryColor(entry.category).split(' ')[2]}`}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center mb-3">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getCategoryColor(entry.category)}`}>
                        {getCategoryIcon(entry.category)} {entry.category}
                      </span>
                    </div>
                    <h3 className="text-xl font-semibold text-gray-800 mb-3">{entry.question}</h3>
                    
                    {/* Tags */}
                    {entry.tags.length > 0 && (
                      <div className="flex flex-wrap gap-2 mb-3">
                        {entry.tags.map(tag => (
                          <span key={tag} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                            #{tag}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* Answer - Expandable */}
                    <div className="mb-3">
                      <div className={`text-gray-700 ${expandedEntryId === entry.id ? '' : 'line-clamp-3'}`}>
                        {entry.answer.split('\n').map((line, index) => (
                          <div key={index} className="mb-1">{line}</div>
                        ))}
                      </div>
                      {entry.answer.length > 150 && (
                        <button
                          onClick={() => toggleExpanded(entry.id)}
                          className="text-blue-600 hover:text-blue-800 text-sm font-medium mt-2"
                        >
                          {expandedEntryId === entry.id ? '▲ Weniger anzeigen' : '▼ Mehr anzeigen'}
                        </button>
                      )}
                    </div>

                    <div className="text-sm text-gray-500">
                      Erstellt: {new Date(entry.created_at).toLocaleDateString('de-DE')}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Login Modal */}
      {showLogin && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-xl font-semibold mb-4">🔐 Admin-Anmeldung</h3>
            <form onSubmit={handleLogin}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Benutzername</label>
                <input
                  required
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={loginData.username}
                  onChange={(e) => setLoginData({...loginData, username: e.target.value})}
                />
              </div>
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">Passwort</label>
                <input
                  required
                  type="password"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={loginData.password}
                  onChange={(e) => setLoginData({...loginData, password: e.target.value})}
                />
              </div>
              <div className="flex gap-4">
                <button
                  type="button"
                  onClick={() => setShowLogin(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Abbrechen
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                >
                  {loading ? 'Anmelden...' : 'Anmelden'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Entry Modal - nur für Admins */}
      {showAddEntry && isAdmin && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-xl font-semibold mb-4">Neue Frage/Antwort hinzufügen</h3>
            <form onSubmit={handleAddEntry}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Frage</label>
                <input
                  required
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={newEntry.question}
                  onChange={(e) => setNewEntry({...newEntry, question: e.target.value})}
                  placeholder="z.B. Was tun wenn der Scanner nicht funktioniert?"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Antwort/Lösung</label>
                <textarea
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows="8"
                  value={newEntry.answer}
                  onChange={(e) => setNewEntry({...newEntry, answer: e.target.value})}
                  placeholder="Detaillierte Schritt-für-Schritt Anleitung..."
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Kategorie</label>
                <select
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={newEntry.category}
                  onChange={(e) => setNewEntry({...newEntry, category: e.target.value})}
                >
                  <option value="">Kategorie auswählen</option>
                  <option value="IT-Support">💻 IT-Support</option>
                  <option value="Produktion">🔧 Produktion</option>
                  <option value="Qualitätskontrolle">🔍 Qualitätskontrolle</option>
                  <option value="Verwaltung">📋 Verwaltung</option>
                  <option value="Wartung">⚙️ Wartung</option>
                </select>
              </div>
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">Tags (kommagetrennt)</label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={newEntry.tags}
                  onChange={(e) => setNewEntry({...newEntry, tags: e.target.value})}
                  placeholder="z.B. scanner, hardware, fehlerbehebung"
                />
              </div>
              <div className="flex gap-4">
                <button
                  type="button"
                  onClick={() => setShowAddEntry(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Abbrechen
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                >
                  {loading ? 'Hinzufügen...' : 'Hinzufügen'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;