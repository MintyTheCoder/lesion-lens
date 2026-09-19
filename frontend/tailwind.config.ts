import type { Config } from "tailwindcss";

// Atlas-plate world: a matte black plate, bone-white hairlines and numerals,
// and exactly two chroma roles — the lesion pattern flags.
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        plate: {
          DEFAULT: "#0b0b0c",
          raised: "#121214",
        },
        bone: {
          DEFAULT: "#ece9e2",
          dim: "#a39f96",
          faint: "#6b675f",
        },
        rule: {
          DEFAULT: "rgba(236, 233, 226, 0.16)",
          strong: "rgba(236, 233, 226, 0.42)",
        },
        typical: "#ff7a1a",
        atypical: "#4fc3f7",
      },
      fontFamily: {
        sans: ['"Archivo"', "system-ui", "sans-serif"],
      },
      letterSpacing: {
        plate: "-0.03em",
        label: "0.08em",
      },
      transitionTimingFunction: {
        out: "cubic-bezier(0.16, 1, 0.3, 1)",
      },
    },
  },
  plugins: [],
} satisfies Config;
