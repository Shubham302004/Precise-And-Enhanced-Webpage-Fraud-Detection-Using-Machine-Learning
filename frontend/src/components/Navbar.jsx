import { NavLink } from "react-router-dom";
import { useState } from "react";

export default function Navbar() {
  const [open, setOpen] = useState(false);

  const links = [
    { name: "Home",      path: "/" },
    { name: "Detection", path: "/detection" },
    { name: "Analysis",  path: "/analysis" },
    { name: "About",     path: "/about" },
    { name: "Contact",   path: "/contact" },
  ];

  return (
    <>
      <style>{`
        @keyframes mobile-in {
          from { opacity: 0; transform: translateY(-8px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        .mobile-menu { animation: mobile-in 0.2s ease both; }

        .nav-link-underline {
          transition: opacity 0.2s, width 0.2s;
        }
        .hamburger-btn {
          transition: background 0.2s, border-color 0.2s;
        }
        .hamburger-btn:hover {
          background: #1a1f22;
          border-color: #1193d4;
        }
      `}</style>

      <header className="sticky top-0 z-50 bg-[#111618]/90 backdrop-blur border-b border-[#283339]">
        <div className="w-full px-6 md:px-10">
          <div className="mx-auto flex max-w-7xl items-center justify-between py-4">

            {/* Logo */}
            <NavLink to="/" className="flex items-center gap-3 group">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#1193d4]/15 border border-[#1193d4]/20 transition group-hover:bg-[#1193d4]/25">
                <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-[#1193d4]">
                  <path d="M44 4H30.6666V17.3334H17.3334V30.6666H4V44H44V4Z" fill="currentColor" />
                </svg>
              </div>
              <span className="text-lg font-semibold tracking-tight text-white">
                Web Page Fraud Detector
              </span>
            </NavLink>

            {/* Desktop Nav */}
            <nav className="hidden md:flex items-center gap-8">
              {links.map((item) => (
                <NavLink
                  key={item.name}
                  to={item.path}
                  className={({ isActive }) =>
                    `relative text-sm font-medium transition ${
                      isActive ? "text-white" : "text-slate-400 hover:text-white"
                    }`
                  }
                >
                  {({ isActive }) => (
                    <>
                      {item.name}
                      <span
                        className={`nav-link-underline absolute -bottom-1 left-0 h-[2px] rounded-full bg-gradient-to-r from-[#1193d4] to-[#38bdf8] ${
                          isActive ? "opacity-100 w-full" : "opacity-0 w-0"
                        }`}
                      />
                    </>
                  )}
                </NavLink>
              ))}
            </nav>

            {/* Mobile Hamburger */}
            <button
              onClick={() => setOpen(!open)}
              className="hamburger-btn md:hidden rounded-lg border border-[#283339] bg-[#111618] p-2 text-slate-300 hover:text-white"
              aria-label="Toggle menu"
            >
              {open ? (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                  <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              ) : (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                  <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>
                </svg>
              )}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {open && (
          <div className="mobile-menu md:hidden border-t border-[#283339] bg-[#0f1416]">
            <nav className="flex flex-col px-6 py-4 space-y-1">
              {links.map((item) => (
                <NavLink
                  key={item.name}
                  to={item.path}
                  onClick={() => setOpen(false)}
                  className={({ isActive }) =>
                    `rounded-lg px-3 py-2.5 text-sm font-medium transition ${
                      isActive
                        ? "bg-[#1193d4]/10 text-white border-l-2 border-[#1193d4]"
                        : "text-slate-400 hover:text-white hover:bg-[#283339]/40"
                    }`
                  }
                >
                  {item.name}
                </NavLink>
              ))}
            </nav>
          </div>
        )}
      </header>
    </>
  );
}