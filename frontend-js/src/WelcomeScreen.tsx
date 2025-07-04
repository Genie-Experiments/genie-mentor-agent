import React, { useState, useEffect } from 'react';
import QuestionBox from './components/ui/QuestionBox';
import InputField from './components/ui/InputField';
import genieLogo from './assets/genie.svg';

interface WelcomeScreenProps {
  onQuestionSubmit?: (question: string) => void;
}

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onQuestionSubmit }) => {
  const [isLargeScreen, setIsLargeScreen] = useState(window.innerWidth >= 1525);

  useEffect(() => {
    const handleResize = () => {
      setIsLargeScreen(window.innerWidth >= 1525);
    };

    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  const handleQuestionClick = (question: string) => {
    if (onQuestionSubmit) {
      onQuestionSubmit(question);
    } else {
      console.log('Question submitted:', question);
    }
  };

  const predefinedQuestions = [
    'What is Genie Mentor?',
    'How can Genie help me learn AI?',
    'What concepts should I start with?',
    'Show me the learning path',
  ];
  // Using inline styles for large screens to guarantee the original sizes

  return (
    <div
      className="flex h-full flex-col items-center justify-between py-6 pb-8"
      style={isLargeScreen ? { paddingTop: '2rem', paddingBottom: '3rem' } : {}}
    >
      {/* Top content */}
      <div className="h-10 flex-grow-0" style={isLargeScreen ? { height: '4rem' } : {}}></div>
      <div className="flex w-full justify-center">
        <div
          className="flex h-32 w-32 items-center justify-center md:h-24 md:w-24"
          style={isLargeScreen ? { height: '10rem', width: '10rem' } : {}}
        >
          <img src={genieLogo} alt="Genie Logo" className="h-full w-full object-contain" />
        </div>
      </div>

      {/* Middle content with title */}
      <div
        className="mt-[12px] flex flex-col items-center md:mt-[8px]"
        style={isLargeScreen ? { marginTop: '24px' } : {}}
      >
        <div className="mb-[6px]">
          <p
            className="text-center font-['Inter'] text-[28px] font-normal text-[#002835] md:text-[22px]"
            style={isLargeScreen ? { fontSize: '34px' } : {}}
          >
            Welcome to
          </p>
          <h1
            className="font-['Inter'] text-[42px] font-bold text-[#002835] md:text-[32px]"
            style={isLargeScreen ? { fontSize: '54px' } : {}}
          >
            Genie Mentor Agent
          </h1>
        </div>
      </div>

      {/* Predefined questions section */}
      <div className="w-full">
        <p
          className="mb-4 text-center font-['Inter'] text-[16px] font-normal text-[#002835] opacity-60 md:text-[14px]"
          style={isLargeScreen ? { marginBottom: '1.5rem', fontSize: '18px' } : {}}
        >
          Try predefined questions provided below
        </p>
        <div
          className="mx-auto grid w-[90%] max-w-[658px] grid-cols-2 gap-x-3 gap-y-2"
          style={isLargeScreen ? { width: '658px', columnGap: '1rem', rowGap: '0.75rem' } : {}}
        >
          {predefinedQuestions.map((question, index) => (
            <QuestionBox
              key={index}
              question={question}
              onClick={() => handleQuestionClick(question)}
            />
          ))}
        </div>
      </div>

      {/* Bottom content with input field */}
      <div
        className="mt-6 flex w-full flex-col items-center md:mt-4"
        style={isLargeScreen ? { marginTop: 'auto' } : {}}
      >
        <div
          className="flex w-full justify-center px-4"
          style={isLargeScreen ? { paddingLeft: 0, paddingRight: 0 } : {}}
        >
          <InputField
            onSubmit={(question) => handleQuestionClick(question)}
            placeholder="Ask Anything..."
            width="100%"
            maxWidth="658px"
          />
        </div>
      </div>
    </div>
  );
};

export default WelcomeScreen;
