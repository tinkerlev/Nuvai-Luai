import React, { useState } from "react";
import UploadForm from "../components/UploadForm";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Icon } from '@iconify/react';

export default function App() {
  const [results, setResults] = useState([]);
  const navigate = useNavigate();

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
      transition: {
        staggerChildren: 0.1
      }
    }
  };
  
  const item = {
    hidden: { opacity: 0, y: 10 },
    visible: { opacity: 1, y: 0 }
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
                <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
                  <Icon icon="mdi:shield-scan" className="w-8 h-8 text-primary"/>
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
                    
                    {r.result.error ? (
                      <div className="alert alert-error">
                        <Icon icon="mdi:close-circle" className="h-6 w-6" />
                        <span>Failed to scan</span>
                      </div>
                    ) : r.result.vulnerabilities?.length ? (
                      <div>
                        <div className="alert alert-warning mb-2">
                          <Icon icon="mdi:alert" className="h-6 w-6" />
                          <span>{r.result.vulnerabilities.length} vulnerabilities detected</span>
                        </div>
                        <ul className="space-y-2">
                          {r.result.vulnerabilities.map((v, i) => (
                            <li key={i} className="flex items-start gap-2">
                              <div className={`badge ${
                                v.severity === 'high' ? 'badge-error' : 
                                v.severity === 'medium' ? 'badge-warning' : 'badge-info'
                              } badge-sm self-center`}>
                                {v.severity.toUpperCase()}
                              </div>
                              <span>{v.title}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    ) : (
                      <div className="alert alert-success">
                        <Icon icon="mdi:check-circle" className="h-6 w-6" />
                        <span>No vulnerabilities found</span>
                      </div>
                    )}
                    
                    {r.result.explanation && (
                      <div className="mt-4 bg-base-200 p-4 rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          <Icon icon="mdi:lightbulb" className="text-warning" />
                          <span className="font-medium">Explanation</span>
                        </div>
                        <p className="text-sm" dangerouslySetInnerHTML={{ __html: r.result.explanation }}></p>
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
