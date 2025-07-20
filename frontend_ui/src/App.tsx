import React, { useState, useEffect } from 'react';
import './App.css';
import { initializeApp } from "firebase/app";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut, onAuthStateChanged } from "firebase/auth";
import { getFirestore, collection, addDoc, query, orderBy, onSnapshot, serverTimestamp } from "firebase/firestore";
import firebaseConfig from './firebaseConfig';

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [user, setUser] = useState<any>(null);
  const [uploadedFiles, setUploadedFiles] = useState<any[]>([]);

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [user, setUser] = useState<any>(null);

  // Backend API URL - REPLACE WITH YOUR ACTUAL CLOUD RUN SERVICE URL
  // Example: const BACKEND_API_URL = "https://your-backend-service-xxxxxx-uc.a.run.app";
  const BACKEND_API_URL = "YOUR_CLOUD_RUN_BACKEND_URL"; 

  useEffect(() => {
    const unsubscribeAuth = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
    });

    const q = query(collection(db, "uploadedFiles"), orderBy("timestamp", "desc"));
    const unsubscribeFirestore = onSnapshot(q, (snapshot) => {
      const files: any[] = [];
      snapshot.forEach((doc) => {
        files.push({ id: doc.id, ...doc.data() });
      });
      setUploadedFiles(files);
    });

    return () => {
      unsubscribeAuth();
      unsubscribeFirestore();
    };
  }, []);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setFile(event.target.files[0]);
      setMessage(''); // Clear previous messages
    }
  };

  const handleSignUp = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await createUserWithEmailAndPassword(auth, email, password);
      setMessage('Signed up successfully!');
    } catch (error: any) {
      setMessage(`Sign up error: ${error.message}`);
      console.error('Sign up error:', error);
    }
  };

  const handleSignIn = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await signInWithEmailAndPassword(auth, email, password);
      setMessage('Signed in successfully!');
    } catch (error: any) {
      setMessage(`Sign in error: ${error.message}`);
      console.error('Sign in error:', error);
    }
  };

  const handleSignOut = async () => {
    try {
      await signOut(auth);
      setMessage('Signed out successfully!');
      setFile(null);
    } catch (error: any) {
      setMessage(`Sign out error: ${error.message}`);
      console.error('Sign out error:', error);
    }
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!file) {
      setMessage('Please select a file to upload.');
      return;
    }
    if (!user) {
      setMessage('Please sign in to upload files.');
      return;
    }

    setMessage('Uploading...');

    try {
      const idToken = await user.getIdToken();

      // Step 1: Get a signed URL from your backend
      const generateUrlResponse = await fetch(`${BACKEND_API_URL}/generate-signed-url/?file_name=${file.name}&content_type=${file.type}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${idToken}`,
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
        // Save file metadata to Firestore
        await addDoc(collection(db, "uploadedFiles"), {
          userId: user.uid,
          fileName: file.name,
          fileType: file.type,
          gcsPath: `gs://${BUCKET_NAME}/${file.name}`,
          timestamp: serverTimestamp(),
        });
      } else {
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
        <h1>AI Invoice Processor</h1>
        {!user ? (
          <div>
            <h2>Sign Up / Sign In</h2>
            <form onSubmit={handleSignIn}>
              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <button type="submit">Sign In</button>
              <button type="button" onClick={handleSignUp}>Sign Up</button>
            </form>
          </div>
        ) : (
          <div>
            <h2>Welcome, {user.email}!</h2>
            <button onClick={handleSignOut}>Sign Out</button>
            <h3>Upload Your Documents</h3>
            <form onSubmit={handleSubmit}>
              <input type="file" onChange={handleFileChange} />
              <button type="submit" disabled={!file}>Upload</button>
            </form>
          </div>
        )}
        {message && <p>{message}</p>}

        {user && uploadedFiles.length > 0 && (
          <div>
            <h3>Your Uploaded Documents</h3>
            <ul>
              {uploadedFiles.map((doc) => (
                <li key={doc.id}>
                  <strong>{doc.fileName}</strong> ({doc.fileType}) - {new Date(doc.timestamp?.toDate()).toLocaleString()}
                </li>
              ))}
            </ul>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
