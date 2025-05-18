import React, { useState, useRef } from "react";

export default function UploadForm({ onScan }) {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [lastUploadTime, setLastUploadTime] = useState(0);
  const [hashCache, setHashCache] = useState(new Set());
  const [scanResults, setScanResults] = useState([]);
  const fileInputRef = useRef();

  const MAX_FILES = 5;
  const MAX_FILE_SIZE_MB = 5;
  const UPLOAD_COOLDOWN_MS = 5000;
  const allowedTypes = [
    ".py", ".js", ".jsx", ".ts", ".tsx", ".html", ".css",
    ".java", ".c", ".cpp", ".go", ".rb", ".php", ".swift", ".kotlin"
  ];

  const isValidExtension = (fileName) =>
    allowedTypes.some((ext) => fileName.toLowerCase().endsWith(ext));

  const isSuspiciousFilename = (name) => {
    const reserved = ["CON", "AUX", "NUL", "COM1", "LPT1"];
    return (
      name.includes("..") ||
      name.startsWith("/") ||
      /[^a-zA-Z0-9_.-]/.test(name) ||
      reserved.includes(name.toUpperCase()) ||
      name.startsWith(".") ||
      name.match(/\.(php|exe|bat|sh)(\.[a-z]{2,4})?$/i)
    );
  };

  const readFileContent = (file) => {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result);
      reader.readAsText(file);
    });
  };

  const detectLanguageByContent = async (file) => {
    const content = await readFileContent(file);
    if (/eval\(|document\.write|innerHTML\s*=/.test(content)) return null;
    if (/import .* from|export default/.test(content)) return "js";
    if (/def |import os|__main__/.test(content)) return "py";
    return null;
  };

  const getFileHash = async (file) => {
    const buffer = await file.arrayBuffer();
    const hashBuffer = await crypto.subtle.digest("SHA-256", buffer);
    return Array.from(new Uint8Array(hashBuffer))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");
  };

  const removeFile = (index) => {
    const updated = [...files];
    updated.splice(index, 1);
    setFiles(updated);
  };

  const validateFiles = async (inputFiles) => {
    if (Date.now() - lastUploadTime < UPLOAD_COOLDOWN_MS) {
      setErrorMsg("Please wait a moment before uploading again.");
      return [];
    }

    if (inputFiles.length > MAX_FILES) {
      setErrorMsg(`You can upload up to ${MAX_FILES} files only.`);
      return [];
    }

    const uniqueFiles = [];
    const newHashCache = new Set(hashCache);

    for (const file of inputFiles) {
      if (isSuspiciousFilename(file.name)) {
        setErrorMsg("One or more files have suspicious file names.");
        return [];
      }

      if (file.size === 0) {
        setErrorMsg("One or more files are empty.");
        return [];
      }

      if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
        setErrorMsg(`Files must be smaller than ${MAX_FILE_SIZE_MB}MB.`);
        return [];
      }

      const fileHash = await getFileHash(file);
      if (newHashCache.has(fileHash)) {
        setErrorMsg("Duplicate file detected. Modify it before re-uploading.");
        return [];
      }
      newHashCache.add(fileHash);

      const contentLang = await detectLanguageByContent(file);
      const extAllowed = isValidExtension(file.name);

      if (!contentLang && !extAllowed) {
        setErrorMsg("Unsupported or suspicious file detected.");
        return [];
      }

      uniqueFiles.push(file);
    }

    setHashCache(newHashCache);
    setErrorMsg("");
    return uniqueFiles;
  };

  const handleFileChange = async (e) => {
    if (loading) return;
    const selected = Array.from(e.target.files);
    const valid = await validateFiles(selected);
    setFiles(valid);
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    if (loading) return;
    const dropped = Array.from(e.dataTransfer.files);
    const valid = await validateFiles(dropped);
    setFiles(valid);
  };

  const handleDragOver = (e) => e.preventDefault();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!files.length) {
      setErrorMsg("Please select at least one file before scanning.");
      return;
    }
    if (loading) return;

    setLoading(true);
    setErrorMsg("");
    setLastUploadTime(Date.now());

    const token = localStorage.getItem("authToken");
    const results = [];

    for (const file of files) {
      const formData = new FormData();
      formData.append("file", file);

      try {
        const res = await fetch(`${process.env.REACT_APP_API_URL}/auth/scan`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`
          },
          body: formData,
        });
        const data = await res.json();
        results.push({ fileName: file.name, ...data });
        onScan(file.name, data);
      } catch (err) {
        console.error(`Error scanning ${file.name}:`, err);
        results.push({ fileName: file.name, error: true });
        onScan(file.name, { error: true });
      }
    }

    setScanResults(results);
    setFiles([]);
    setHashCache(new Set());
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-xl mx-auto">
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        className={`border-2 border-dashed rounded-xl p-8 text-center transition ${
          loading
            ? "border-gray-300 bg-gray-100 cursor-not-allowed opacity-70"
            : "border-gray-300 bg-white hover:border-blue-400 hover:bg-blue-50"
        }`}
      >
        <p className="text-gray-600 mb-4">
          Drag & drop your code files here or
        </p>

        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={handleFileChange}
          className="hidden"
        />

        <button
          type="button"
          onClick={() => fileInputRef.current.click()}
          disabled={loading}
          className={`px-5 py-2 rounded-md shadow transition ${
            loading
              ? "bg-gray-400 text-white cursor-not-allowed"
              : "bg-blue-600 hover:bg-blue-700 text-white"
          }`}
        >
          Browse Files
        </button>

        {files.length > 0 && (
          <div className="mt-4 text-sm text-left text-gray-700">
            <p className="font-medium mb-1">Files selected:</p>
            <ul className="list-disc ml-5">
              {files.map((file, idx) => (
                <li key={idx} className="flex items-center justify-between">
                  {file.name}
                  <button
                    type="button"
                    onClick={() => removeFile(idx)}
                    className="ml-4 text-red-500 text-xs hover:underline"
                  >
                    Remove
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {errorMsg && (
        <p className="text-red-600 text-sm text-center mt-3">{errorMsg}</p>
      )}

      <button
        type="submit"
        disabled={loading}
        className={`block mx-auto text-white text-sm font-medium py-3 px-8 rounded-xl transition mt-4 ${
          loading ? "bg-gray-400 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700"
        }`}
      >
        {loading ? (
          <>
            🔍 Scanning...
            <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin ml-2"></span>
          </>
        ) : (
          "🚀 Start Scanning"
        )}
      </button>

      {loading && (
        <p className="text-center mt-2 text-blue-600 text-sm animate-pulse">
          Please wait... scanning in progress.
        </p>
      )}

      {scanResults.length > 0 && (
        <div className="mt-6 text-sm">
          <h3 className="text-lg font-semibold mb-2">Scan Results:</h3>
          {scanResults.map((result, index) => (
            <div
              key={index}
              className="mb-4 p-4 rounded border shadow-sm bg-white"
            >
              <p className="font-medium text-gray-800">
                📝 <strong>{result.fileName}</strong>
              </p>
              {result.error ? (
                <p className="text-red-600 mt-1">❌ Error processing this file.</p>
              ) : result.vulnerabilities?.length ? (
                <ul className="list-disc ml-6 text-gray-700 mt-1">
                  {result.vulnerabilities.map((vuln, i) => (
                    <li key={i}>
                      <span className="font-semibold">[{vuln.severity.toUpperCase()}]</span> {vuln.title}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-green-600 mt-1">✅ No vulnerabilities found.</p>
              )}
              {result.explanation && (
                <p className="mt-2 text-gray-600 italic">
                  💡 <span dangerouslySetInnerHTML={{ __html: result.explanation }}></span>
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </form>
  );
}
