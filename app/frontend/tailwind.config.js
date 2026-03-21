/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        // OKX-inspired dark palette
        bg: {
          primary: "#0b0e11",
          card: "#1a1d23",
          hover: "#22262e",
          border: "#2b2f36",
        },
        accent: {
          green: "#00b075",
          red: "#f6465d",
          blue: "#1e90ff",
          purple: "#9945ff",
          orange: "#f7931a",
          yellow: "#fcd535",
        },
        text: {
          primary: "#eaecef",
          secondary: "#848e9c",
          muted: "#5e6673",
        },
      },
      fontFamily: {
        sans: [
          "Inter",
          "SF Pro Display",
          "-apple-system",
          "BlinkMacSystemFont",
          "sans-serif",
        ],
        mono: ["JetBrains Mono", "SF Mono", "monospace"],
      },
    },
  },
  plugins: [],
};
