/**
 * LanguageDropdown — Compact dropdown to switch locale
 *
 * Replaces the old EN / 中文 / ES button row with a clean
 * single-button dropdown. Sits in the top-right of the navbar.
 */

import { useState, useRef, useEffect } from "react";
import { Globe } from "lucide-react";
import { useLanguage } from "../hooks/useLanguage";

export default function LanguageDropdown() {
  const { locale, setLocale, localeLabels } = useLanguage();
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  // Close on outside click
  useEffect(() => {
    function handleClick(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg
                   bg-bg-card border border-bg-border
                   hover:border-text-muted transition-colors
                   text-sm text-text-secondary"
      >
        <Globe size={15} />
        <span className="font-medium">{localeLabels[locale].flag}</span>
      </button>

      {open && (
        <div
          className="absolute right-0 top-full mt-2 w-40
                     bg-bg-card border border-bg-border rounded-xl
                     shadow-2xl overflow-hidden z-50"
        >
          {Object.entries(localeLabels).map(([code, { label, flag }]) => (
            <button
              key={code}
              onClick={() => {
                setLocale(code);
                setOpen(false);
              }}
              className={`w-full flex items-center gap-3 px-4 py-3 text-sm
                         transition-colors
                         ${
                           code === locale
                             ? "bg-bg-hover text-text-primary"
                             : "text-text-secondary hover:bg-bg-hover hover:text-text-primary"
                         }`}
            >
              <span className="text-base">{flag}</span>
              <span>{label}</span>
              {code === locale && (
                <span className="ml-auto text-accent-blue">✓</span>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
