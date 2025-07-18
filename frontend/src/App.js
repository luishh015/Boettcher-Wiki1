import React, { useState, useEffect } from 'react';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function App() {
  const [questions, setQuestions] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [categories, setCategories] = useState([]);
  const [stats, setStats] = useState({});
  const [showAddQuestion, setShowAddQuestion] = useState(false);
  const [showAddAnswer, setShowAddAnswer] = useState(false);
  const [selectedQuestionId, setSelectedQuestionId] = useState('');
  const [loading, setLoading] = useState(false);

  // Form states
  const [newQuestion, setNewQuestion] = useState({
    question_text: '',
    category: '',
    author: '',
    tags: []
  });
  const [newAnswer, setNewAnswer] = useState({
    answer_text: '',
    author: ''
  });

  useEffect(() => {
    fetchQuestions();
    fetchCategories();
    fetchStats();
  }, []);

  const fetchQuestions = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/questions`);
      const data = await response.json();
      setQuestions(data);
    } catch (error) {
      console.error('Error fetching questions:', error);
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
    if (!searchQuery.trim()) {
      fetchQuestions();
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
      setQuestions(data);
    } catch (error) {
      console.error('Error searching questions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddQuestion = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const tagsArray = newQuestion.tags.length > 0 ? newQuestion.tags.split(',').map(tag => tag.trim()) : [];
      
      const response = await fetch(`${BACKEND_URL}/api/questions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...newQuestion,
          tags: tagsArray
        })
      });
      
      if (response.ok) {
        setNewQuestion({ question_text: '', category: '', author: '', tags: [] });
        setShowAddQuestion(false);
        fetchQuestions();
        fetchStats();
      }
    } catch (error) {
      console.error('Error adding question:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddAnswer = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/questions/${selectedQuestionId}/answer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newAnswer)
      });
      
      if (response.ok) {
        setNewAnswer({ answer_text: '', author: '' });
        setShowAddAnswer(false);
        setSelectedQuestionId('');
        fetchQuestions();
        fetchStats();
      }
    } catch (error) {
      console.error('Error adding answer:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredQuestions = questions.filter(qa => 
    selectedCategory ? qa.question.category === selectedCategory : true
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100">
      {/* Header */}
      <header className="bg-white shadow-lg border-b-4 border-blue-600">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="bg-blue-600 text-white p-3 rounded-full">
                <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10 2L3 7v11h4v-6h6v6h4V7l-7-5z"/>
                </svg>
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-800">Böttcher Wiki</h1>
                <p className="text-blue-600 font-medium">Fahrradmanufaktur Wissensdatenbank</p>
              </div>
            </div>
            <div className="hidden md:block">
              <img 
                src="https://images.unsplash.com/photo-1612767651852-be62cd23ab65?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NjZ8MHwxfHNlYXJjaHwxfHxiaWN5Y2xlJTIwbWFudWZhY3R1cmluZ3xlbnwwfHx8Ymx1ZXwxNzUyODU0NjczfDA&ixlib=rb-4.1.0&q=85" 
                alt="Böttcher Bikes" 
                className="w-32 h-20 object-cover rounded-lg shadow-md"
              />
            </div>
          </div>
        </div>
      </header>

      {/* Stats Dashboard */}
      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-lg p-6 shadow-md border-l-4 border-blue-500">
            <div className="flex items-center">
              <div className="bg-blue-500 text-white p-3 rounded-full mr-4">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Gesamt Fragen</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_questions || 0}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg p-6 shadow-md border-l-4 border-green-500">
            <div className="flex items-center">
              <div className="bg-green-500 text-white p-3 rounded-full mr-4">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Beantwortet</p>
                <p className="text-2xl font-bold text-gray-900">{stats.answered_questions || 0}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg p-6 shadow-md border-l-4 border-orange-500">
            <div className="flex items-center">
              <div className="bg-orange-500 text-white p-3 rounded-full mr-4">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Offen</p>
                <p className="text-2xl font-bold text-gray-900">{stats.unanswered_questions || 0}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Search and Filter */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
            <div className="flex-1 flex gap-4">
              <div className="flex-1">
                <input
                  type="text"
                  placeholder="Suche nach Fragen..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <div>
                <select
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                >
                  <option value="">Alle Kategorien</option>
                  {categories.map(category => (
                    <option key={category} value={category}>{category}</option>
                  ))}
                </select>
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
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4 mb-6">
          <button
            onClick={() => setShowAddQuestion(true)}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            Neue Frage hinzufügen
          </button>
          <button
            onClick={() => setShowAddAnswer(true)}
            className="px-6 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
          >
            Antwort hinzufügen
          </button>
        </div>

        {/* Questions List */}
        <div className="space-y-4">
          {filteredQuestions.length === 0 ? (
            <div className="bg-white rounded-lg shadow-md p-8 text-center">
              <div className="text-gray-500">
                <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                <p className="text-lg font-medium mb-2">Noch keine Fragen vorhanden</p>
                <p className="text-gray-400">Fügen Sie die erste Frage hinzu, um die Wissensdatenbank zu starten.</p>
              </div>
            </div>
          ) : (
            filteredQuestions.map(qa => (
              <div key={qa.question.id} className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-800 mb-2">{qa.question.question_text}</h3>
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <span className="flex items-center">
                        <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                        {qa.question.category}
                      </span>
                      <span className="flex items-center">
                        <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                        </svg>
                        {qa.question.author}
                      </span>
                      <span className="flex items-center">
                        <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M12 8l-3 3 3 3m-6-6l3 3-3 3"/>
                        </svg>
                        {new Date(qa.question.created_at).toLocaleDateString('de-DE')}
                      </span>
                    </div>
                    {qa.question.tags.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-2">
                        {qa.question.tags.map(tag => (
                          <span key={tag} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="flex items-center space-x-2">
                    {qa.question.answered ? (
                      <span className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
                        ✓ Beantwortet
                      </span>
                    ) : (
                      <span className="px-3 py-1 bg-orange-100 text-orange-800 text-sm rounded-full">
                        ⏳ Offen
                      </span>
                    )}
                  </div>
                </div>
                
                {qa.answer && (
                  <div className="mt-4 p-4 bg-green-50 rounded-lg border-l-4 border-green-500">
                    <h4 className="font-medium text-green-800 mb-2">Antwort:</h4>
                    <p className="text-gray-800 mb-2">{qa.answer.answer_text}</p>
                    <div className="text-sm text-gray-600">
                      <span className="mr-4">von {qa.answer.author}</span>
                      <span>{new Date(qa.answer.created_at).toLocaleDateString('de-DE')}</span>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Add Question Modal */}
      {showAddQuestion && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Neue Frage hinzufügen</h3>
            <form onSubmit={handleAddQuestion}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Frage</label>
                <textarea
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows="3"
                  value={newQuestion.question_text}
                  onChange={(e) => setNewQuestion({...newQuestion, question_text: e.target.value})}
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Kategorie</label>
                <input
                  required
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={newQuestion.category}
                  onChange={(e) => setNewQuestion({...newQuestion, category: e.target.value})}
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Ihr Name</label>
                <input
                  required
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={newQuestion.author}
                  onChange={(e) => setNewQuestion({...newQuestion, author: e.target.value})}
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Tags (kommagetrennt)</label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={newQuestion.tags}
                  onChange={(e) => setNewQuestion({...newQuestion, tags: e.target.value})}
                />
              </div>
              <div className="flex gap-4">
                <button
                  type="button"
                  onClick={() => setShowAddQuestion(false)}
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

      {/* Add Answer Modal */}
      {showAddAnswer && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Antwort hinzufügen</h3>
            <form onSubmit={handleAddAnswer}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Frage auswählen</label>
                <select
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={selectedQuestionId}
                  onChange={(e) => setSelectedQuestionId(e.target.value)}
                >
                  <option value="">Wählen Sie eine Frage...</option>
                  {questions.filter(qa => !qa.answer).map(qa => (
                    <option key={qa.question.id} value={qa.question.id}>
                      {qa.question.question_text.substring(0, 50)}...
                    </option>
                  ))}
                </select>
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Antwort</label>
                <textarea
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows="4"
                  value={newAnswer.answer_text}
                  onChange={(e) => setNewAnswer({...newAnswer, answer_text: e.target.value})}
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Ihr Name</label>
                <input
                  required
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={newAnswer.author}
                  onChange={(e) => setNewAnswer({...newAnswer, author: e.target.value})}
                />
              </div>
              <div className="flex gap-4">
                <button
                  type="button"
                  onClick={() => setShowAddAnswer(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Abbrechen
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors disabled:opacity-50"
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