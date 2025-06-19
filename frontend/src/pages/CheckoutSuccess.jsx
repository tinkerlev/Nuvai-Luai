// CheckoutSuccess.jsx
import { useEffect } from "react";
import { useAuth } from "../constants/AuthContext";
import { useNavigate } from "react-router-dom";

export default function CheckoutSuccess() {
  const { refetchAuth } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const run = async () => {
      await refetchAuth();
      navigate("/scan");
    };
    run();
  }, [navigate, refetchAuth]);

  return (
    <div className="flex flex-col min-h-screen">
      <div className="flex justify-end items-center gap-4 h-16 px-4">
      </div>

      <div className="flex-grow flex items-center justify-center">
        <div className="text-center space-y-4">
          <h2 className="text-2xl font-bold">✅ Payment successful!</h2>
          <p className="text-gray-600">Redirecting to your dashboard...</p>
        </div>
      </div>

      <footer className="h-16">
      </footer>
    </div>
  );
}
