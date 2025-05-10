import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import 'primereact/resources/themes/lara-light-indigo/theme.css';
import 'primereact/resources/primereact.min.css';
import 'primeicons/primeicons.css';
import { Toast } from 'primereact/toast';

import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';

import githubMark from './images/github-mark.svg';


function App() {
  const toast = useRef(null);

  const showToast = (severity, summary, detail) => {
    toast.current.show({
      severity: severity,
      summary: summary,
      detail: detail,
      life: 3000
    });
  };

  function parseJwt(token) {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => {
          return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        })
        .join('')
    );
    return JSON.parse(jsonPayload);
  }

  function Details() {
    return (
      <div>
        <h1>Details</h1>
        <GoogleLogin
          onSuccess={credentialResponse => {
            console.log('CRED RESPONSE', credentialResponse);
            const userInfo = parseJwt(credentialResponse.credential);
            console.log(userInfo);
            showToast('success', 'Login Successful', 'Welcome ' + userInfo.name);
          }}
          onError={() => {
            console.log('Login Failed');
          }}
        />
      </div>
    )
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

          <Details />

        </header>
      </div>
    </GoogleOAuthProvider>
  );
}

export default App;
