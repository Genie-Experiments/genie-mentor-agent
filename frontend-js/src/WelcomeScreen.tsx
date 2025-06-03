import React from 'react';
import InputField from './components/ui/InputField';
import QuestionBox from './components/ui/QuestionBox';
import genieLogo from './assets/genie.svg';

const WelcomeScreen: React.FC = () => {
  const handleQuestionSubmit = (question: string) => {
    console.log("Question submitted:", question);
  };

  const predefinedQuestions = [
    "What is Genie AI Mentor?",
    "How can Genie help me learn AI?",
    "What concepts should I start with?",
    "Show me the learning path"
  ];

  return (
    <div className="flex flex-col items-center justify-between h-full py-8">     
      <div className="w-full flex justify-center">
        <div className="w-40 h-40 flex items-center justify-center">
          <img src={genieLogo} alt="Genie Logo" className="w-full h-full object-contain" />
        </div>
      </div>
      <div className="flex flex-col items-center mt-[24px]">
        <div className="mb-6">
          <p className="text-[#002835] text-center font-['Inter'] text-[34px] font-normal">
            Welcome to
          </p>
          <h1 className="text-[#002835] font-['Inter'] text-[54px] font-bold">
          </h1>
        </div>
        
        <p className="text-[#002835] text-center font-['Inter'] text-[22px] font-normal mb-8">
          Start by asking a question
        </p>

        <div className="mt-[34px]">
          <InputField onSubmit={handleQuestionSubmit} />
        </div>
      </div>

      <div className="w-full mt-auto">
        <p className="text-[#002835] text-center font-['Inter'] text-[18px] font-normal mb-6">
          Or try predefined questions provided below
        </p>
        
        <div className="grid grid-cols-2 gap-6 max-w-[690px] mx-auto">
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