/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./context/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "#0a0d14",
        surface: {
          50: "#182030",
          100: "#131a28",
          200: "#0f1522",
          300: "#0b101b",
          border: "#1f2b3e",
        },
        brand: {
          primary: "#3b82f6",
          emerald: "#10b981",
          crimson: "#ef4444",
          amber: "#f59e0b",
          cyan: "#06b6d4",
        },
      },
      fontFamily: {
        mono: [
          "JetBrains Mono",
          "Fira Code",
          "ui-monospace",
          "SFMono-Regular",
          "monospace",
        ],
        sans: [
          "Inter",
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          "sans-serif",
        ],
      },
      animation: {
        "pulse-fast": "pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "radar-scan": "radar 4s linear infinite",
        "flash-alert": "flash 0.8s ease-in-out infinite alternate",
      },
      keyframes: {
        radar: {
          "0%": { transform: "rotate(0deg)" },
          "100%": { transform: "rotate(360deg)" },
        },
        flash: {
          "0%": { opacity: "1", borderColor: "rgba(239, 68, 68, 0.9)" },
          "100%": { opacity: "0.4", borderColor: "rgba(239, 68, 68, 0.2)" },
        },
      },
    },
  },
  plugins: [],
};
