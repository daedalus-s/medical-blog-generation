// src/components/BlogForm.js
import React, { useState } from 'react';
import axios from 'axios';

function BlogForm() {
  const [drugName, setDrugName] = useState('');
  const [drugDetails, setDrugDetails] = useState('');
  const [blogPost, setBlogPost] = useState('');
  const [blogImage, setBlogImage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await axios.post('/api/generate-blog', { drugName, drugDetails });
      setBlogPost(response.data.blogPost);
      setBlogImage(`data:image/png;base64,${response.data.blogImage}`);
    } catch (error) {
      console.error('Error:', error);
      alert('An error occurred while generating the blog. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="blog-form">
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="drug-name">Drug Name:</label>
          <input
            type="text"
            id="drug-name"
            value={drugName}
            onChange={(e) => setDrugName(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="drug-details">Drug Details and History:</label>
          <textarea
            id="drug-details"
            value={drugDetails}
            onChange={(e) => setDrugDetails(e.target.value)}
            required
          />
        </div>
        <button type="submit" disabled={isLoading}>
          Generate Blog
        </button>
      </form>

      {isLoading && <div className="loading">Generating blog post and image...</div>}

      {blogPost && (
        <div className="blog-result">
          <h2>Generated Blog Post</h2>
          <div dangerouslySetInnerHTML={{ __html: blogPost }} />
          <h3>Generated Image</h3>
          <img src={blogImage} alt="Generated blog image" />
        </div>
      )}
    </div>
  );
}

export default BlogForm;