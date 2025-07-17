import React, { useState, useRef, useEffect } from 'react';
import { cn } from '@/lib/utils';

interface SidebarProps {
  onNewChat?: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ onNewChat }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isHovering, setIsHovering] = useState(false);
  const sidebarRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLDivElement>(null);

  // Function to toggle sidebar between collapsed and expanded states
  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
    setIsHovering(false); // Reset hover state when explicitly toggled
  };

  // Effect to expand sidebar on hover if it's collapsed
  useEffect(() => {
    const handleSidebarHover = () => {
      if (isCollapsed) {
        setIsHovering(true);
      }
    };

    const handleSidebarLeave = () => {
      if (isCollapsed) {
        setIsHovering(false);
      }
    };

    // Using current ref values inside the effect to ensure we have the most up-to-date elements
    const sidebarEl = sidebarRef.current;
    const buttonEl = buttonRef.current;

    // Add event listeners only if the elements exist
    if (sidebarEl) {
      sidebarEl.addEventListener('mouseenter', handleSidebarHover);
      sidebarEl.addEventListener('mouseleave', handleSidebarLeave);
    }

    if (buttonEl) {
      buttonEl.addEventListener('mouseenter', handleSidebarHover);
      buttonEl.addEventListener('mouseleave', handleSidebarLeave);
    }

    // Cleanup function to remove event listeners when component unmounts or dependencies change
    return () => {
      if (sidebarEl) {
        sidebarEl.removeEventListener('mouseenter', handleSidebarHover);
        sidebarEl.removeEventListener('mouseleave', handleSidebarLeave);
      }
      if (buttonEl) {
        buttonEl.removeEventListener('mouseenter', handleSidebarHover);
        buttonEl.removeEventListener('mouseleave', handleSidebarLeave);
      }
    };
  }, [isCollapsed]);

  return (
    <div
      ref={sidebarRef}
      className={cn(
        'sticky top-0 left-0 flex h-screen flex-col overflow-hidden transition-all duration-300 ease-in-out',
        'border-r border-[#B9D9D7] bg-[#F0FFFE]'
      )}
      onMouseEnter={() => isCollapsed && setIsHovering(true)}
      onMouseLeave={() => isCollapsed && setIsHovering(false)}
      style={{
        width: isCollapsed && !isHovering ? '90px' : '280px',
        paddingLeft: '25px',
        paddingRight: isCollapsed && !isHovering ? '0' : '25px',
        zIndex: 100, // Ensure sidebar stays on top
      }}
    >
      {/* Toggle Button - Only visible in expanded mode */}
      {!isCollapsed && (
        <div
          className="absolute top-[24px] right-[12px] z-20 cursor-pointer rounded-full p-1 transition-all duration-200 ease-in-out hover:bg-gray-100"
          onClick={toggleSidebar}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#002835"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="transition-transform duration-200 ease-in-out"
          >
            <path d="M15 18l-6-6 6-6" />
          </svg>
        </div>
      )}

      {/* Genie Logo - SVG implementation - Also serves as toggle button when collapsed */}
      <div
        className={cn(
          'absolute top-[24px] z-10 h-[75px] w-[47px]',
          isCollapsed && 'cursor-pointer transition-opacity hover:opacity-80'
        )}
        style={{ left: '25px' }}
        onClick={isCollapsed ? toggleSidebar : undefined}
        title={isCollapsed ? 'Expand sidebar' : ''}
      >
        <svg
          width="47"
          height="75"
          viewBox="0 0 94 150"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M20.72 102.31C26.65 101.7 31.99 100.58 35.88 97.15C32.56 98.24 28.81 99.86 24.89 100.65C19.01 101.83 13.24 101.13 8.29996 97.34C1.43996 92.08 -0.380044 82.6 3.84996 74.23C7.12996 67.74 12.34 63.13 18.66 59.7C19.17 59.43 19.82 59.28 20.16 58.87C22.4 56.16 25.28 55.07 28.67 55.51C29.55 52.16 28.75 50.44 26.35 48.49C25.38 47.7 24.72 46.1 24.59 44.81C24.44 43.27 24.74 41.53 25.36 40.1C26.45 37.59 26.36 35.09 25.62 32.68C24.8 30.02 23.51 27.51 22.41 24.95C22.21 24.48 21.95 24.04 21.72 23.58C23.56 22.89 24.2 23.23 29.35 27.44C32.02 23.1 35.77 20.13 40.81 18.76C40.5 17.22 40.4 15.78 41.87 14.7C42.17 14.48 42.07 13.63 42.07 13.08C42.01 9.24 42.75 5.67 45.28 2.59C48.14 -0.890005 54.33 -0.910005 56.42 2.92C57.78 5.4 60.35 6.73 63.72 7.32C60.29 8.21 57.45 8.89 54.48 7.29C50.54 5.16 47.38 6.35 45.75 10.51C45.03 12.34 44.27 14.22 45.75 16.18C46.17 16.73 45.9 17.8 45.96 18.91C50.16 20.48 53.88 23.14 56.38 27.5C58.62 25.46 60.64 23.2 64.31 23.15C63.9 23.91 63.7 24.42 63.38 24.83C60.65 28.36 59.77 32.51 59.59 36.81C59.54 38.01 60.28 39.22 60.51 40.45C60.81 42.02 61.24 43.64 61.11 45.2C61.01 46.34 60.38 47.9 59.49 48.41C56.6 50.06 56.55 52.51 56.8 55.48C57.62 55.48 58.37 55.38 59.08 55.5C60.26 55.7 61.61 55.76 62.54 56.39C66.22 58.91 70.01 61.37 73.3 64.34C77.68 68.3 80.94 73.13 81.76 79.2C82.85 87.23 80.13 93.82 73.88 98.9C70.6499 101.53 66.86 101.89 63.35 99.89C59.73 97.83 56.39 95.22 53.09 92.64C47.88 88.57 42.26 85.45 35.64 84.44C34.81 84.31 33.96 84.3 33.08 84.36C38.97 85.5 44.27 87.93 48.96 91.59C52.14 94.07 55.12 96.8 58.23 99.35C60.47 101.19 62.9 102.73 65.83 102.96C61.73 105.62 57.51 108.17 53.5 111.02C48.94 114.27 44.82 118.07 41.45 122.58C40.5 123.86 39.73 125.31 39.09 126.77C38.47 128.18 38.33 129.74 39.47 131.01C40.58 132.25 42.11 132.18 43.49 131.7C45.92 130.85 48.34 129.9 50.67 128.81C54.09 127.2 57.54 125.85 61.41 126.03C64.43 126.17 67.06 127.12 68.23 130.12C69.49 133.36 69.34 136.59 67 139.39C65.77 140.86 63.96 141.07 62.16 141.34C59.95 141.68 57.71 142.05 55.6 142.75C51.79 144.02 51.3 145.68 53.46 149.06C51.56 148.38 49.69 145.8 49.72 143.89C49.74 142.3 50.78 141.48 52.09 141.05C53.34 140.64 54.67 140.48 55.96 140.21C57.21 139.95 58.37 139.46 58.53 138.03C58.7 136.5 57.59 135.53 56.33 135.36C53.85 135.03 51.32 134.93 48.82 134.98C45.15 135.05 41.48 135.59 37.82 135.47C33.54 135.33 30.4 132.92 28.11 129.4C24.9 124.47 23.46 118.9 22.39 113.23C21.72 109.68 21.27 106.08 20.68 102.29L20.72 102.31Z"
            fill="#002835"
          />
          <path
            d="M93.75 20.26C89.21 20.26 82.02 13.07 82.02 8.53C82.02 13.07 74.83 20.26 70.29 20.26C74.83 20.26 82.02 27.45 82.02 31.99C82.02 27.45 89.21 20.26 93.75 20.26Z"
            fill="#00A599"
          />
          <path
            d="M17.42 40.65C14.1 40.65 8.82999 35.39 8.82999 32.06C8.82999 35.38 3.56999 40.65 0.23999 40.65C3.55999 40.65 8.82999 45.91 8.82999 49.24C8.82999 45.92 14.09 40.65 17.42 40.65Z"
            fill="#00A599"
          />
        </svg>
      </div>

      {/* Toggle Button - Only visible in expanded mode */}
      {!isCollapsed && (
        <div
          className="absolute top-[24px] right-[12px] z-20 cursor-pointer rounded-full p-1 hover:bg-gray-100"
          onClick={toggleSidebar}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#002835"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M15 18l-6-6 6-6" />
          </svg>
        </div>
      )}

      {/* New Chat Button */}
      <div
        ref={buttonRef}
        className="absolute top-[132px] z-10 transition-all duration-300 ease-in-out"
        style={{ left: '25px' }}
        onMouseEnter={() => isCollapsed && setIsHovering(true)}
        onMouseLeave={() => isCollapsed && setIsHovering(false)}
      >
        <div className="relative overflow-hidden">
          {isCollapsed && !isHovering ? (
            <div
              className="flex h-[44px] w-[44px] cursor-pointer items-center justify-center rounded-[7px] bg-[rgba(0,165,153,0.10)] transition-all duration-300 ease-in-out"
              onClick={toggleSidebar}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="28"
                height="28"
                viewBox="0 0 28 28"
                fill="none"
              >
                <path
                  d="M14 5.83333V22.1667M5.83333 14H22.1667"
                  stroke="#00A599"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </div>
          ) : (
            <div
              className="flex cursor-pointer items-center gap-2 rounded-[7px] bg-[rgba(0,165,153,0.10)] transition-all duration-300 ease-in-out"
              style={{
                padding: '8px 14px 8px 9px',
                width: isCollapsed && !isHovering ? '44px' : '230px',
                overflow: 'hidden',
              }}
              onClick={() => {
                // If new chat handler is provided, call it
                if (onNewChat) {
                  onNewChat();
                }
              }}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="28"
                height="28"
                viewBox="0 0 28 28"
                fill="none"
                className="flex-shrink-0"
              >
                <path
                  d="M14 5.83333V22.1667M5.83333 14H22.1667"
                  stroke="#00A599"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              <span
                className={cn(
                  'font-medium whitespace-nowrap text-[#00A599] transition-opacity duration-300 ease-in-out',
                  isCollapsed && !isHovering ? 'opacity-0' : 'opacity-100'
                )}
              >
                Start New Chat
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
