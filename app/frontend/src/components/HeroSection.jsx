/**
 * HeroSection — Landing hero with 3D rotating Bitcoin coin
 *
 * Features:
 *   - Metallic Bitcoin coin with 3D Y-axis rotation + floating animation
 *   - Sci-fi elements: orbit rings, glowing particles, grid background
 *   - Gradient tagline text
 *   - CTA buttons that scroll to Markets and Methodology sections
 */

import { useLanguage } from "../hooks/useLanguage";

export default function HeroSection() {
  const { t } = useLanguage();

  const scrollTo = (id) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <section
      id="hero"
      style={{
        minHeight: "92vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "60px 48px",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Subtle radial glow */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(ellipse 50% 50% at 28% 50%, rgba(247,147,26,0.04) 0%, transparent 70%)",
        }}
      />

      {/* Sci-fi grid background */}
      <div className="hero-grid-bg" />

      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "72px",
          maxWidth: "920px",
          width: "100%",
          position: "relative",
          zIndex: 1,
          flexWrap: "wrap",
          justifyContent: "center",
        }}
      >
        {/* Left: 3D Rotating Bitcoin Coin */}
        <div
          style={{
            flexShrink: 0,
            width: "260px",
            height: "260px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            position: "relative",
          }}
        >
          {/* Orbit rings */}
          <div className="hero-orbit-ring" />
          <div className="hero-orbit-ring-2" />

          {/* Coin container with float + spin */}
          <div className="hero-coin-wrapper">
            <div className="hero-coin-spin">
              <svg
                viewBox="0 0 200 200"
                style={{
                  width: "170px",
                  height: "170px",
                  filter:
                    "drop-shadow(0 8px 32px rgba(247,147,26,0.3)) drop-shadow(0 2px 8px rgba(0,0,0,0.5))",
                }}
              >
                <defs>
                  <radialGradient id="coinFace" cx="40%" cy="35%" r="60%">
                    <stop offset="0%" stopColor="#FFB84D" />
                    <stop offset="30%" stopColor="#F7931A" />
                    <stop offset="70%" stopColor="#C47612" />
                    <stop offset="100%" stopColor="#8B5209" />
                  </radialGradient>
                  <radialGradient id="coinEdge" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" stopColor="#D4860F" />
                    <stop offset="100%" stopColor="#6B4008" />
                  </radialGradient>
                  <linearGradient id="rimLight" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="rgba(255,220,150,0.4)" />
                    <stop offset="50%" stopColor="rgba(255,220,150,0)" />
                    <stop offset="100%" stopColor="rgba(255,220,150,0.15)" />
                  </linearGradient>
                  <linearGradient id="bevelTop" x1="50%" y1="0%" x2="50%" y2="100%">
                    <stop offset="0%" stopColor="rgba(255,230,170,0.5)" />
                    <stop offset="100%" stopColor="rgba(0,0,0,0.3)" />
                  </linearGradient>
                </defs>

                {/* Ground shadow */}
                <ellipse cx="100" cy="108" rx="72" ry="10" fill="rgba(247,147,26,0.08)" />

                {/* Coin edge (depth) */}
                <ellipse cx="100" cy="103" rx="68" ry="8" fill="url(#coinEdge)" opacity="0.6" />

                {/* Main coin face */}
                <circle cx="100" cy="97" r="72" fill="url(#coinFace)" />
                <circle cx="100" cy="97" r="72" fill="url(#rimLight)" />

                {/* Outer rim */}
                <circle cx="100" cy="97" r="72" fill="none" stroke="rgba(255,200,100,0.25)" strokeWidth="1.5" />

                {/* Inner rings (engraving) */}
                <circle cx="100" cy="97" r="62" fill="none" stroke="rgba(255,200,100,0.12)" strokeWidth="0.8" />
                <circle cx="100" cy="97" r="58" fill="none" stroke="rgba(139,82,9,0.3)" strokeWidth="0.5" />

                {/* B letter with depth effect */}
                <text
                  x="100" y="112"
                  textAnchor="middle"
                  fontFamily="Georgia, 'Times New Roman', serif"
                  fontSize="64"
                  fontWeight="700"
                  fill="rgba(0,0,0,0.15)"
                  transform="translate(0,2)"
                >
                  B
                </text>
                <text
                  x="100" y="112"
                  textAnchor="middle"
                  fontFamily="Georgia, 'Times New Roman', serif"
                  fontSize="64"
                  fontWeight="700"
                  fill="rgba(255,230,170,0.9)"
                >
                  B
                </text>
                <text
                  x="100" y="112"
                  textAnchor="middle"
                  fontFamily="Georgia, 'Times New Roman', serif"
                  fontSize="64"
                  fontWeight="700"
                  fill="url(#bevelTop)"
                  opacity="0.5"
                >
                  B
                </text>

                {/* Vertical strokes on B */}
                <line x1="82" y1="73" x2="82" y2="120" stroke="rgba(255,230,170,0.15)" strokeWidth="1.5" strokeLinecap="round" />
                <line x1="118" y1="73" x2="118" y2="120" stroke="rgba(255,230,170,0.15)" strokeWidth="1.5" strokeLinecap="round" />

                {/* Breathing pulse ring */}
                <circle cx="100" cy="97" r="72" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="2">
                  <animate attributeName="r" values="72;75;72" dur="3s" repeatCount="indefinite" />
                  <animate attributeName="opacity" values="1;0;1" dur="3s" repeatCount="indefinite" />
                </circle>

                {/* Specular highlight */}
                <circle cx="70" cy="65" r="18" fill="rgba(255,255,255,0.04)" />
              </svg>
            </div>

            {/* Floating particles */}
            <div className="hero-particle hero-p1" />
            <div className="hero-particle hero-p2" />
            <div className="hero-particle hero-p3" />
            <div className="hero-particle hero-p4" />
          </div>
        </div>

        {/* Right: Tagline + CTA */}
        <div style={{ flex: 1, minWidth: "280px" }}>
          <p
            style={{
              fontSize: "12px",
              fontWeight: 600,
              color: "#F7931A",
              letterSpacing: "3px",
              textTransform: "uppercase",
              margin: "0 0 20px 0",
              opacity: 0.8,
            }}
          >
            Real-time analytics
          </p>
          <h1
            style={{
              fontSize: "40px",
              fontWeight: 700,
              lineHeight: 1.15,
              margin: "0 0 24px 0",
              letterSpacing: "-1.5px",
            }}
          >
            <span style={{ color: "#eaecef" }}>Crypto is gonna</span>
            <br />
            <span
              style={{
                background:
                  "linear-gradient(135deg, #F7931A 0%, #E8A040 25%, #627EEA 60%, #9945FF 100%)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                backgroundClip: "text",
              }}
            >
              change you
            </span>
            <span style={{ color: "#eaecef" }}> and</span>
            <br />
            <span style={{ color: "#eaecef" }}>the world.</span>
          </h1>
          <p
            style={{
              fontSize: "14px",
              color: "#5e6673",
              lineHeight: 1.8,
              margin: "0 0 32px 0",
              maxWidth: "380px",
            }}
          >
            End-to-end analytics pipeline with ML-evaluated forecasts and
            exchange-inspired dashboards. Built to understand crypto, not just
            track it.
          </p>
          <div style={{ display: "flex", gap: "12px", alignItems: "center", flexWrap: "wrap" }}>
            <button
              onClick={() => scrollTo("section-markets")}
              style={{
                padding: "11px 28px",
                borderRadius: "8px",
                background: "linear-gradient(135deg, #F7931A, #D4770A)",
                color: "#fff",
                fontSize: "13px",
                fontWeight: 600,
                cursor: "pointer",
                border: "none",
                letterSpacing: "0.3px",
                fontFamily: "inherit",
              }}
            >
              Explore markets
            </button>
            <button
              onClick={() => scrollTo("section-insights")}
              style={{
                padding: "11px 24px",
                borderRadius: "8px",
                border: "1px solid #2b2f36",
                background: "transparent",
                color: "#5e6673",
                fontSize: "13px",
                fontWeight: 500,
                cursor: "pointer",
                fontFamily: "inherit",
              }}
            >
              View insights
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
