import React from 'react';
import QuestionBox from './components/ui/QuestionBox';
import InputField from './components/ui/InputField';
import genieLogo from './assets/genie.svg';

interface WelcomeScreenProps {
  onQuestionSubmit?: (question: string) => void;
}

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onQuestionSubmit }) => {
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
  return (
    <div className="flex h-full flex-col items-center justify-between py-8 pb-12">
      {/* Top content */}
      <div className="h-16 flex-grow-0"></div>
      <div className="flex w-full justify-center">
        <div className="flex h-40 w-40 items-center justify-center">
          <img src={genieLogo} alt="Genie Logo" className="h-full w-full object-contain" />
        </div>
      </div>

      {/* Middle content with title */}
      <div className="mt-[24px] flex flex-col items-center">
        <div className="mb-[6px]">
          <p className="text-center font-['Inter'] text-[34px] font-normal text-[#002835]">
            Welcome to
          </p>
          <h1 className="font-['Inter'] text-[54px] font-bold text-[#002835]">
            Genie Mentor Agent
          </h1>
        </div>
      </div>

      {/* Predefined questions section */}
      <div className="w-full">
        <p className="mb-6 text-center font-['Inter'] text-[18px] font-normal text-[#002835] opacity-60">
          Try predefined questions provided below
        </p>
        <div className="mx-auto grid w-[658px] grid-cols-2 gap-x-4 gap-y-3">
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
      <div className="mt-auto flex w-full flex-col items-center">
        <div className="flex justify-center">
          <InputField
            onSubmit={(question) => handleQuestionClick(question)}
            placeholder="Ask Anything..."
            width="658px"
          />
        </div>
      </div>
    </div>
  );
};

export default WelcomeScreen;
