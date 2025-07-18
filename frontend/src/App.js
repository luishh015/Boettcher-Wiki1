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
  const [loading, setLoading] = useState(false);
  const [expandedEntryId, setExpandedEntryId] = useState(null);

  // Form state
  const [newEntry, setNewEntry] = useState({
    question: '',
    answer: '',
    category: '',
    tags: []
  });

  useEffect(() => {
    fetchKnowledgeEntries();
    fetchCategories();
    fetchStats();
  }, []);

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
      const tagsArray = newEntry.tags.length > 0 ? newEntry.tags.split(',').map(tag => tag.trim()) : [];
      
      const response = await fetch(`${BACKEND_URL}/api/knowledge`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
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
      }
    } catch (error) {
      console.error('Error adding entry:', error);
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
              <div className="bg-blue-600 text-white p-3 rounded-full">
                <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-800">Böttcher Wiki</h1>
                <p className="text-blue-600 font-medium">Fahrradmanufaktur Wissensdatenbank</p>
              </div>
            </div>
            <div className="hidden md:block">
              <img 
                src="https://images.unsplash.com/photo-1570169043013-de63774bbf97?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NjZ8MHwxfHNlYXJjaHwyfHxiaWN5Y2xlJTIwbWFudWZhY3R1cmluZ3xlbnwwfHx8Ymx1ZXwxNzUyODU0NjczfDA&ixlib=rb-4.1.0&q=85" 
                alt="Böttcher Bikes" 
                className="w-32 h-20 object-cover rounded-lg shadow-md"
              />
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div className="bg-white rounded-lg p-6 shadow-md border-l-4 border-blue-500">
            <div className="flex items-center">
              <div className="bg-blue-500 text-white p-3 rounded-full mr-4">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
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
              <div className="bg-green-500 text-white p-3 rounded-full mr-4">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M19 11H5l5-5-1.5-1.5L2 11l6.5 6.5L10 16l-5-5h14v-0z"/>
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
                <path d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"/>
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

        {/* Admin Add Entry Button */}
        <div className="mb-6">
          <button
            onClick={() => setShowAddEntry(true)}
            className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors shadow-md"
          >
            ➕ Neue Frage/Antwort hinzufügen
          </button>
        </div>

        {/* Knowledge Entries */}
        <div className="space-y-4">
          {knowledgeEntries.length === 0 ? (
            <div className="bg-white rounded-lg shadow-md p-8 text-center">
              <div className="text-gray-500">
                <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
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

      {/* Add Entry Modal */}
      {showAddEntry && (
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