import React, { useState, useEffect } from 'react';
import Skeleton from 'react-loading-skeleton';
import 'react-loading-skeleton/dist/skeleton.css';
import './App.css';

function App() {
  const [headlines, setHeadlines] = useState([]);
  const [loadingHeadlines, setLoadingHeadlines] = useState(true);
  const [error, setError] = useState(null);

  // Fetch headlines on mount
  useEffect(() => {
    fetchHeadlines();
  }, []);

  const fetchHeadlines = async () => {
    setLoadingHeadlines(true);
    setError(null);
    try {
      // Construct URLs using URLSearchParams
      const foxParams = new URLSearchParams({
        query: 'give me every headline on this page',
        url: 'https://www.foxnews.com/politics',
      });

      const cnnParams = new URLSearchParams({
        query: 'give me every headline on this page',
        url: 'https://www.cnn.com/election/2024',
      });

      // Fetch headlines
      const [foxResponse, cnnResponse] = await Promise.all([
        fetch(`https://lsd.so/knawledge?${foxParams.toString()}`),
        fetch(`https://lsd.so/knawledge?${cnnParams.toString()}`),
      ]);

      const [foxData, cnnData] = await Promise.all([
        foxResponse.json(),
        cnnResponse.json(),
      ]);

      // Combine and map headlines with source and placeholder for spoofed headline
      const foxHeadlinesData = foxData.results || [];
      const cnnHeadlinesData = cnnData.results || [];

      const combinedHeadlines = [
        ...foxHeadlinesData.map((h) => ({
          headline: h.headline,
          source: 'fox',
          spoofedHeadline: null,
        })),
        ...cnnHeadlinesData.map((h) => ({
          headline: h.headline,
          source: 'cnn',
          spoofedHeadline: null,
        })),
      ];

      // Remove duplicates based on the headline text
      const uniqueHeadlines = [
        ...new Map(combinedHeadlines.map((item) => [item.headline, item])).values(),
      ];

      // Set the initial headlines state
      setHeadlines(uniqueHeadlines);
      setLoadingHeadlines(false);

      // Fetch spoofed headlines individually
      uniqueHeadlines.forEach((headlineObj) => {
        fetchSpoofedHeadline(headlineObj);
      });
    } catch (error) {
      console.error('Error fetching headlines:', error);
      setError('Error loading headlines. Please try again later.');
      setLoadingHeadlines(false);
    }
  };

  // Fetch spoofed version of a headline
  const fetchSpoofedHeadline = async (headlineObj) => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/spoof-headline?headline=${encodeURIComponent(headlineObj.headline)}`
      );
      const data = await response.json();

      // Update the specific headline with its spoofed version
      setHeadlines((prevHeadlines) =>
        prevHeadlines.map((h) =>
          h.headline === headlineObj.headline ? { ...h, spoofedHeadline: data.spoofed_headline } : h
        )
      );
    } catch (error) {
      console.error('Error fetching spoofed headline:', error);
      setHeadlines((prevHeadlines) =>
        prevHeadlines.map((h) =>
          h.headline === headlineObj.headline ? { ...h, spoofedHeadline: 'Failed to spoof headline' } : h
        )
      );
    }
  };

  const retryFetch = () => {
    setError(null);
    setHeadlines([]);
    setLoadingHeadlines(true);
    fetchHeadlines();
  };

  return (
    <div className="app">
      {error ? (
        <div className="error-message">
          <p>{error}</p>
          <button onClick={retryFetch}>Retry</button>
        </div>
      ) : loadingHeadlines ? (
        <div className="skeleton-container">
          <Skeleton count={5} height={80} />
        </div>
      ) : (
        <div>
          <h1>Spoofed Headlines</h1>
          <ul className="headline-list" aria-live="polite">
            {headlines.map((headlineObj, index) => (
              <li key={index} className="headline-item">
                <div className="headline-card">
                  <span className={`source-icon ${headlineObj.source}`}>
                    {headlineObj.source.toUpperCase()}
                  </span>
                  <p className="original-headline">{headlineObj.headline}</p>
                  <p className="spoofed-headline">
                    {headlineObj.spoofedHeadline || <Skeleton width={300} />}
                  </p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
