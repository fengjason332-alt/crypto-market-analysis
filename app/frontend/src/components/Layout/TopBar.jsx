/**
 * TopBar — Sticky navigation with scroll-to-section links
 *
 * Instead of switching tabs, clicking a nav item smoothly scrolls
 * to the corresponding section on the page.
 */

import { useState, useEffect } from "react";
import { useLanguage } from "../../hooks/useLanguage";
import LanguageDropdown from "../LanguageDropdown";

const NAV_ITEMS = [
  { key: "markets", icon: "📊", sectionId: "section-markets" },
  { key: "technical", icon: "📈", sectionId: "section-technical" },
  { key: "insights", icon: "🤖", sectionId: "section-insights" },
  { key: "watchlist", icon: "⭐", sectionId: "section-watchlist" },
  { key: "data", icon: "🗂", sectionId: "section-data" },
];

export default function TopBar() {
  const { t } = useLanguage();
  const [activeSection, setActiveSection] = useState("");

  // Track which section is currently in view
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveSection(entry.target.id);
          }
        });
      },
      { rootMargin: "-20% 0px -60% 0px", threshold: 0 }
    );

    NAV_ITEMS.forEach(({ sectionId }) => {
      const el = document.getElementById(sectionId);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  const scrollTo = (sectionId) => {
    const el = document.getElementById(sectionId);
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <header className="sticky top-0 z-40 bg-bg-primary/95 backdrop-blur-sm border-b border-bg-border">
      <div className="max-w-[1400px] mx-auto px-6 flex items-center justify-between h-14">
        {/* Brand — click to scroll to top */}
        <button
          onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
          className="flex items-center gap-2 bg-transparent border-none cursor-pointer"
          style={{ fontFamily: "inherit" }}
        >
          <span className="text-xl">📊</span>
          <span className="text-lg font-bold text-text-primary tracking-tight">
            CryptoScope
          </span>
        </button>

        {/* Nav links — scroll to sections */}
        <nav className="flex items-center gap-1 bg-bg-card rounded-lg p-1">
          {NAV_ITEMS.map(({ key, icon, sectionId }) => (
            <button
              key={key}
              onClick={() => scrollTo(sectionId)}
              className={`flex items-center gap-1.5 px-4 py-1.5 rounded-md text-sm font-medium transition-all duration-150
                ${
                  activeSection === sectionId
                    ? "bg-bg-hover text-text-primary"
                    : "text-text-muted hover:text-text-secondary"
                }`}
              style={{ border: "none", cursor: "pointer", fontFamily: "inherit" }}
            >
              <span className="text-xs">{icon}</span>
              {t(`nav.${key}`)}
            </button>
          ))}
        </nav>

        {/* Language dropdown */}
        <LanguageDropdown />
      </div>
    </header>
  );
}
