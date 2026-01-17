import type { Config } from "tailwindcss";

const config: Config = {
    content: [
        "./pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./components/**/*.{js,ts,jsx,tsx,mdx}",
        "./app/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                background: "#0A0A0A", // Deep charcoal
                foreground: "#EDEDED", // Off-white text
                card: "rgba(255, 255, 255, 0.05)",
                "card-border": "rgba(255, 255, 255, 0.1)",
                brand: {
                    primary: "#8B5CF6", // Neon Purple
                    secondary: "#10B981", // Neon Green
                    accent: "#EF4444", // Neon Red/Orange
                },
                muted: "#A3A3A3",
            },
            backdropBlur: {
                xs: "2px",
            },
            backgroundImage: {
                "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
                "glass-gradient": "linear-gradient(180deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.03) 100%)",
            },
            keyframes: {
                "fade-in-up": {
                    "0%": { opacity: "0", transform: "translateY(10px)" },
                    "100%": { opacity: "1", transform: "translateY(0)" },
                },
                pulse: {
                    "0%, 100%": { opacity: "1" },
                    "50%": { opacity: "0.5" },
                },
            },
            animation: {
                "fade-in-up": "fade-in-up 0.5s ease-out forwards",
                pulse: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
            },
        },
    },
    plugins: [],
};
export default config;
