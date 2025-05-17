import { useMediaQuery } from 'react-responsive';

// Common breakpoints (can be adjusted based on your needs)
export const BREAKPOINTS = {
  mobile: 640,
  tablet: 768,
  laptop: 1024,
  desktop: 1280,
} as const;

export function useBreakpoint() {
  const isMobile = useMediaQuery({ maxWidth: BREAKPOINTS.mobile });
  const isTablet = useMediaQuery({
    minWidth: BREAKPOINTS.mobile + 1,
    maxWidth: BREAKPOINTS.tablet,
  });
  const isLaptop = useMediaQuery({
    minWidth: BREAKPOINTS.tablet + 1,
    maxWidth: BREAKPOINTS.laptop,
  });
  const isDesktop = useMediaQuery({ minWidth: BREAKPOINTS.laptop + 1 });

  // Additional useful combinations
  const isMobileOrTablet = useMediaQuery({ maxWidth: BREAKPOINTS.tablet });
  const isTabletOrLaptop = useMediaQuery({
    minWidth: BREAKPOINTS.mobile + 1,
    maxWidth: BREAKPOINTS.laptop,
  });

  return {
    isMobile,
    isTablet,
    isLaptop,
    isDesktop,
    isMobileOrTablet,
    isTabletOrLaptop,
    // Current breakpoint name
    breakpoint: isMobile ? 'mobile' : isTablet ? 'tablet' : isLaptop ? 'laptop' : 'desktop',
  } as const;
}

// For backwards compatibility
export function useScreen() {
  const { isMobile, isTablet, isLaptop, isDesktop } = useBreakpoint();
  return { isMobile, isTablet, isLaptop, isDesktop };  
}
