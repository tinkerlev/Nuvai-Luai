// UploadPage.jsx
import React, { useState } from "react";
import { motion } from "framer-motion";
import { Icon } from '@iconify/react';
import { useAuth } from "../constants/AuthContext";
import { Suspense } from "react";
const UploadForm = React.lazy(() => import("../components/UploadForm"));
export default function App() {
  const { user } = useAuth();
  const [results, setResults] = useState([]);
  const handleScanResult = (fileName, result) => {
    setResults((prev) => [...prev, { fileName, result }]);
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
      .replace(/\b(Tip.*?):/gi, '<span class="text-sky-400 font-semibold">🔎 $1:</span>')
      .replace(/\b(Short.*?):/gi, '<span class="text-yellow-500 font-semibold">⚡ $1:</span>')
      .replace(/\b(Long.*?):/gi, '<span class="text-yellow-500 font-semibold">⚡ $1:</span>')
      .replace(/\b(Immediate.*?):/gi, '<span class="text-yellow-500 font-semibold">⚡ $1:</span>');
  };
  return (
    <div className="min-h-screen bg-base-200 py-10">
      <div className="container mx-auto px-4">
        <motion.div
          initial="hidden"
          animate="visible"
          variants={fadeIn}
          className="max-w-3xl mx-auto">
          <div className="card bg-base-100 shadow-xl border border-base-300 mb-8">
              <div className="card-body flex flex-col items-center">
                <div className="mb-4">
                  <div className="w-24 h-24 rounded-full overflow-hidden">
                    {user?.logoUrl && !user.logoUrl.includes("default_logo") ? (
                      <img
                        src={`${process.env.REACT_APP_API_URL}${user.logoUrl}`}
                        alt="User profile"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                    <div className="w-full h-full bg-neutral-focus text-neutral-content flex items-center justify-center ring ring-primary ring-offset-base-100 ring-offset-2 rounded-full">
                      <span className="text-3xl font-bold">
                        {user?.initials?.substring(0, 2).toUpperCase() || "??"}
                      </span>
                    </div>
                  )}
                </div>
              </div>
              <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                Luai Code Scanner
              </h1>
              <p className="text-base-content/70 mb-6">
                Upload your code files for instant security analysis and vulnerability detection
              </p>
            <Suspense fallback={<div className="text-center">Loading...</div>}>
              <UploadForm onScan={handleScanResult} />
            </Suspense>
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
