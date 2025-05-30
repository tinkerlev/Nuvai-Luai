import React, { useState, useEffect } from 'react';
import { Icon } from '@iconify/react';

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

// Theme categories for better organization
export const themeCategories = {
  base: ['light', 'dark', 'system'],
  colorful: ['cupcake', 'bumblebee', 'emerald', 'corporate', 'synthwave', 'retro', 'cyberpunk'],
  seasonal: ['valentine', 'halloween', 'autumn', 'winter'],
  nature: ['garden', 'forest', 'aqua', 'lemonade'],
  aesthetic: ['lofi', 'pastel', 'fantasy', 'wireframe', 'black', 'luxury', 'dracula', 'cmyk'],
  mood: ['business', 'acid', 'night', 'coffee'],
};

// Theme icons using Iconify
export const themeIconify = {
  light: 'ph:sun-bold',
  dark: 'ph:moon-bold',
  system: 'ph:desktop-bold',
  cupcake: 'mdi:cupcake',
  bumblebee: 'lucide-lab:bee',
  emerald: 'fa6-solid:gem',
  corporate: 'mdi:office-building',
  synthwave: 'mdi:sine-wave',
  retro: 'fa-solid:camera-retro',
  cyberpunk: 'mdi:robot',
  valentine: 'mdi:heart',
  halloween: 'mdi:halloween',
  garden: 'mdi:flower',
  forest: 'mdi:pine-tree',
  aqua: 'mdi:water',
  lofi: 'mdi:fantasy',
  pastel: 'mdi:palette-swatch',
  fantasy: 'mdi:wizard-hat',
  wireframe: 'mdi:pencil-ruler',
  black: 'mdi:circle',
  luxury: 'mdi:crown',
  cmyk: 'mdi:printer',
  autumn: 'mdi:leaf-maple',
  business: 'mdi:briefcase',
  acid: 'mdi:flask',
  lemonade: 'icon-park-outline:lemon',
  night: 'mdi:weather-night',
  coffee: 'mdi:coffee',
  winter: 'mdi:snowflake',
  dracula: 'game-icons:vampire-dracula',
};

export function ThemeToggle() {
  const [activeCategory, setActiveCategory] = useState('base');
  const [currentTheme, setCurrentTheme] = useState('halloween');
  const [isDarkTheme, setIsDarkTheme] = useState(true);

  // Load theme from localStorage on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      setCurrentTheme(savedTheme);
      applyTheme(savedTheme);
    } 
  }, []);

  // Function to apply theme
  const applyTheme = (theme) => {
    const root = document.documentElement;
    
    if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light';
      
      root.setAttribute('data-theme', systemTheme);
      setIsDarkTheme(darkThemes.includes(systemTheme));
    } else {
      // Make sure we're using a valid theme name
      root.setAttribute('data-theme', theme);
      setIsDarkTheme(darkThemes.includes(theme));
    }

    // Save to localStorage
    localStorage.setItem('theme', theme);
    setCurrentTheme(theme);
  };

  const handleThemeChange = (theme) => {
    applyTheme(theme);
  };

  return (
    <>
      <DecorativeBlur isDarkTheme={isDarkTheme} />
    <div className="dropdown z-50 dropdown-end fixed top-4 right-4">
      {/* Dropdown toggle button */}
      {/* Toggle button with current theme icon */}
      <label 
        tabIndex={0} 
        className="btn btn-ghost btn-sm btn-circle m-1"
      >
        {isDarkTheme ? (
          <Icon icon="ph:moon-bold" className="h-4 w-4" />
        ) : (
          <Icon icon="ph:sun-bold" className="h-4 w-4" />
        )}
      </label>
      
      {/* Theme selector dropdown - fixed width and improved styling */}
      <ul 
        tabIndex={0} 
        className="dropdown-content menu z-[100] p-3  shadow-lg w-max bg-base-100 rounded-box"
        // style={{ minWidth:'20vw', maxWidth: '90vw' }}
      >
        <li className="menu-title px-0 pt-0 mb-2">
          <div className="tabs tabs-boxed flex overflow-x-auto">
            {Object.keys(themeCategories).map(category => (
              <div
                key={category}
                className={`tab text-xs ${activeCategory === category ? 'tab-active' : ''}`}
                onClick={() => setActiveCategory(category)}
              >
                {category.charAt(0).toUpperCase() + category.slice(1)}
              </div>
            ))}
          </div>
        </li>
        <li className="p-0">
          <div className="flex justify-center gap-2 pt-1 max-h-[40vh] w-full p-1">
            {themeCategories[activeCategory].map(themeName => (
              <button
                key={themeName}
                className={`btn btn-sm ${
                  currentTheme === themeName ? 'btn-primary' : 'btn-ghost'
                } flex items-center justify-center w-fit h-auto py-2`}
                onClick={() => handleThemeChange(themeName)}
              >
                <div className="flex flex-col items-center justify-center">
                  <span className="mb-1">
                    {themeIconify[themeName] ? (
                      <Icon icon={themeIconify[themeName]} width="15" height="15" />
                    ) : '🎨'}
                  </span>
                  <span className="text-xs text-center capitalize truncate w-full">
                    {themeName}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </li>
      </ul>
    </div>
    </>
  );
}


const DecorativeBlur = ({isDarkTheme = false}) => {
  // const isDarkTheme = useThemeStore((state) => state.isDarkTheme);
  return (
      <div className='z-0'>
      {/* <div className="absolute top-0 left-0 w-[100vw] h-[100vh] bg-gradient-to-tr from-[#1e1e2f]/10 to-[#16161d]/5 opacity-50 blur-[200px] -z-10"></div> */}
      {/* <div className="absolute top-0 right-0 w-[100vw] h-[100vh] bg-gradient-to-br from-[#1e1e2f] to-[#16161d] opacity-50 blur-[200px] -z-10"></div> */}
      <div
        style={{ animationDuration: '35s' }}
        className={`fixed animate-spin* top-[-30vh] right-[-30vw] w-1/2 h-1/2 rounded-full bg-gradient-to-r ${
          isDarkTheme
            ? 'from-emerald-400/40 to-violet-400/40'
            : 'from-emerald-500/10 to-violet-500/10'
        } blur-[200px]`}
      />
      <div
        style={{}}
        className={`fixed animate-spin* bottom-[-30vh] right-1/4 w-1/2 h-1/5 rounded-full bg-gradient-to-r ${
          isDarkTheme ? 'from-amber-400/80 to-pink-400/40' : 'from-amber-400/40 to-pink-400/30'
        } blur-[300px]`}
      />
      {!isDarkTheme && (
        <div
          style={{ animationDuration: '40s' }}
          className={`fixed animate-spin* top-[-30vh] left-[-20vw] w-1/2 h-1/2 rounded-full bg-gradient-to-r ${
            isDarkTheme ? 'from-purple-400/40 to-pink-400/40' : 'from-purple-500/10 to-pink-500/10'
          } blur-[200px]`}
        />
      )}
      {/* <div
        style={{}}
        className={`fixed animate-spin** bottom-0 right-[-10vw] w-1/2 h-1/4 rounded-full bg-gradient-to-r from-primary/10 to-accent/10 blur-[100px]`}
      /> */}
    </div>
  );
}