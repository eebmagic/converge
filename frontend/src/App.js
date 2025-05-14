import React, { useEffect, useRef } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './App.css';
import 'primereact/resources/themes/lara-light-indigo/theme.css';
import 'primereact/resources/primereact.min.css';
import 'primeicons/primeicons.css';
import { Toast } from 'primereact/toast';
import { Button } from 'primereact/button';
import { Menubar } from 'primereact/menubar';

import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';

import GamesList from './components/GamesList';
import GameView from './components/GameView';
import UserDetails from './components/UserDetails';

import api from './helpers/api';
import utils from './helpers/utils';
import { UserProvider, useUser } from './contexts/UserContext';


function AppContent() {
  const toast = useRef(null);
  const { user, setUser } = useUser();

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
  }, [user]);

  const menuItems = [
    {
      label: 'Home',
      icon: 'pi pi-home',
      url: '/',
    },
    {
      label: 'Games',
      icon: 'pi pi-comments',
    },
    {
      label: 'GitHub',
      icon: 'pi pi-github',
      command: () => {window.open('https://github.com/eebmagic/converge', '_blank')}
    }
  ]

  return (
    <div className="App">
      <Toast ref={toast} />
      <Menubar model={menuItems} end={<UserDetails />} />
      <header className="App-header">
        {!user && (
          <GoogleLogin
            onSuccess={processCreds}
            onError={() => {
              console.error('Login Failed');
              showToast('error', 'Login Failed', 'Please try again');
            }}
          />
        )}
        {user && (
          <Routes>
            <Route path="/" element={
              <div>
                <Button
                  label="Create Game"
                  severity="success"
                  iconPos="right"
                  icon="pi pi-plus"
                  onClick={async () => {
                    console.log('Creating game from user:', user);
                    const result = await api.createGame(user.provider_id);
                    console.log('Result from createGame:', result);
                  }}
                />
                <Button
                  label="Logout"
                  severity="danger"
                  iconPos="right"
                  icon="pi pi-sign-out"
                  onClick={() => {
                    localStorage.removeItem('userCreds');
                    setUser(null);
                  }}
                />
                <GamesList user={user} />
              </div>
            } />
            <Route path="/usergame/:gameId" element={<GameView user={user} />} />
          </Routes>
        )}
      </header>
    </div>
  );
}

function App() {
  return (
    <GoogleOAuthProvider clientId={process.env.REACT_APP_GOOGLE_CLIENT_ID}>
      <UserProvider>
        <BrowserRouter>
          <AppContent /> {/* TODO: Rename this to something like CoreRoutes or HomePage and move ot its own file*/}
        </BrowserRouter>
      </UserProvider>
    </GoogleOAuthProvider>
  );
}

export default App;
