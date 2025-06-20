import React, { useState, useEffect, useRef } from 'react';

interface InputFieldProps {
  onSubmit: (value: string) => void;
  placeholder?: string;
  isLoading?: boolean;
  width?: string;
}

const InputField: React.FC<InputFieldProps> = ({
  onSubmit,
  placeholder = 'Ask Anything...',
  isLoading = false,
  width = '658px',
}) => {
  const [inputValue, setInputValue] = useState('');
  const [webSearchActive, setWebSearchActive] = useState(false);
  const hasText = inputValue.trim().length > 0;
  const wasLoadingRef = useRef(false);
  const handleSubmit = () => {
    if (inputValue.trim()) {
      onSubmit(inputValue);
      setInputValue(''); // Clear the input immediately after submission
    }
  };
  // Clear input when loading finishes - only on transition from loading to not loading
  useEffect(() => {
    // Store current value for dependency check
    const currentInput = inputValue;

    // Only execute when loading state changes from true to false
    if (wasLoadingRef.current && !isLoading && currentInput.trim()) {
      setInputValue('');
    }

    // Update ref for next check
    wasLoadingRef.current = isLoading;
    // We intentionally don't include inputValue in deps to avoid infinite loop
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isLoading]);

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSubmit();
    }
  };

  const toggleWebSearch = () => {
    setWebSearchActive(!webSearchActive);
  };
  return (
    <div
      className="flex flex-col items-start rounded-[8px] border border-[#B9D9D7] bg-white transition-all duration-200 focus-within:border-[#00A599] focus-within:shadow-[0px_4px_12px_rgba(0,165,153,0.15)]"
      style={{ width }}
    >
      {/* First row for text input */}
      <div className="flex w-full items-center px-[18px] pt-[15px] pb-[5px]">
        <input
          type="text"
          className="w-full border-none text-left font-['Inter'] text-[16px] text-[#002835] transition-colors duration-200 outline-none placeholder:text-left placeholder:font-['Inter'] placeholder:text-[16px] placeholder:font-normal placeholder:text-[#002835] placeholder:opacity-50"
          placeholder={placeholder}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          style={{
            color: '#002835',
            textAlign: 'left',
            fontFamily: 'Inter',
            fontSize: '16px',
            fontStyle: 'normal',
            fontWeight: '400',
            lineHeight: 'normal',
          }}
        />{' '}
      </div>

      {/* Second row for action items */}
      <div className="flex w-full items-center justify-between px-[18px] py-[10px]">
        {/* Web search button on left */}
        <div
          className={`group flex cursor-pointer items-center transition-all duration-200 ease-in-out ${
            webSearchActive
              ? 'gap-[7px] rounded-[50px] border border-[rgba(0,_165,_153,_0.24)] bg-[rgba(0,_165,_153,_0.10)] px-[9px] py-0'
              : 'gap-[12px] hover:text-[#00A599]'
          }`}
          onClick={toggleWebSearch}
          role="button"
          aria-pressed={webSearchActive}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="17"
            height="18"
            viewBox="0 0 17 18"
            fill="none"
            className="cursor-pointer transition-all duration-200"
          >
            <path
              d="M15.5834 9.07003C15.5834 12.982 12.4121 16.1534 8.50008 16.1534M15.5834 9.07003C15.5834 5.15801 12.4121 1.98669 8.50008 1.98669M15.5834 9.07003H1.41675M8.50008 16.1534C4.58806 16.1534 1.41675 12.982 1.41675 9.07003M8.50008 16.1534C10.2718 14.2137 11.2787 11.6965 11.3334 9.07003C11.2787 6.44355 10.2718 3.92636 8.50008 1.98669M8.50008 16.1534C6.72834 14.2137 5.72146 11.6965 5.66675 9.07003C5.72146 6.44355 6.72834 3.92636 8.50008 1.98669M1.41675 9.07003C1.41675 5.15801 4.58806 1.98669 8.50008 1.98669"
              stroke={webSearchActive ? '#00A599' : '#002835'}
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="group-hover:stroke-[#00A599]"
            />
          </svg>
          <span
            className={`font-['Inter'] text-[14px] font-normal transition-colors duration-200 ${
              webSearchActive ? 'text-[#00A599]' : 'text-[#002835] group-hover:text-[#00A599]'
            }`}
          >
            Web Search
          </span>
        </div>

        {/* Submit button on right */}
        <button
          onClick={handleSubmit}
          className={`h-[30px] w-[30px] flex-shrink-0 transform cursor-pointer transition-all duration-200 ${
            hasText && !isLoading ? 'hover:scale-105 active:scale-95' : ''
          } ${!hasText && !isLoading ? 'cursor-not-allowed opacity-40' : ''}`}
          aria-label="Submit question"
          disabled={isLoading || !hasText}
        >
          {isLoading ? (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="30"
              height="30"
              viewBox="0 0 30 30"
              fill="none"
              className="opacity-40 transition-opacity duration-200"
            >
              <rect width="30" height="30" rx="6" fill="#00A599" />
              <rect x="10" y="10" width="10" height="10" fill="white" />
            </svg>
          ) : (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="30"
              height="30"
              viewBox="0 0 30 30"
              fill="none"
              className="transition-all duration-200"
            >
              <rect
                width="30"
                height="30"
                rx="6"
                fill="#00A599"
                fillOpacity={hasText ? '1' : '0.4'}
              />
              <path
                d="M8.33337 15H21.6667M21.6667 15L15 8.40332M21.6667 15L15 21.7367"
                stroke="white"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          )}
        </button>
      </div>
    </div>
  );
};

export default InputField;
