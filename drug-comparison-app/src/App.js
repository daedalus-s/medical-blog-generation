import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [drugName, setDrugName] = useState('');
  const [drugDetails, setDrugDetails] = useState('');
  const [blogPost, setBlogPost] = useState('');
  const [blogImage, setBlogImage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setBlogPost('');
    setBlogImage('');

    try {
      const response = await axios.post('https://0pnd965v02.execute-api.us-east-1.amazonaws.com/prod', {
        drugName,
        drugDetails
      });
      setBlogPost(response.data.blogPost);
      setBlogImage(response.data.blogImage);
    } catch (error) {
      setError('An error occurred while generating the blog post. Please try again.');
      console.error('Error:', error);
    }
    setLoading(false);
  };

  return (
    <div className="App">
      <h1>Drug Comparison Blog Generator</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={drugName}
          onChange={(e) => setDrugName(e.target.value)}
          placeholder="Enter drug name"
          required
        />
        <textarea
          value={drugDetails}
          onChange={(e) => setDrugDetails(e.target.value)}
          placeholder="Enter drug details"
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Generating...' : 'Generate Blog Post'}
        </button>
      </form>
      {error && <p className="error">{error}</p>}
      {blogPost && (
        <div className="blog-post">
          <h2>Generated Blog Post</h2>
          <div dangerouslySetInnerHTML={{ __html: blogPost }} />
        </div>
      )}
      {blogImage && (
        <div className="blog-image">
          <h2>Generated Image</h2>
          <img src={`data:image/png;base64,${blogImage}`} alt="Blog post illustration" />
        </div>
      )}
    </div>
  );
}

export default App;