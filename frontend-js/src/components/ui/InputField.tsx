import React, { useState } from 'react';

interface InputFieldProps {
  onSubmit: (value: string) => void;
  placeholder?: string;
}

const InputField: React.FC<InputFieldProps> = ({ onSubmit, placeholder = "Ask a question..." }) => {
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = () => {
    if (inputValue.trim()) {
      onSubmit(inputValue);
      setInputValue('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSubmit();
    }
  };
  return (
    <div className="flex w-full max-w-[760px] items-center justify-between rounded-[16px] border border-[#002835] bg-white p-[15px_15px_15px_20px] shadow-lg">      <input
        type="text"
        className="flex-grow border-none font-['Inter'] text-[18px] text-[#002835] outline-none placeholder-[#002835]/50"
        placeholder={placeholder}
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyPress={handleKeyPress}
      />
      <button 
        onClick={handleSubmit} 
        className="h-[36px] w-[36px] flex-shrink-0 transition-transform hover:scale-105"
        aria-label="Submit question"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="30"
          height="30"
          viewBox="0 0 30 30"
          fill="none"
        >
          <rect width="30" height="30" rx="6" fill="#00A599" />
          <path
            d="M8.33325 15H21.6666M21.6666 15L14.9999 8.33333M21.6666 15L14.9999 21.6667"
            stroke="white"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>
    </div>
  );
};

export default InputField;
