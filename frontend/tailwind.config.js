/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        // Extracted directly from the mockups
        root: {
          950: '#04090E', // navbar / deepest background
          900: '#060B10', // page background
          850: '#080D12', // stats band / raised panel
          800: '#0C1116', // card surface
          750: '#101720', // hovered surface / inputs
          700: '#151D26', // borders (strong)
          600: '#1B242E', // borders (subtle-strong)
        },
        line: {
          DEFAULT: '#161E27',
          soft: '#111820',
          strong: '#25303C',
        },
        brand: {
          50: '#FFF4E8',
          100: '#FFE4C7',
          200: '#FFC98F',
          300: '#FFAD57',
          400: '#FB9733',
          500: '#F8851F', // primary — sampled from CTA button
          600: '#E0710F',
          700: '#B4590B',
          800: '#7A3C08',
          900: '#3D1E04',
        },
        ink: {
          DEFAULT: '#E8EDF2',
          soft: '#9AA7B4',
          dim: '#6B7885',
          faint: '#495562',
        },
        ok: '#2ECC71',
        warn: '#F5B942',
        danger: '#E5484D',
        info: '#3B9EFF',
      },
      fontFamily: {
        sans: ['Inter', 'Segoe UI', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'SFMono-Regular', 'Menlo', 'Consolas', 'monospace'],
        ar: ['Noto Kufi Arabic', 'Tajawal', 'Inter', 'sans-serif'],
      },
      borderRadius: {
        xl: '0.75rem',
        '2xl': '1rem',
      },
      boxShadow: {
        glow: '0 0 0 1px rgba(248,133,31,.35), 0 8px 30px -8px rgba(248,133,31,.45)',
        card: '0 1px 0 0 rgba(255,255,255,.03) inset, 0 10px 30px -20px rgba(0,0,0,.9)',
        pop: '0 20px 60px -20px rgba(0,0,0,.85)',
      },
      keyframes: {
        'fade-up': {
          '0%': { opacity: 0, transform: 'translateY(14px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
        'fade-in': { '0%': { opacity: 0 }, '100%': { opacity: 1 } },
        'pulse-glow': {
          '0%,100%': { opacity: 0.55 },
          '50%': { opacity: 1 },
        },
        marquee: {
          '0%': { transform: 'translateX(0)' },
          '100%': { transform: 'translateX(-50%)' },
        },
        blink: { '0%,49%': { opacity: 1 }, '50%,100%': { opacity: 0 } },
      },
      animation: {
        'fade-up': 'fade-up .6s cubic-bezier(.22,1,.36,1) both',
        'fade-in': 'fade-in .5s ease both',
        'pulse-glow': 'pulse-glow 3s ease-in-out infinite',
        marquee: 'marquee 28s linear infinite',
        blink: 'blink 1.1s step-end infinite',
      },
    },
  },
  plugins: [],
}
