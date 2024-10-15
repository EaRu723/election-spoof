import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [headlines, setHeadlines] = useState({ fox: [], cnn: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [spoofing, setSpoofing] = useState(false);
  const fetchedRef = useRef(false);
  const [headlinesFetched, setHeadlinesFetched] = useState(false);
  const [headlinesSpoofed, setHeadlinesSpoofed] = useState(false);

  useEffect(() => {
    if (!headlinesFetched) {
      fetchHeadlines();
    }
  }, [headlinesFetched]);

  useEffect(() => {
    if (headlinesFetched && !headlinesSpoofed && headlines.fox.length > 0 || headlines.cnn.length > 0) {
      const allHeadlines = [...headlines.fox, ...headlines.cnn];
      spoofedHeadlines(allHeadlines);
      setHeadlinesSpoofed(true);
  }
}, [headlinesFetched]);

  const fetchHeadlines = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/fetch-headlines');
      if (!response.ok) throw new Error('Failed to fetch headlines');
      const data = await response.json();
      setHeadlines({
        fox: data.fox_headlines,
        cnn: data.cnn_headlines
      });
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
      setHeadlinesFetched(true);
    }
  };

  const spoofHeadlines = async (allHeadlines) => {
    setSpoofing(true);
    for (const headline of allHeadlines) {
      try {
        const response = await fetch(`http://127.0.0.1:8000/spoof-headline?headline=${encodeURIComponent(headline.headline)}`);
        const data = await response.json();
        setHeadlines(prev => {
          const source = headline.source;
          const index = prev[source].findIndex(h => h.headline === headline.headline);
          const updatedSource = [...prev[source]];
          updatedSource[index] = { ...updatedSource[index], spoofedHeadline: data.spoofed_headline };
          return { ...prev, [source]: updatedSource };
        });
      } catch (error) {
        console.error('Error spoofing headline:', error);
      }
    }
    setSpoofing(false);
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (spoofing) return <div>Spoofing headlines...</div>;


  return (
    <div className="app">
      <h1>Spoofed Headlines</h1>
      {['fox', 'cnn'].map(source => (
        <div key={source}>
          <h2>{source === 'fox' ? 'Fox News' : 'CNN'}</h2>
          <ul>
            {headlines[source].map((headline, index) => (
              <li key={index}>
                <p>Original: {headline.headline}</p>
                <p>Spoofed: {headline.spoofedHeadline || 'Spoofing...'}</p>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

export default App;
