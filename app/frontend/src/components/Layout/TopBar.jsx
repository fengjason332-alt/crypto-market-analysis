/**
 * TopBar — Main navigation header
 *
 * Mimics OKX's top bar: brand on left, nav tabs center, language on right.
 */

import { useLanguage } from "../../hooks/useLanguage";
import LanguageDropdown from "../LanguageDropdown";

const NAV_ITEMS = [
  { key: "markets", icon: "📊" },
  { key: "technical", icon: "📈" },
  { key: "insights", icon: "🤖" },
  { key: "watchlist", icon: "⭐" },
  { key: "data", icon: "🗂" },
];

export default function TopBar({ activeTab, onTabChange }) {
  const { t } = useLanguage();

  return (
    <header className="sticky top-0 z-40 bg-bg-primary/95 backdrop-blur-sm border-b border-bg-border">
      <div className="max-w-[1400px] mx-auto px-6 flex items-center justify-between h-14">
        {/* Brand */}
        <div className="flex items-center gap-2">
          <span className="text-xl">📊</span>
          <span className="text-lg font-bold text-text-primary tracking-tight">
            CryptoScope
          </span>
        </div>

        {/* Nav tabs */}
        <nav className="flex items-center gap-1 bg-bg-card rounded-lg p-1">
          {NAV_ITEMS.map(({ key, icon }) => (
            <button
              key={key}
              onClick={() => onTabChange(key)}
              className={`flex items-center gap-1.5 px-4 py-1.5 rounded-md text-sm font-medium transition-all duration-150
                ${
                  activeTab === key
                    ? "bg-bg-hover text-text-primary"
                    : "text-text-muted hover:text-text-secondary"
                }`}
            >
              <span className="text-xs">{icon}</span>
              {t(`nav.${key}`)}
            </button>
          ))}
        </nav>

        {/* Right: language */}
        <LanguageDropdown />
      </div>
    </header>
  );
}
