import React, { useState } from 'react';
import axios from 'axios';
import TripForm from './components/TripForm';
import MapDisplay from './components/MapDisplay';
import './index.css';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGenerateValues = async (data) => {
    setLoading(true);
    setError(null);
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL;
      if (!baseUrl) {
        throw new Error("VITE_API_BASE_URL is not defined");
      }
      const response = await axios.post(`${baseUrl}/generate-plan/`, data);
      setResult(response.data);
    } catch (err) {
      console.error(err);
      setError("Failed to generate plan. Please check inputs and server connection.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="sidebar">
        <header>
          <h1>DriverLog Pro</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Automated Trip Planning & HOS Compliance</p>
        </header>

        <TripForm onSubmit={handleGenerateValues} isLoading={loading} />

        {error && (
          <div className="card" style={{ borderColor: 'var(--danger)', color: 'var(--danger)' }}>
            {error}
          </div>
        )}

        {result && (
          <div className="result-section">
            <div className="card" style={{ marginBottom: '2rem' }}>
              <h2>Itinerary</h2>
              {/* PDF Download Button */}
              {result.pdf_blob && (
                <a
                  href={`data:application/pdf;base64,${result.pdf_blob}`}
                  download="driver_logs.pdf"
                  className="download-btn"
                  style={{
                    display: 'block',
                    textAlign: 'center',
                    padding: '10px',
                    backgroundColor: 'var(--accent-color)',
                    color: 'white',
                    textDecoration: 'none',
                    borderRadius: '4px',
                    marginBottom: '1rem'
                  }}
                >
                  📄 Download Full Logs (PDF)
                </a>
              )}

              <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                {result.itinerary.map((item, idx) => (
                  <div key={idx} className="itinerary-item">
                    <span style={{ color: 'var(--accent-color)' }}>●</span>
                    {item}
                  </div>
                ))}
              </div>
            </div>

            <div className="card">
              <h2>Generated Logs</h2>
              {result.log_images.map((imgSrc, idx) => (
                <div key={idx}>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Day {idx + 1}</p>
                  <img src={imgSrc} alt={`Log Day ${idx + 1}`} className="log-image" />
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="main-content">
        <MapDisplay routeGeometry={result?.route_geometry} />
      </div>
    </div>
  );
}

export default App;
