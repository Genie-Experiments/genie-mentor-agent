import React from "react";

interface HamburgerIconProps {
  isOpen?: boolean; // Made optional since we don't use it anymore
  onClick: () => void;
}

const HamburgerIcon: React.FC<HamburgerIconProps> = ({ onClick }) => {
  return (
    <button 
      className="flex justify-center items-center cursor-pointer"
      onClick={onClick}
    >
      <svg 
        xmlns="http://www.w3.org/2000/svg" 
        width="34" 
        height="34" 
        viewBox="0 0 34 34" 
        fill="none"
      >
        <path 
          d="M4.25 17H29.75M4.25 8.5H29.75M4.25 25.5H29.75" 
          stroke="white" 
          strokeWidth="4" 
          strokeLinecap="round" 
          strokeLinejoin="round"
        />
      </svg>
    </button>
  );
};

export default HamburgerIcon;
