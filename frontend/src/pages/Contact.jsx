import { useState } from "react";
import axios from "axios";

export default function Contact() {
  const [form, setForm] = useState({ name: "", email: "", message: "" });
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(""); // "success" | "error" | ""

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatus("");

    try {
      await axios.post("http://127.0.0.1:5000/contact", form);
      setStatus("success");
      setForm({ name: "", email: "", message: "" });
    } catch {
      setStatus("error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <style>{`
        @keyframes fade-up {
          from { opacity: 0; transform: translateY(16px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes result-in {
          from { opacity: 0; transform: translateY(8px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        .card-enter  { animation: fade-up 0.5s ease both; }
        .status-enter { animation: result-in 0.3s ease both; }

        .form-input {
          transition: border-color 0.2s, box-shadow 0.2s;
        }
        .form-input:focus {
          border-color: #1193d4;
          box-shadow: 0 0 0 3px rgba(17,147,212,0.15);
        }

        .btn-send {
          transition: background 0.2s, transform 0.15s, box-shadow 0.2s;
        }
        .btn-send:not(:disabled):hover {
          background: #0f7fb8;
          transform: translateY(-1px);
          box-shadow: 0 6px 20px rgba(17,147,212,0.35);
        }
        .btn-send:not(:disabled):active {
          transform: translateY(0);
        }
      `}</style>

      <section className="flex min-h-[calc(100vh-64px)] items-center justify-center bg-[#111618] px-6 py-10">
        <div className="w-full max-w-xl card-enter">

          {/* Card */}
          <div className="relative rounded-2xl border border-[#283339] bg-[#0f1416] p-8 md:p-10 shadow-[0_30px_60px_rgba(0,0,0,0.7)]">

            {/* Top Accent */}
            <div className="absolute inset-x-0 top-0 h-[2px] rounded-t-2xl bg-gradient-to-r from-transparent via-[#1193d4] to-transparent" />

            {/* Header */}
            <div className="mb-8 text-center">
              <h1 className="text-2xl font-semibold tracking-tight text-white md:text-3xl">
                Contact
              </h1>
              <p className="mt-2 text-sm text-slate-400">
                Have questions or feedback? Feel free to reach out.
              </p>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-5">

              {/* Name */}
              <div>
                <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-300">
                  Your Name
                </label>
                <input
                  type="text"
                  name="name"
                  placeholder="Enter your name"
                  value={form.name}
                  onChange={handleChange}
                  required
                  className="form-input w-full rounded-xl border border-[#283339] bg-[#111618] px-4 py-3 text-white placeholder-slate-500 outline-none"
                />
              </div>

              {/* Email */}
              <div>
                <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-300">
                  Email Address
                </label>
                <input
                  type="email"
                  name="email"
                  placeholder="you@example.com"
                  value={form.email}
                  onChange={handleChange}
                  required
                  className="form-input w-full rounded-xl border border-[#283339] bg-[#111618] px-4 py-3 text-white placeholder-slate-500 outline-none"
                />
              </div>

              {/* Message */}
              <div>
                <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-300">
                  Message
                </label>
                <textarea
                  name="message"
                  rows="4"
                  placeholder="Write your message here..."
                  value={form.message}
                  onChange={handleChange}
                  required
                  className="form-input w-full rounded-xl border border-[#283339] bg-[#111618] px-4 py-3 text-white placeholder-slate-500 outline-none resize-none"
                />
              </div>

              {/* Button */}
              <button
                type="submit"
                disabled={loading}
                className="btn-send flex w-full items-center justify-center gap-2 rounded-xl bg-[#1193d4] py-3.5 text-base font-semibold text-white disabled:opacity-60"
              >
                {loading ? (
                  <>
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                    Sending...
                  </>
                ) : (
                  <>
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <line x1="22" y1="2" x2="11" y2="13"/>
                      <polygon points="22 2 15 22 11 13 2 9 22 2"/>
                    </svg>
                    Send Message
                  </>
                )}
              </button>
            </form>

            {/* Status */}
            {status === "success" && (
              <div className="status-enter mt-5 flex items-center gap-2 rounded-xl border border-green-500/30 bg-green-500/10 px-4 py-3 text-sm text-green-400">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="shrink-0">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                Message sent successfully. We'll get back to you soon.
              </div>
            )}

            {status === "error" && (
              <div className="status-enter mt-5 flex items-center gap-2 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="shrink-0">
                  <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                Failed to send message. Please try again.
              </div>
            )}

          </div>
        </div>
      </section>
    </>
  );
}