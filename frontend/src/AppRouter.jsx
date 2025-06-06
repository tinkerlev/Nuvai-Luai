// AppRouter.jsx

import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from "react-router-dom"; 
import { AuthProvider, useAuth } from "./constants/AuthContext";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import ForgotPasswordPage from "./pages/ForgotPasswordPage";
import UploadPage from "./pages/UploadPage";
import ResetPasswordPage from "./pages/ResetPasswordPage";
import HomePage from "./pages/Home";
import Footer from "./components/Footer";
import GetEarlyAccess from './pages/GetEarlyAccess';
import ThemeSwitcher from "./components/ThemeSwitcher";
import { SpeedInsights } from "@vercel/speed-insights/react";
import { Analytics } from "@vercel/analytics/react";

function LoadingScreen() {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
      <h1>Loading...</h1>
    </div>
  );
}

function AppContent() {
  const { user, checkingAuth, logout } = useAuth();
  const navigate = useNavigate();
  const handleLogout = async () => {
    try {
      await logout();
      navigate("/login");
    } catch (error) {
      console.error("Logout failed in AppContent:", error);
    }
  };

  if (checkingAuth) {
    return <LoadingScreen />;
  }

  return (
    <div className="flex flex-col min-h-screen">
      <div className="flex justify-end p-4 items-center gap-4">
        <ThemeSwitcher />
        
        {user && (
          <button onClick={handleLogout} className="btn btn-outline btn-error btn-sm">
            Logout
          </button>
        )}
      </div>

      <div className="flex-grow">
        <Routes>
          <Route path="/home" element={<HomePage />} />
          <Route path="/early-access" element={<GetEarlyAccess />} />
          <Route path="/login" element={!user ? <LoginPage /> : <Navigate to="/scan" />} />
          <Route path="/register" element={!user ? <RegisterPage /> : <Navigate to="/scan" />} />
          <Route path="/forgot-password" element={!user ? <ForgotPasswordPage /> : <Navigate to="/scan" />} />
          <Route path="/reset-password" element={!user ? <ResetPasswordPage /> : <Navigate to="/scan" />} />
          <Route path="/scan" element={user ? <UploadPage /> : <Navigate to="/login" />} />
          <Route path="*" element={<Navigate to="/home" replace />} />
        </Routes>
      </div>
      <Footer />
    </div>
  );
}

export default function AppRouter() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
        <SpeedInsights />
        <Analytics />
      </AuthProvider>
    </Router>
  );
}