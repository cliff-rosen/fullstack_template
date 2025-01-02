import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom'
import TopBar from './components/TopBar'
import { ThemeProvider } from './context/ThemeContext'
import { useAuth } from './context/AuthContext'
import { useEffect, useState } from 'react'
import { setSessionExpiredHandler } from './lib/api'
import LoginForm from './components/auth/LoginForm'
import settings from './config/settings'

/*
all backend requests are made via api.ts, which implements axios interceptors
setSessionExpiredHandler accepts a callback function that is called when 401 is returned from backend
the callback function passed is handleSessionExpired, which is defined in AuthContext.tsx

handleSessionExpired behavior:
- called when 401 is returned from backend
- removes authToken and user from localStorage
- sets isAuthenticated to false
- sets user to null
- sets error to null
*/

function GoogleCallback() {
  const { handleGoogleCallback } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const handleCallback = async () => {
      // Get the ID token from the URL hash
      const hashParams = new URLSearchParams(window.location.hash.substring(1));
      const idToken = hashParams.get('id_token');

      if (!idToken) {
        setError('No ID token found in URL');
        return;
      }

      try {
        await handleGoogleCallback(idToken);
        navigate('/'); // Use React Router navigation instead of window.location
      } catch (error) {
        setError('Failed to authenticate with Google');
      }
    };

    handleCallback();
  }, [handleGoogleCallback, navigate]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center dark:bg-gray-900 bg-gray-50">
        <div className="text-red-600 dark:text-red-400">{error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center dark:bg-gray-900 bg-gray-50">
      <div className="text-gray-600 dark:text-gray-400">Authenticating...</div>
    </div>
  );
}

function App() {
  const { handleSessionExpired, isAuthenticated, login, register, error } = useAuth()
  const [isRegistering, setIsRegistering] = useState(false)

  useEffect(() => {
    // Set up the session expired handler
    setSessionExpiredHandler(handleSessionExpired)

    // Clean up when component unmounts
    return () => setSessionExpiredHandler(() => { })
  }, [handleSessionExpired])

  if (!isAuthenticated) {
    return (
      <BrowserRouter>
        <ThemeProvider>
          <Routes>
            <Route path="/auth/google/callback" element={<GoogleCallback />} />
            <Route
              path="*"
              element={
                <div className="min-h-screen flex items-center justify-center dark:bg-gray-900 bg-gray-50">
                  <LoginForm
                    isRegistering={isRegistering}
                    setIsRegistering={setIsRegistering}
                    login={login}
                    register={register}
                    error={error}
                  />
                </div>
              }
            />
          </Routes>
        </ThemeProvider>
      </BrowserRouter>
    )
  }

  return (
    <BrowserRouter>
      <ThemeProvider>
        <div className="min-h-screen flex flex-col bg-white dark:bg-gray-900">
          <TopBar />
          <div className="flex-1 flex items-center justify-center">
            <h1 className="text-2xl font-semibold text-gray-800 dark:text-gray-200">
              Welcome to {settings.appName}
            </h1>
          </div>
        </div>
      </ThemeProvider>
    </BrowserRouter>
  )
}

export default App 