import React, { useState } from 'react';
import axios from 'axios';
import './App.css';
import { motion } from 'framer-motion';

const api = axios.create({
  baseURL: 'https://r1vyi7eqc5.execute-api.us-east-1.amazonaws.com/prod/generate-blog',
  headers: {
    'Content-Type': 'application/json',
  }
});

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
      console.log('Sending request with data:', { drugName, drugDetails });
      
      const response = await api.post('/', {
        drugName,
        drugDetails
      });
      
      console.log('Full API response:', response);
      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);
      console.log('Response data type:', typeof response.data);
      console.log('Response data:', JSON.stringify(response.data, null, 2));
      
      if (response.data) {
        if (response.data.statusCode === 200 && response.data.body) {
          try {
            const parsedBody = JSON.parse(response.data.body);
            if (parsedBody.blogPost) {
              setBlogPost(parsedBody.blogPost);
              if (parsedBody.blogImage) {
                setBlogImage(parsedBody.blogImage);
              }
            } else {
              throw new Error('Blog post not found in parsed body');
            }
          } catch (parseError) {
            console.error('Error parsing response body as JSON:', parseError);
            throw new Error('Invalid response format');
          }
        } else if (response.data.statusCode >= 400) {
          throw new Error(response.data.body ? JSON.parse(response.data.body).error : 'Unknown error occurred');
        } else {
          throw new Error('Unexpected response structure');
        }
      } else {
        throw new Error('No data in response');
      }
    } catch (error) {
      console.error('Error details:', error);
      setError(error.message || 'An error occurred while generating the blog post.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <motion.div 
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, ease: 'easeOut' }}
        className="header"
      >
        <h1>Drug Comparison Blog Generator</h1>
      </motion.div>

      <motion.form 
        onSubmit={handleSubmit}
        initial={{ x: -100, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.8, ease: 'easeOut', delay: 0.2 }}
        className="form"
      >
        <div className="form-group">
          <label htmlFor="drugName">Drug Name:</label>
          <input
            type="text"
            id="drugName"
            value={drugName}
            onChange={(e) => setDrugName(e.target.value)}
            placeholder="Enter drug name"
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="drugDetails">Drug Details:</label>
          <textarea
            id="drugDetails"
            value={drugDetails}
            onChange={(e) => setDrugDetails(e.target.value)}
            placeholder="Enter drug details and history"
            required
          />
        </div>
        <motion.button 
          type="submit" 
          disabled={loading}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          {loading ? 'Generating...' : 'Generate Blog Post'}
        </motion.button>
      </motion.form>

      {error && <p className="error">{error}</p>}

      {loading && <p>Generating blog post and image, please wait...</p>}

      {blogPost && (
        <motion.div 
          className="blog-post"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, ease: 'easeOut', delay: 0.2 }}
        >
          <h2>Generated Blog Post</h2>
          <div dangerouslySetInnerHTML={{ __html: blogPost }} />
        </motion.div>
      )}

      {blogImage && (
        <motion.div 
          className="blog-image"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, ease: 'easeOut', delay: 0.4 }}
        >
          <h2>Generated Image</h2>
          <img src={`data:image/png;base64,${blogImage}`} alt="Blog post illustration" />
        </motion.div>   
      )}
    </div>
  );
}

export default App;