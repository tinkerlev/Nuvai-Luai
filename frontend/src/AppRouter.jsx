// AppRouter.jsx

import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./constants/AuthContext";
import Footer from "./components/Footer";
import UserMenu from './components/UserMenu';
import { SpeedInsights } from "@vercel/speed-insights/react";
import { Analytics } from "@vercel/analytics/react";
import { loadStripe } from '@stripe/stripe-js';
import { Elements } from '@stripe/react-stripe-js';

const LoginPage = React.lazy(() => import("./pages/LoginPage"));
const RegisterPage = React.lazy(() => import("./pages/RegisterPage"));
const ForgotPasswordPage = React.lazy(() => import("./pages/ForgotPasswordPage"));
const ResetPasswordPage = React.lazy(() => import("./pages/ResetPasswordPage"));
const UploadPage = React.lazy(() => import("./pages/UploadPage"));
const SettingsPage = React.lazy(() => import("./pages/SettingsPage"));
const ProfilePage = React.lazy(() => import("./pages/ProfilePage"));
const HomePage = React.lazy(() => import("./pages/Home"));
const GetEarlyAccess = React.lazy(() => import("./pages/GetEarlyAccess"));
const PricingPage = React.lazy(() => import("./pages/PricingPage"));
const CheckoutSuccess = React.lazy(() => import("./pages/CheckoutSuccess"));
const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY);

// function LoadingScreen() {
//   return (
//     <div className="min-h-screen flex items-center justify-center">
//       <div className="animate-pulse text-sm text-gray-500">
//         🔄 Validating session...
//       </div>
//     </div>
//   );
// }

function AppContent() {
  const { user } = useAuth();
  // if (checkingAuth) return <LoadingScreen />;

  return (
    <div className="flex flex-col min-h-screen">
      <div className="flex justify-end items-center gap-4 h-16 px-4">        
        <UserMenu />
      </div>

      <div className="flex-grow">
        {/* <Suspense fallback={<LoadingScreen />}> */}
          <Routes>
            <Route path="/home" element={<HomePage />} />
            <Route path="/early-access" element={<GetEarlyAccess />} />
            <Route path="/login" element={!user ? <LoginPage /> : <Navigate to="/scan" />} />
            <Route path="/register" element={!user ? <RegisterPage /> : <Navigate to="/scan" />} />
            <Route path="/forgot-password" element={!user ? <ForgotPasswordPage /> : <Navigate to="/scan" />} />
            <Route path="/reset-password" element={!user ? <ResetPasswordPage /> : <Navigate to="/scan" />} />
            <Route path="/scan" element={user ? (!user.plan || user.plan === "free" ? <Navigate to="/pricing" /> : <UploadPage />) : <Navigate to="/login" /> } />
            <Route path="/settings" element={user ? <SettingsPage /> : <Navigate to="/login" />} />
            <Route path="/profile" element={user ? <ProfilePage /> : <Navigate to="/login" />} />
            <Route path="/pricing" element={<PricingPage />} />
            <Route path="*" element={<Navigate to="/home" replace />} />
            <Route path="/checkout-success" element={<CheckoutSuccess />} />

          </Routes>
        {/* </Suspense> */}
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
