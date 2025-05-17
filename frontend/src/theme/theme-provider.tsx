
import { createContext, useContext, useEffect, useMemo, useState } from 'react';

// Extended list of supported themes
export type Theme =
  | 'light'
  | 'dark'
  | 'cupcake'
  | 'bumblebee'
  | 'emerald'
  | 'corporate'
  | 'synthwave'
  | 'retro'
  | 'cyberpunk'
  | 'valentine'
  | 'halloween'
  | 'garden'
  | 'forest'
  | 'aqua'
  | 'lofi'
  | 'pastel'
  | 'fantasy'
  | 'wireframe'
  | 'black'
  | 'luxury'
  | 'dracula'
  | 'cmyk'
  | 'autumn'
  | 'business'
  | 'acid'
  | 'lemonade'
  | 'night'
  | 'coffee'
  | 'winter'
  | 'system';

interface ThemeProviderProps {
  children: React.ReactNode;
  defaultTheme?: Theme;
  storageKey?: string;
}

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  isDarkTheme: boolean;
  isLoading: boolean;
}

const initialState: ThemeContextType = {
  theme: 'system',
  setTheme: () => null,
  isDarkTheme: false,
  isLoading: true,
};

const ThemeContext = createContext(initialState);

// List of themes considered "dark"
export const darkThemes = [
  'dark',
  'synthwave',
  'halloween',
  'forest',
  'black',
  'luxury',
  'dracula',
  'business',
  'night',
  'coffee',
];

export function ThemeProvider({
  children,
  defaultTheme = 'halloween',
  storageKey = 'theme',
  ...props
}: ThemeProviderProps) {
  const [theme, setTheme] = useState(defaultTheme);
  const [isDarkTheme, setIsDarkTheme] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const savedTheme = localStorage.getItem(storageKey) as Theme | null;
    console.log('Theme', 'Saved theme from localStorage:', savedTheme);
    if (savedTheme) {
      setTheme(savedTheme);
    }
    setIsLoading(false);
  }, [storageKey]);

  useEffect(() => {
    const root = document.documentElement;

    if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'forest'
        : 'autumn';

      root.setAttribute('data-theme', systemTheme);
      setIsDarkTheme(systemTheme === 'forest');
      return;
    }

    root.setAttribute('data-theme', theme);
    setIsDarkTheme(darkThemes.includes(theme));
  }, [theme]);

  const value = useMemo(
    () => ({
      theme,
      setTheme: (theme: Theme) => {
        localStorage.setItem(storageKey, theme);
        setTheme(theme);
      },
      isLoading,
      isDarkTheme,
    }),
    [theme, isLoading, storageKey, isDarkTheme]
  );

  return (
    <ThemeContext.Provider {...props} value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

export const useTheme = () => {
  const context = useContext(ThemeContext);

  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }

  return context;
};