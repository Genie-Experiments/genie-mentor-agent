import React from "react";

interface PlusIconProps {
  onClick: () => void;
  className?: string;
}

const PlusIcon: React.FC<PlusIconProps> = ({ onClick, className }) => {
  return (
    <button 
      onClick={onClick}
      className={`flex items-center justify-center w-[44px] h-[44px] p-[8px] bg-white rounded-full ${className || ''}`}
    >
      <svg 
        xmlns="http://www.w3.org/2000/svg" 
        width="28" 
        height="28" 
        viewBox="0 0 28 28" 
        fill="none"
      >
        <path 
          d="M14.0002 5.83334V22.1667M5.8335 14H22.1668" 
          stroke="#00A599" 
          strokeWidth="2" 
          strokeLinecap="round" 
          strokeLinejoin="round"
        />
      </svg>
    </button>
  );
};

export default PlusIcon;
