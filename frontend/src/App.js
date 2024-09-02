import React from 'react';
import BlogForm from './components/BlogForm';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Medical Blog Generator</h1>
      </header>
      <main>
        <BlogForm />
      </main>
    </div>
  );
}

export default App;