import React, { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingResult, setProcessingResult] = useState(null);
  const [error, setError] = useState(null);
  const [processingStatus, setProcessingStatus] = useState(null);
  const [jobId, setJobId] = useState(null);
  
  const fileInputRef = useRef(null);
  const audioRef = useRef(null);

  const API_BASE_URL = 'http://localhost:8000';

  // Poll for status updates
  useEffect(() => {
    let intervalId;
    
    if (jobId && isProcessing) {
      intervalId = setInterval(async () => {
        try {
          const response = await fetch(`${API_BASE_URL}/status/${jobId}`);
          if (response.ok) {
            const status = await response.json();
            setProcessingStatus(status);
            
            // If processing is complete or failed, stop polling
            if (status.status === 'completed' || status.status === 'error') {
              setIsProcessing(false);
              if (status.status === 'completed') {
                // Download the completed result
                try {
                  const downloadResponse = await fetch(`${API_BASE_URL}/download/${jobId}`);
                  if (downloadResponse.ok) {
                    const audioBlob = await downloadResponse.blob();
                    const audioUrl = URL.createObjectURL(audioBlob);
                    
                    // Get filename from response headers or generate one
                    const contentDisposition = downloadResponse.headers.get('content-disposition');
                    let filename = 'chord_cover.wav';
                    if (contentDisposition) {
                      const filenameMatch = contentDisposition.match(/filename="(.+)"/);
                      if (filenameMatch) {
                        filename = filenameMatch[1];
                      }
                    }

                    setProcessingResult({
                      audioUrl,
                      filename,
                      blob: audioBlob
                    });
                  } else {
                    setError('Failed to download result');
                  }
                } catch (err) {
                  console.error('Error downloading result:', err);
                  setError('Failed to download result');
                }
              } else {
                setError(status.message || 'Processing failed');
              }
            }
          }
        } catch (err) {
          console.error('Error checking status:', err);
        }
      }, 1000); // Poll every second
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [jobId, isProcessing]);

  const handleFileUpload = (event) => {
    const uploadedFile = event.target.files[0];
    if (uploadedFile) {
      // Validate file type
      const allowedTypes = ['audio/mpeg', 'audio/wav', 'audio/flac', 'audio/mp4', 'audio/ogg'];
      if (!allowedTypes.includes(uploadedFile.type)) {
        setError('Please select a valid audio file (MP3, WAV, FLAC, M4A, or OGG)');
        setFile(null);
        return;
      }

      // Validate file size (50MB limit)
      const maxSize = 50 * 1024 * 1024; // 50MB
      if (uploadedFile.size > maxSize) {
        setError('File size must be less than 50MB');
        setFile(null);
        return;
      }

      setFile(uploadedFile);
      setError(null);
      setProcessingResult(null);
      setProcessingStatus(null);
      setJobId(null);
    }
  };

  const handleGenerateChordCover = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setProcessingStatus(null);
    setProcessingResult(null);

    try {
      // Create FormData for file upload
      const formData = new FormData();
      formData.append('file', file);

      // Make API request to start processing
      const response = await fetch(`${API_BASE_URL}/process-song/`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      // Get the job ID from response
      const result = await response.json();
      setJobId(result.job_id);
      
      // Initial status will be set by the polling effect
      setProcessingStatus({
        status: 'starting',
        progress: 0,
        message: 'Starting processing...'
      });
      
    } catch (err) {
      console.error('Error starting processing:', err);
      setError(err.message || 'Failed to start processing. Please try again.');
      setIsProcessing(false);
    }
  };

  const handleDownload = () => {
    if (processingResult) {
      const link = document.createElement('a');
      link.href = processingResult.audioUrl;
      link.download = processingResult.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const handleReset = () => {
    setFile(null);
    setProcessingResult(null);
    setError(null);
    setProcessingStatus(null);
    setJobId(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎵 AI Music Coach</h1>
        <p>Upload a song and learn chord progressions by ear</p>
      </header>

      <main className="App-main">
        {/* File Upload Section */}
        <div className="upload-section">
          <h2>Upload Your Song</h2>
          <div className="file-upload-container">
            <input
              ref={fileInputRef}
              type="file"
              accept="audio/*"
              onChange={handleFileUpload}
              className="file-input"
              disabled={isProcessing}
            />
            <div className="file-info">
              {file && (
                <div className="selected-file">
                  <span className="file-name">{file.name}</span>
                  <span className="file-size">({formatFileSize(file.size)})</span>
                </div>
              )}
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="error-message">
              <span>⚠️ {error}</span>
            </div>
          )}

          {/* Progress Bar */}
          {isProcessing && processingStatus && (
            <div className="progress-container">
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${processingStatus.progress || 0}%` }}
                ></div>
              </div>
              <div className="progress-details">
                <span className="progress-text">
                  {processingStatus.message || 'Processing...'}
                </span>
                <span className="progress-percentage">
                  {processingStatus.progress || 0}%
                </span>
              </div>
              <div className="progress-status">
                <span className={`status-badge status-${processingStatus.status}`}>
                  {processingStatus.status === 'starting' && '🚀 Starting'}
                  {processingStatus.status === 'preprocessing' && '🔄 Preprocessing'}
                  {processingStatus.status === 'separating_vocals' && '🎤 Separating Vocals'}
                  {processingStatus.status === 'detecting_chords' && '🎵 Detecting Chords'}
                  {processingStatus.status === 'extracting_melody' && '🎼 Extracting Melody'}
                  {processingStatus.status === 'synthesizing' && '🎤 Synthesizing'}
                  {processingStatus.status === 'completed' && '✅ Complete'}
                  {processingStatus.status === 'error' && '❌ Error'}
                </span>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="action-buttons">
            <button
              onClick={handleGenerateChordCover}
              disabled={!file || isProcessing}
              className="process-button"
            >
              {isProcessing ? 'Processing...' : 'Generate Chord Cover'}
            </button>
            
            {processingResult && (
              <button
                onClick={handleReset}
                className="reset-button"
              >
                Process New Song
              </button>
            )}
          </div>
        </div>

        {/* Results Section */}
        {processingResult && (
          <div className="results-section">
            <h2>Your Chord Cover</h2>
            
            {/* Audio Player */}
            <div className="audio-player-container">
              <audio
                ref={audioRef}
                controls
                className="audio-player"
                src={processingResult.audioUrl}
              >
                Your browser does not support the audio element.
              </audio>
            </div>

            {/* Download Button */}
            <div className="download-section">
              <button
                onClick={handleDownload}
                className="download-button"
              >
                📥 Download Chord Cover
              </button>
              <span className="download-info">
                Click to save the generated audio file
              </span>
            </div>

            {/* Success Message */}
            <div className="success-message">
              <span>✅ Chord cover generated successfully!</span>
              <p>Listen to the spoken chord names that match the timing of your original song.</p>
            </div>
          </div>
        )}

        {/* How It Works Section */}
        <div className="features-section">
          <h2>How it works</h2>
          <div className="feature-grid">
            <div className="feature">
              <h3>1. Upload</h3>
              <p>Upload any song file (MP3, WAV, FLAC, M4A, OGG)</p>
            </div>
            <div className="feature">
              <h3>2. Analyze</h3>
              <p>AI analyzes chord progressions and timing</p>
            </div>
            <div className="feature">
              <h3>3. Generate</h3>
              <p>AI voice speaks chord names in rhythm</p>
            </div>
            <div className="feature">
              <h3>4. Learn</h3>
              <p>Internalize chord progressions by ear</p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="App-footer">
        <p>AI Music Coach - Learn chord progressions through AI-powered audio analysis</p>
      </footer>
    </div>
  );
}

export default App; 