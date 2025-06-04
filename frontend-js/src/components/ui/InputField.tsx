import React, { useState } from 'react';

interface InputFieldProps {
  onSubmit: (value: string) => void;
}

const InputField: React.FC<InputFieldProps> = ({ onSubmit }) => {
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
    <div className="flex w-[658px] items-center justify-between rounded-[8px] border border-[#002835] bg-white p-[13px_13px_13px_18px]">
      <input
        type="text"
        className="flex-grow border-none font-['Inter'] text-[#002835] outline-none"
        placeholder="Ask a question..."
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyPress={handleKeyPress}
      />
      <button onClick={handleSubmit} className="h-[30px] w-[30px] flex-shrink-0">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="30"
          height="31"
          viewBox="0 0 30 31"
          fill="none"
        >
          <rect y="0.0700073" width="30" height="30" rx="6" fill="#00A599" />
          <path
            d="M8.33325 15.07H21.6666M21.6666 15.07L14.9999 8.40332M21.6666 15.07L14.9999 21.7367"
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
