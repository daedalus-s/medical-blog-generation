import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import { motion, AnimatePresence } from 'framer-motion';
import { FaSearch, FaSpinner } from 'react-icons/fa';

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
  const [showForm, setShowForm] = useState(true);

  useEffect(() => {
    const canvas = document.getElementById('bgAnimation');
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    const waves = [
      { y: canvas.height * 0.6, length: 0.01, amplitude: 40, speed: 0.02 },
      { y: canvas.height * 0.65, length: 0.012, amplitude: 30, speed: 0.03 },
      { y: canvas.height * 0.7, length: 0.015, amplitude: 20, speed: 0.04 }
    ];

    const drawWave = (wave, time) => {
      ctx.beginPath();
      ctx.moveTo(0, wave.y);

      for (let x = 0; x < canvas.width; x++) {
        const dx = x * wave.length;
        const y = wave.y + Math.sin(dx + time * wave.speed) * wave.amplitude;
        ctx.lineTo(x, y);
      }

      ctx.lineTo(canvas.width, canvas.height);
      ctx.lineTo(0, canvas.height);
      ctx.closePath();

      const gradient = ctx.createLinearGradient(0, wave.y - wave.amplitude, 0, wave.y + wave.amplitude);
      gradient.addColorStop(0, 'rgba(100, 200, 255, 0.8)');
      gradient.addColorStop(1, 'rgba(50, 150, 220, 0.6)');
      ctx.fillStyle = gradient;
      ctx.fill();
    };

    const animate = (time) => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw sky
      const skyGradient = ctx.createLinearGradient(0, 0, 0, canvas.height * 0.6);
      skyGradient.addColorStop(0, '#87CEEB');
      skyGradient.addColorStop(1, '#E0F6FF');
      ctx.fillStyle = skyGradient;
      ctx.fillRect(0, 0, canvas.width, canvas.height * 0.6);

      // Draw sand
      ctx.fillStyle = '#F0E68C';
      ctx.fillRect(0, canvas.height * 0.7, canvas.width, canvas.height * 0.3);

      waves.forEach(wave => drawWave(wave, time * 0.001));

      animationFrameId = requestAnimationFrame(animate);
    };

    animate(0);

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setBlogPost('');
    setBlogImage('');
    setShowForm(false);

    try {
      const response = await api.post('/', { drugName, drugDetails });
      
      if (response.data && response.data.blogPost) {
        setBlogPost(response.data.blogPost);
        if (response.data.blogImage) {
          setBlogImage(response.data.blogImage);
        }
      } else {
        throw new Error('Blog post not found in response data');
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
      <canvas id="bgAnimation" />
      <motion.div 
        className="content"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1 }}
      >
        <motion.h1 
          className="title"
          initial={{ y: -50 }}
          animate={{ y: 0 }}
          transition={{ type: "spring", stiffness: 100 }}
        >
          MedBlogGen: AI-Powered Drug Blog Generator
        </motion.h1>

        <AnimatePresence>
          {showForm && (
            <motion.form 
              onSubmit={handleSubmit}
              className="form"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
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
                {loading ? <FaSpinner className="spinner" /> : <><FaSearch /> Generate Blog Post</>}
              </motion.button>
            </motion.form>
          )}
        </AnimatePresence>

        {error && (
          <motion.div 
            className="error"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            {error}
          </motion.div>
        )}

        {loading && (
          <motion.div 
            className="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            <FaSpinner className="spinner" /> Generating blog post and image, please wait...
          </motion.div>
        )}

        <AnimatePresence>
          {blogPost && (
            <motion.div 
              className="blog-post"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
            >
              <h2>Generated Blog Post</h2>
              <div dangerouslySetInnerHTML={{ __html: blogPost.replace(/\n/g, '<br>') }} />
              {blogImage && (
                <motion.div 
                  className="blog-image"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.5, delay: 0.2 }}
                >
                  <img src={`data:image/png;base64,${blogImage}`} alt="Blog post illustration" />
                </motion.div>   
              )}
              <motion.button
                onClick={() => setShowForm(true)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Generate Another Blog Post
              </motion.button>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}

export default App;