import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import 'primereact/resources/themes/lara-light-indigo/theme.css';
import 'primereact/resources/primereact.min.css';
import 'primeicons/primeicons.css';
import { Toast } from 'primereact/toast';
import { Button } from 'primereact/button';

import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';

import githubMark from './images/github-mark.svg';
import api from './helpers/api';
import utils from './helpers/utils';


function App() {
  const toast = useRef(null);
  const [user, setUser] = useState(null);

  if (!process.env.REACT_APP_GOOGLE_CLIENT_ID) {
    console.error('NO GOOGLE CLIENT ID SET!!! Set REACT_APP_GOOGLE_CLIENT_ID in file: .env');
  }

  const showToast = (severity, summary, detail) => {
    toast.current.show({
      severity: severity,
      summary: summary,
      detail: detail,
      life: 3000
    });
  };

  const processCreds = async (creds, notify = true) => {
    const userInfo = utils.parseJwt(creds.credential);
    const currentTime = Math.floor(Date.now() / 1000);
    if (userInfo.exp < currentTime) {
      localStorage.removeItem('userCreds');
      setUser(null);
      return;
    }

    // Get or create the user on the server
    try {
      const response = await api.getUser(userInfo);
      if (response) {
        localStorage.setItem('userCreds', JSON.stringify(creds));
        setUser(response);
      } else {
        console.error('Error getting user:', response);
      }
    } catch (error) {
      console.error('Error getting user:', error);
    }

    if (notify) {
      showToast('success', 'Login Successful', 'Welcome ' + userInfo.name);
    }
  }

  useEffect(() => {
    if (!user) {
      const userCreds = localStorage.getItem('userCreds');
      if (userCreds) {
        processCreds(JSON.parse(userCreds), false);
      }
    }
  });

  function UserDetails() {
    if (!user) {
      return (
        <div>
          <GoogleLogin
            onSuccess={processCreds}
            onError={() => {
              console.log('Login Failed');
              showToast('error', 'Login Failed', 'Please try again');
            }}
          />
        </div>
      )
    } else {
      return (
        <div>
          <h1>User Details</h1>
          <p>Welcome {user.name}</p>
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '20px' }}>
            <img src={user.details.picture} alt="User" />
          </div>
          <Button label="Logout" severity="danger" iconPos="right" icon="pi pi-sign-out" onClick={() => {
            localStorage.removeItem('userCreds');
            setUser(null);
          }} />
        </div>
      )
    }
  };

  return (
    <GoogleOAuthProvider clientId={process.env.REACT_APP_GOOGLE_CLIENT_ID}>
      <div className="App">
        <Toast ref={toast} />
        <header className="App-header">
        <a
          href="https://github.com/eebmagic/wavelength-game"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            position: 'absolute',
            top: '10px',
            left: '10px'
          }}
        >
          <img src={githubMark} alt="GitHub Mark" style={{ width: '30px', height: '30px', filter: 'invert(100%)' }} />
        </a>

          <UserDetails />

        </header>
      </div>
    </GoogleOAuthProvider>
  );
}

export default App;
