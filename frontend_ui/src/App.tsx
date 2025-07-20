import React, { useState } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState('');
  // IMPORTANT: In a production environment, this API key should NOT be hardcoded.
  // It should be loaded securely, e.g., from an environment variable during build time,
  // or fetched from a dedicated backend endpoint that provides a temporary token.
  const API_KEY = 'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2'; // Replace with your actual API key

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setFile(event.target.files[0]);
      setMessage(''); // Clear previous messages
    }
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!file) {
      setMessage('Please select a file to upload.');
      return;
    }

    setMessage('Uploading...');

    try {
      // Step 1: Get a signed URL from your backend
      const generateUrlResponse = await fetch(`/generate-signed-url/?file_name=${file.name}&content_type=${file.type}`, {
        method: 'POST',
        headers: {
          'X-API-Key': API_KEY,
        },
      });

      if (!generateUrlResponse.ok) {
        const errorData = await generateUrlResponse.json();
        throw new Error(`Failed to get signed URL: ${errorData.detail || generateUrlResponse.statusText}`);
      }

      const { signed_url } = await generateUrlResponse.json();

      // Step 2: Upload the file directly to GCS using the signed URL
      const uploadResponse = await fetch(signed_url, {
        method: 'PUT',
        headers: {
          'Content-Type': file.type,
        },
        body: file,
      });

      if (uploadResponse.ok) {
        setMessage(`File "${file.name}" uploaded successfully to Google Cloud Storage.`);
      } else {
        // GCS might return a non-JSON error, so check for text first
        const errorText = await uploadResponse.text();
        throw new Error(`Failed to upload file to GCS: ${uploadResponse.status} - ${errorText}`);
      }
    } catch (error: any) {
      setMessage(`An error occurred: ${error.message}`);
      console.error('Upload error:', error);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Upload Your Documents</h1>
        <form onSubmit={handleSubmit}>
          <input type="file" onChange={handleFileChange} />
          <button type="submit" disabled={!file}>Upload</button>
        </form>
        {message && <p>{message}</p>}
      </header>
    </div>
  );
}

export default App;