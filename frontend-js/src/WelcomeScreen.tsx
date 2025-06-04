import React from 'react';
import InputField from './components/ui/InputField';
import QuestionBox from './components/ui/QuestionBox';
import genieLogo from './assets/genie.svg';

const WelcomeScreen: React.FC = () => {
  const handleQuestionSubmit = (question: string) => {
    console.log('Question submitted:', question);
  };

  const predefinedQuestions = [
    'What is Genie AI Mentor?',
    'How can Genie help me learn AI?',
    'What concepts should I start with?',
    'Show me the learning path',
  ];
  return (
    <div className="flex h-full flex-col items-center justify-between py-8 pb-12">
      <div className="h-16 flex-grow-0"></div>z
      <div className="flex w-full justify-center">
        <div className="flex h-40 w-40 items-center justify-center">
          <img src={genieLogo} alt="Genie Logo" className="h-full w-full object-contain" />
        </div>
      </div>
      <div className="mt-[24px] flex flex-col items-center">
        <div className="mb-6">
          <p className="text-center font-['Inter'] text-[34px] font-normal text-[#002835]">
            Welcome to
          </p>
          <h1 className="font-['Inter'] text-[54px] font-bold text-[#002835]">
            Genie AI Mentor Agent
          </h1>
        </div>{' '}
        {/* Start text */}
        <p className="mb-4 text-center font-['Inter'] text-[22px] font-normal text-[#002835]">
          Start by asking a question
        </p>
        <div className="mt-4">
          <InputField onSubmit={handleQuestionSubmit} />{' '}
        </div>{' '}
      </div>
      <div className="mt-auto w-full">
        {' '}
        <p className="mb-6 text-center font-['Inter'] text-[18px] font-normal text-[#002835] opacity-60">
          Or try predefined questions provided below
        </p>
        <div className="mx-auto grid w-[658px] grid-cols-2 gap-x-4 gap-y-3">
          {predefinedQuestions.map((question, index) => (
            <QuestionBox
              key={index}
              question={question}
              onClick={() => handleQuestionSubmit(question)}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default WelcomeScreen;
