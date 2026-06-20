import { useState } from "react";
import axios from "axios";

export default function Detection() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setError("");

    try {
      const res = await axios.post("http://127.0.0.1:5000/predict", { url });
      setResult(res.data);
    } catch {
      setError("Unable to analyze the URL. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const isSafe = result?.prediction === "safe";
  const isSuspicious = result?.prediction === "suspicious";

  const resultColor = isSafe
    ? "text-green-400"
    : isSuspicious
    ? "text-yellow-400"
    : "text-red-400";

  const resultBorder = isSafe
    ? "border-green-500/30 bg-green-500/5"
    : isSuspicious
    ? "border-yellow-500/30 bg-yellow-500/5"
    : "border-red-500/30 bg-red-500/5";

  const resultLabel = isSafe
    ? "Website Appears Safe"
    : isSuspicious
    ? "Suspicious Website"
    : "Phishing Website Detected";

  const resultIcon = isSafe ? (
    <svg className="mx-auto mb-2" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" style={{ color: "#4ade80" }}>
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
      <polyline points="9 12 11 14 15 10"/>
    </svg>
  ) : isSuspicious ? (
    <svg className="mx-auto mb-2" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" style={{ color: "#facc15" }}>
      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
      <line x1="12" y1="9" x2="12" y2="13"/>
      <line x1="12" y1="17" x2="12.01" y2="17"/>
    </svg>
  ) : (
    <svg className="mx-auto mb-2" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" style={{ color: "#f87171" }}>
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
      <line x1="9" y1="9" x2="15" y2="15"/>
      <line x1="15" y1="9" x2="9" y2="15"/>
    </svg>
  );

  return (
    <>
      <style>{`
        @keyframes fade-up {
          from { opacity: 0; transform: translateY(16px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes result-in {
          from { opacity: 0; transform: translateY(10px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        .card-enter { animation: fade-up 0.5s ease both; }
        .result-enter { animation: result-in 0.4s ease both; }

        .url-input {
          transition: border-color 0.2s, box-shadow 0.2s;
        }
        .url-input:focus {
          border-color: #1193d4;
          box-shadow: 0 0 0 3px rgba(17,147,212,0.15);
        }

        .btn-analyze {
          transition: background 0.2s, transform 0.15s, box-shadow 0.2s;
          position: relative;
          overflow: hidden;
        }
        .btn-analyze:not(:disabled):hover {
          background: #0f7fb8;
          transform: translateY(-1px);
          box-shadow: 0 6px 20px rgba(17,147,212,0.35);
        }
        .btn-analyze:not(:disabled):active {
          transform: translateY(0);
        }

        @keyframes progress {
          from { width: 0%; }
          to   { width: 100%; }
        }
        .loading-bar {
          animation: progress 1.8s ease-in-out infinite;
        }
      `}</style>

      <section className="flex h-[calc(100vh-64px)] items-center justify-center bg-[#111618] px-6">
        <div className="w-full max-w-lg card-enter">

          {/* Card */}
          <div className="relative rounded-2xl border border-[#283339] bg-[#0f1416] p-8 md:p-10 shadow-[0_30px_60px_rgba(0,0,0,0.7)]">

            {/* Top Accent */}
            <div className="absolute inset-x-0 top-0 h-[2px] rounded-t-2xl bg-gradient-to-r from-transparent via-[#1193d4] to-transparent" />

            {/* Loading bar */}
            {loading && (
              <div className="absolute inset-x-0 top-0 h-[2px] rounded-t-2xl overflow-hidden">
                <div className="loading-bar h-full bg-[#1193d4]" />
              </div>
            )}

            {/* Header */}
            <div className="mb-8 text-center">
              <h1 className="text-2xl font-semibold tracking-tight text-white md:text-3xl">
                Phishing URL Detection
              </h1>
              <p className="mt-2 text-sm text-slate-400">
                Analyze a website URL to detect phishing and malicious activity.
              </p>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-5">

              {/* Input */}
              <div>
                <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-300">
                  Website URL
                </label>
                <div className="relative">
                  <span className="absolute left-4 top-1/2 -translate-y-1/2">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#1193d4" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
                    </svg>
                  </span>
                  <input
                    type="url"
                    required
                    value={url}
                    onChange={(e) => { setUrl(e.target.value); setResult(null); setError(""); }}
                    placeholder="https://example.com"
                    className="url-input w-full rounded-xl border border-[#283339] bg-[#111618] py-3.5 pl-11 pr-4 text-white placeholder-slate-500 outline-none"
                  />
                </div>
              </div>

              {/* Button */}
              <button
                type="submit"
                disabled={loading}
                className="btn-analyze flex w-full items-center justify-center gap-2 rounded-xl bg-[#1193d4] py-3.5 text-base font-semibold text-white disabled:opacity-60"
              >
                {loading ? (
                  <>
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
                    </svg>
                    Analyze URL
                  </>
                )}
              </button>
            </form>

            {/* Error */}
            {error && (
              <div className="result-enter mt-6 rounded-xl border border-red-500/40 bg-red-500/10 p-4 text-sm text-red-400 flex items-center gap-2">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="shrink-0">
                  <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                {error}
              </div>
            )}

            {/* Divider */}
            {result && !loading && (
              <div className="my-6 h-px w-full bg-gradient-to-r from-transparent via-[#283339] to-transparent" />
            )}

            {/* Result */}
            {result && !loading && (
              <div className={`result-enter rounded-xl border p-5 text-center ${resultBorder}`}>
                {resultIcon}
                <p className="text-xs uppercase tracking-wider text-slate-400 mb-1">
                  Detection Result
                </p>
                <p className={`text-2xl font-semibold ${resultColor}`}>
                  {resultLabel}
                </p>
                {result.confidence && (
                  <div className="mt-3">
                    <p className="text-xs text-slate-500 mb-1">Confidence</p>
                    <div className="mx-auto w-48 h-1.5 rounded-full bg-[#283339] overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-700"
                        style={{
                          width: `${result.confidence}%`,
                          background: isSafe ? "#4ade80" : isSuspicious ? "#facc15" : "#f87171",
                        }}
                      />
                    </div>
                    <p className="mt-1.5 text-sm font-medium text-white">{result.confidence}%</p>
                  </div>
                )}
                {result.note && (
                  <p className="mt-3 text-xs text-slate-500">{result.note}</p>
                )}
              </div>
            )}

          </div>
        </div>
      </section>
    </>
  );
}