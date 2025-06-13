// AppRouter.jsx

import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./constants/AuthContext";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import ForgotPasswordPage from "./pages/ForgotPasswordPage";
import UploadPage from "./pages/UploadPage";
import SettingsPage from "./pages/SettingsPage"
import ProfilePage from "./pages/ProfilePage";
import ResetPasswordPage from "./pages/ResetPasswordPage";
import HomePage from "./pages/Home";
import Footer from "./components/Footer";
import GetEarlyAccess from './pages/GetEarlyAccess';
import ThemeSwitcher from "./components/ThemeSwitcher";
import { SpeedInsights } from "@vercel/speed-insights/react";
import { Analytics } from "@vercel/analytics/react";
import PricingPage from './pages/PricingPage';
import { loadStripe } from '@stripe/stripe-js';
import { Elements } from '@stripe/react-stripe-js';
import UserMenu from './components/UserMenu';



const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY);

function LoadingScreen() {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
      <h1>Loading...</h1>
    </div>
  );
}

function AppContent() {
  const { user, checkingAuth } = useAuth();

  if (checkingAuth) {
    return <LoadingScreen />;
  }

  return (
    <div className="flex flex-col min-h-screen">
      <div className="flex justify-end p-4 items-center gap-4">
        <ThemeSwitcher />
        
        <UserMenu />
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
          <Route path="/settings" element={user ? <SettingsPage /> : <Navigate to="/login" />} />
          <Route path="/profile" element={user ? <ProfilePage /> : <Navigate to="/login" />} />
          <Route path="*" element={<Navigate to="/home" replace />} />
          <Route path="/pricing" element={<PricingPage />} />
          
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
        <Elements stripe={stripePromise}>
        <AppContent />
        <SpeedInsights />
        <Analytics />
        </Elements>
      </AuthProvider>
    </Router>
  );
}