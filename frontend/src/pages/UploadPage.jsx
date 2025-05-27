// UploadPage.jsx
import React, { useState } from "react";
import UploadForm from "../components/UploadForm";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Icon } from '@iconify/react';

export default function App() {
  const [results, setResults] = useState([]);
  const navigate = useNavigate();
  const [customLogo, setCustomLogo] = useState(() => {
    const savedLogo = localStorage.getItem("customLogo");
    return savedLogo || null;
  });

  const handleScanResult = (fileName, result) => {
    setResults((prev) => [...prev, { fileName, result }]);
  };

  const handleLogout = () => {
    localStorage.removeItem("authToken");
    navigate("/login");
  };

  const fadeIn = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5 } }
  };

  const staggerContainer = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };
  const item = {
    hidden: { opacity: 0, y: 10 },
    visible: { opacity: 1, y: 0 }
  };
  const formatAIText = (text) => {
    return text
      .replace(/^### (.+)(\r?\n)?/gm, '<h3 class="text-amber-500 font-bold text-base mt-3 mb-1">$1</h3>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/^(\d+\.\s*)(.*?):/gm, '<span class="text-purple-500 font-semibold">$1$2:</span>')
      .replace(/\b(Critical.*?):/gi, '<span class="text-red-600 font-semibold">⚠️ $1:</span>')
      .replace(/\b(High.*?):/gi, '<span class="text-orange-500 font-semibold">🟠 $1:</span>')
      .replace(/\b(Medium.*?):/gi, '<span class="text-yellow-500 font-semibold">🟡 $1:</span>')
      .replace(/\b(Low.*?):/gi, '<span class="text-green-600 font-semibold">🟢 $1:</span>')
      .replace(/\b(Warning.*?):/gi, '<span class="text-yellow-400 font-semibold">⚠️ $1:</span>')
      .replace(/\b(Info.*?):/gi, '<span class="text-sky-500 font-semibold">💡 $1:</span>')
      .replace(/\b(Tip.*?):/gi, '<span class="text-sky-400 font-semibold">🔎 $1:</span>');
  };
  return (
    <div className="min-h-screen bg-base-200 py-10">
      <div className="container mx-auto px-4">
        <motion.div
          initial="hidden"
          animate="visible"
          variants={fadeIn}
          className="max-w-3xl mx-auto"
        >
          <div className="card bg-base-100 shadow-xl border border-base-300 mb-8">
            <div className="card-body text-center">
              <div className="flex justify-center mb-2">
                <div
                  className={`relative w-20 h-20 rounded-full overflow-hidden group cursor-pointer bg-transparent ${
                    customLogo ? '' : 'border-2 border-dashed border-primary'
                  }`}
                >
                {customLogo ? (
                  <img
                    src={customLogo}
                    alt="Custom Logo"
                    className="object-contain w-full h-full"
                  />
                ) : (
                  <div className="flex flex-col items-center justify-center w-full h-full text-primary/70">
                    <Icon icon="mdi:camera-plus" className="w-8 h-8 mb-1" />
                    <span className="text-xs">Upload Logo</span>
                  </div>
                )}
                <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <Icon icon="mdi:camera-outline" className="text-white w-6 h-6" />
                </div>
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => {
                    const file = e.target.files[0];
                    if (!file) return;
                    const reader = new FileReader();
                    reader.onloadend = () => {
                      const dataUrl = reader.result;
                      setCustomLogo(dataUrl);
                      localStorage.setItem("customLogo", dataUrl);
                    };
                    reader.readAsDataURL(file);
                  }}
                  className="absolute inset-0 opacity-0 cursor-pointer"
                />
              </div>
              </div>
              <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                Luai Code Scanner
              </h1>
              <p className="text-base-content/70 mb-6">
                Upload your code files for instant security analysis and vulnerability detection
              </p>
              <div className="flex justify-end mb-4">
                <button
                  onClick={handleLogout}
                  className="btn btn-sm btn-outline btn-error gap-2"
                >
                  <Icon icon="mdi:logout" />
                  Logout
                </button>
              </div>
              <UploadForm onScan={handleScanResult} />
            </div>
          </div>
          {results.length > 0 && (
            <motion.div
              initial="hidden"
              animate="visible"
              variants={staggerContainer}
              className="mb-8"
            >
              <h2 className="text-2xl font-bold mb-4 text-center">Scan Results</h2>

              {results.map((r, idx) => (
                <motion.div
                  key={idx}
                  className="card bg-base-100 shadow-md mb-4"
                  variants={item}
                >
                  <div className="card-body">
                    <h3 className="card-title text-lg font-medium flex items-center gap-2">
                      <Icon icon="mdi:file-code" className="text-primary" />
                      {r.fileName}
                    </h3>
                    {r.result.ai_analysis && (
                      <div className="mt-2 bg-base-200 p-4 rounded-lg border-l-4 border-primary/60 shadow-sm">
                        <div className="flex items-center gap-2 mb-2">
                          <Icon icon="mdi:robot-outline" className="text-primary" />
                          <span className="font-semibold text-base">AI Analysis Summary</span>
                        </div>
                        <div
                          className="text-sm whitespace-pre-line text-base-content/80"
                          dangerouslySetInnerHTML={{
                            __html: formatAIText(r.result.ai_analysis)
                          }}
                        />
                      </div>
                    )}
                    {r.result.error ? (
                      <div className="alert alert-error mt-4">
                        <Icon icon="mdi:close-circle" className="h-6 w-6" />
                        <span>Failed to scan</span>
                      </div>
                    ) : r.result.vulnerabilities?.length ? (
                      <div className="mt-4">
                        <div className="alert alert-warning mb-2">
                          <Icon icon="mdi:alert" className="h-6 w-6" />
                          <span>{r.result.vulnerabilities.length} vulnerabilities detected</span>
                        </div>
                      </div>
                    ) : (
                      <div className="alert alert-success mt-4">
                        <Icon icon="mdi:check-circle" className="h-6 w-6" />
                        <span>No vulnerabilities found</span>
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
