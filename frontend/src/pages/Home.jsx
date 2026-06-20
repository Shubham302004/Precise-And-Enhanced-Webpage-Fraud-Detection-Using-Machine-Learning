import { Link } from "react-router-dom";

export default function Home() {
  return (
    <>
      <style>{`
        @keyframes fade-up {
          from { opacity: 0; transform: translateY(20px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        .hero-content { animation: fade-up 0.6s ease both; }
        .hero-sub     { animation: fade-up 0.6s ease 0.12s both; }
        .hero-ctas    { animation: fade-up 0.6s ease 0.24s both; }

        .btn-primary  { transition: background 0.2s, transform 0.2s, box-shadow 0.2s; }
        .btn-primary:hover {
          background: #0f7fb8;
          transform: translateY(-1px);
          box-shadow: 0 6px 24px rgba(17,147,212,0.35);
        }
        .btn-secondary { transition: background 0.2s, transform 0.2s; }
        .btn-secondary:hover {
          background: #1a1f22;
          transform: translateY(-1px);
        }
      `}</style>

      <section
        className="flex h-[calc(100vh-64px)] items-center justify-center bg-[#111618] px-6"
        style={{ fontFamily: 'Inter, "Noto Sans", sans-serif' }}
      >
        <div className="w-full max-w-6xl">

          {/* Hero Card */}
          <div
            className="relative overflow-hidden rounded-2xl border border-[#283339] bg-cover bg-center bg-no-repeat shadow-[0_40px_80px_rgba(0,0,0,0.7)] min-h-[560px] flex items-center justify-center"
            style={{
              backgroundImage:
                'linear-gradient(rgba(0,0,0,0.28), rgba(0,0,0,0.58)), url("https://lh3.googleusercontent.com/aida-public/AB6AXuBT7V_lwsw_-eqd57PzF_gTXxI0GnbiFZ5Sc-ntzjwLpBAyte-dBATFN7yi1V0hry4KrdKq6NeogbgoXjcbWs5rX66I9pODiKLKRN138AiAIaD3h1X9RPz62A_wpRIdpkbzysgie9ruBIfiFQ8BzA2HXNgTdqLHxIZdW2JoITHR6BeT1j76yhQdw5cKVvsE5aDDZafoQrWJ_5HNgpvXZrM51gWASfwpwQfYvUNqGu5PhHFAj90SucD8B-6V3AQXnFWyQMcjFz7kWn5-")',
            }}
          >
            {/* Top Accent */}
            <div className="absolute inset-x-0 top-0 h-[2px] bg-gradient-to-r from-transparent via-[#1193d4] to-transparent" />

            {/* Subtle vignette at bottom */}
            <div className="absolute inset-x-0 bottom-0 h-32 bg-gradient-to-t from-black/40 to-transparent pointer-events-none" />

            {/* Content */}
            <div className="relative z-10 max-w-4xl px-6 text-center">

              <h1 className="hero-content text-4xl font-extrabold tracking-tight text-white md:text-5xl leading-tight">
                Precise &amp; Enhanced Webpage Fraud Detection
              </h1>

              <p className="hero-sub mt-4 text-lg leading-relaxed text-white/80 max-w-2xl mx-auto">
                Protect your online presence using machine learning and deep learning
                to identify phishing and malicious websites with confidence.
              </p>

              {/* CTA Buttons */}
              <div className="hero-ctas mt-8 flex flex-wrap justify-center gap-4">
                <Link
                  to="/detection"
                  className="btn-primary flex h-12 min-w-[160px] items-center justify-center rounded-xl bg-[#1193d4] px-6 text-base font-semibold text-white"
                >
                  Start Detection
                </Link>
                <Link
                  to="/analysis"
                  className="btn-secondary flex h-12 min-w-[160px] items-center justify-center rounded-xl border border-[#283339] bg-[#111618] px-6 text-base font-semibold text-white"
                >
                  View Analysis
                </Link>
              </div>
            </div>
          </div>

        </div>
      </section>
    </>
  );
}