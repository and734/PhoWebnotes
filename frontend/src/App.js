import React, { useState, useEffect, useCallback } from 'react';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import './App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [notes, setNotes] = useState([]);
  const [selectedNote, setSelectedNote] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [lastSaved, setLastSaved] = useState(null);
  const [saveTimeout, setSaveTimeout] = useState(null);

  // Rich text editor configuration
  const modules = {
    toolbar: [
      ['undo', 'redo'],
      [{ 'header': [1, 2, 3, false] }],
      ['bold', 'italic', 'underline', 'strike'],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }],
      ['blockquote', 'code-block'],
      [{ 'color': [] }, { 'background': [] }],
      ['link'],
      ['clean']
    ],
  };

  const formats = [
    'header', 'bold', 'italic', 'underline', 'strike',
    'list', 'bullet', 'blockquote', 'code-block',
    'color', 'background', 'link'
  ];

  // Fetch all notes
  const fetchNotes = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/notes`);
      setNotes(response.data);
    } catch (error) {
      console.error('Error fetching notes:', error);
    }
  }, []);

  // Auto-save functionality
  const autoSave = useCallback(async () => {
    if (!selectedNote || !title.trim()) return;

    try {
      const noteData = { title: title.trim(), content };
      
      if (selectedNote.id) {
        // Update existing note
        await axios.put(`${API}/notes/${selectedNote.id}`, noteData);
      } else {
        // Create new note
        const response = await axios.post(`${API}/notes`, noteData);
        setSelectedNote(response.data);
      }
      
      setLastSaved(new Date());
      await fetchNotes();
    } catch (error) {
      console.error('Error saving note:', error);
    }
  }, [selectedNote, title, content, fetchNotes]);

  // Debounced auto-save
  useEffect(() => {
    if (saveTimeout) {
      clearTimeout(saveTimeout);
    }

    if (selectedNote && (title.trim() || content.trim())) {
      const timeout = setTimeout(autoSave, 1000); // Save after 1 second of inactivity
      setSaveTimeout(timeout);
    }

    return () => {
      if (saveTimeout) {
        clearTimeout(saveTimeout);
      }
    };
  }, [title, content, autoSave, selectedNote]);

  // Load notes on component mount
  useEffect(() => {
    fetchNotes();
  }, [fetchNotes]);

  // Create new note
  const createNewNote = () => {
    const newNote = {
      id: null,
      title: 'Untitled Note',
      content: '',
      created_at: new Date(),
      updated_at: new Date()
    };
    setSelectedNote(newNote);
    setTitle(newNote.title);
    setContent(newNote.content);
    setIsEditing(true);
  };

  // Select note
  const selectNote = (note) => {
    setSelectedNote(note);
    setTitle(note.title);
    setContent(note.content);
    setIsEditing(false);
  };

  // Delete note
  const deleteNote = async (noteId) => {
    if (window.confirm('Are you sure you want to delete this note?')) {
      try {
        await axios.delete(`${API}/notes/${noteId}`);
        await fetchNotes();
        if (selectedNote?.id === noteId) {
          setSelectedNote(null);
          setTitle('');
          setContent('');
        }
      } catch (error) {
        console.error('Error deleting note:', error);
      }
    }
  };

  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Get note preview
  const getPreview = (content) => {
    const plainText = content.replace(/<[^>]*>/g, '');
    return plainText.length > 100 ? plainText.substring(0, 100) + '...' : plainText;
  };

  return (
    <div className="min-h-screen bg-gray-100 flex">
      {/* Sidebar */}
      <div className="w-1/3 bg-white shadow-lg border-r border-gray-200">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-800">My Notes</h1>
            <button
              onClick={createNewNote}
              className="bg-blue-600 hover:bg-blue-700 text-white p-2 rounded-lg transition-colors"
              title="Create New Note"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </button>
          </div>
        </div>

        {/* Notes List */}
        <div className="overflow-y-auto h-screen pb-32">
          {isLoading ? (
            <div className="p-6 text-center text-gray-500">Loading notes...</div>
          ) : notes.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              <p>No notes yet.</p>
              <p className="text-sm mt-2">Click the + button to create your first note!</p>
            </div>
          ) : (
            notes.map((note) => (
              <div
                key={note.id}
                className={`p-4 border-b border-gray-100 cursor-pointer hover:bg-gray-50 ${
                  selectedNote?.id === note.id ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
                }`}
                onClick={() => selectNote(note)}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-800 truncate">{note.title}</h3>
                    <p className="text-sm text-gray-600 mt-1">{getPreview(note.content)}</p>
                    <p className="text-xs text-gray-400 mt-2">{formatDate(note.updated_at)}</p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteNote(note.id);
                    }}
                    className="text-red-500 hover:text-red-700 p-1 rounded"
                    title="Delete Note"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {selectedNote ? (
          <>
            {/* Editor Header */}
            <div className="bg-white shadow-sm border-b border-gray-200 p-4">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    className="text-2xl font-bold text-gray-800 bg-transparent border-none outline-none w-full"
                    placeholder="Note title..."
                  />
                  <div className="flex items-center mt-2 text-sm text-gray-500">
                    <span>Created: {formatDate(selectedNote.created_at)}</span>
                    {selectedNote.updated_at && selectedNote.updated_at !== selectedNote.created_at && (
                      <span className="ml-4">Updated: {formatDate(selectedNote.updated_at)}</span>
                    )}
                    {lastSaved && (
                      <span className="ml-4 text-green-600">
                        Last saved: {formatDate(lastSaved)}
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="text-sm text-gray-500">
                    Auto-saving...
                  </div>
                </div>
              </div>
            </div>

            {/* Rich Text Editor */}
            <div className="flex-1 bg-white">
              <ReactQuill
                theme="snow"
                value={content}
                onChange={setContent}
                modules={modules}
                formats={formats}
                placeholder="Start writing your note..."
                className="h-full"
                style={{ height: 'calc(100vh - 120px)' }}
              />
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center bg-gray-50">
            <div className="text-center">
              <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              <h2 className="text-xl font-semibold text-gray-600 mb-2">Select a note to edit</h2>
              <p className="text-gray-500">Choose a note from the sidebar or create a new one</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;