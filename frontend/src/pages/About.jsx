export default function About() {
  return (
    <>
      <style>{`
        @keyframes fade-up {
          from { opacity: 0; transform: translateY(16px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        .section-card {
          animation: fade-up 0.5s ease both;
          transition: border-color 0.2s, transform 0.2s;
        }
        .section-card:hover {
          border-color: rgba(17,147,212,0.3);
          transform: translateY(-2px);
        }
        .section-card:nth-child(1) { animation-delay: 0.05s; }
        .section-card:nth-child(2) { animation-delay: 0.12s; }
        .section-card:nth-child(3) { animation-delay: 0.19s; }
        .section-card:nth-child(4) { animation-delay: 0.26s; }
      `}</style>

      <section className="min-h-[calc(100vh-64px)] bg-[#111618] px-6 py-12">
        <div className="mx-auto max-w-5xl">

          {/* Header */}
          <div className="mb-12">
            <h1 className="text-3xl font-semibold tracking-tight text-white">
              About Web Page Fraud Detector
            </h1>
            <p className="mt-3 max-w-3xl text-base text-slate-400">
              Web Page Fraud Detector is a machine learning–powered application designed
              to identify phishing and malicious websites in real time. It helps
              users make safer decisions while browsing the web.
            </p>
          </div>

          {/* Sections */}
          <div className="space-y-6">

            {/* Problem */}
            <div className="section-card rounded-xl border border-[#283339] bg-[#0f1416] p-6 shadow-[0_20px_40px_rgba(0,0,0,0.6)]">
              <div className="flex items-center gap-3 mb-3">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-red-500/10 border border-red-500/20">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#f87171" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                    <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
                  </svg>
                </div>
                <h2 className="text-xl font-semibold text-white">The Problem</h2>
              </div>
              <p className="text-sm leading-relaxed text-slate-400">
                Phishing websites are designed to look legitimate while stealing
                sensitive information such as login credentials, personal data,
                and financial details. Traditional rule-based detection systems
                struggle to keep up with evolving attack patterns.
              </p>
            </div>

            {/* Solution */}
            <div className="section-card rounded-xl border border-[#283339] bg-[#0f1416] p-6 shadow-[0_20px_40px_rgba(0,0,0,0.6)]">
              <div className="flex items-center gap-3 mb-3">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[#1193d4]/10 border border-[#1193d4]/20">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#1193d4" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                    <polyline points="9 12 11 14 15 10"/>
                  </svg>
                </div>
                <h2 className="text-xl font-semibold text-white">The Solution</h2>
              </div>
              <p className="text-sm leading-relaxed text-slate-400">
                This project uses a <span className="text-white font-medium">Hybrid Stacking Model</span> combining
                Random Forest and Decision Tree as base learners with Logistic Regression
                as the meta-classifier, trained on real-world URL features to classify
                websites as safe or potentially malicious. The system analyzes patterns
                that are not easily detectable through static rules.
              </p>
            </div>

            {/* How it works */}
            <div className="section-card rounded-xl border border-[#283339] bg-[#0f1416] p-6 shadow-[0_20px_40px_rgba(0,0,0,0.6)]">
              <div className="flex items-center gap-3 mb-4">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-green-500/10 border border-green-500/20">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#4ade80" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10"/>
                    <polyline points="12 6 12 12 16 14"/>
                  </svg>
                </div>
                <h2 className="text-xl font-semibold text-white">How It Works</h2>
              </div>
              <div className="space-y-3">
                {[
                  { n: "01", t: "URL features are extracted and preprocessed" },
                  { n: "02", t: "Trained ML models analyze the extracted features" },
                  { n: "03", t: "The backend returns a prediction with confidence score" },
                  { n: "04", t: "The frontend displays the result in a clear, user-friendly way" },
                ].map((step) => (
                  <div key={step.n} className="flex items-center gap-3">
                    <span className="text-xs font-mono font-bold text-[#1193d4]/60 w-6 shrink-0">{step.n}</span>
                    <div className="h-px flex-1 bg-[#283339]" />
                    <p className="text-sm text-slate-400 text-right">{step.t}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Tech stack */}
            <div className="section-card rounded-xl border border-[#283339] bg-[#0f1416] p-6 shadow-[0_20px_40px_rgba(0,0,0,0.6)]">
              <div className="flex items-center gap-3 mb-4">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-purple-500/10 border border-purple-500/20">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#c084fc" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="16 18 22 12 16 6"/>
                    <polyline points="8 6 2 12 8 18"/>
                  </svg>
                </div>
                <h2 className="text-xl font-semibold text-white">Technology Stack</h2>
              </div>
              <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                {[
                  { label: "Frontend", value: "React, Tailwind CSS" },
                  { label: "Backend", value: "Flask" },
                  { label: "ML Model", value: "Hybrid Stacking (RF + DT)" },
                  { label: "Model Storage", value: "Pickle (.pkl)" },
                  { label: "Data Visualization", value: "Recharts" },
                ].map((item) => (
                  <div key={item.label} className="flex items-center gap-2 rounded-lg border border-[#283339] bg-[#111618] px-4 py-2.5">
                    <span className="text-xs text-slate-500 w-28 shrink-0">{item.label}</span>
                    <span className="h-3 w-px bg-[#283339]" />
                    <span className="text-sm text-slate-300">{item.value}</span>
                  </div>
                ))}
              </div>
            </div>

          </div>
        </div>
      </section>
    </>
  );
}