import React from 'react';
import QuestionBox from './components/ui/QuestionBox';
import InputField from './components/ui/InputField';
import genieLogo from './assets/genie.svg';
import { PREDEFINED_QUESTIONS } from './constant';

interface WelcomeScreenProps {
  onQuestionSubmit?: (question: string) => void;
}

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onQuestionSubmit }) => {
  const handleQuestionClick = (question: string) => {
    if (onQuestionSubmit) {
      onQuestionSubmit(question);
    } else {
      console.warn('No onQuestionSubmit handler provided');
    }
  };

  return (
    <div className="flex h-full flex-col items-center justify-between py-6 pb-8 xl:pt-8 xl:pb-12">
      <div className="h-10 xl:h-16" />

      <header className="flex w-full justify-center">
        <div className="flex h-24 w-24 items-center justify-center md:h-32 md:w-32 xl:h-40 xl:w-40">
          <img
            src={genieLogo}
            alt="Genie Logo"
            className="h-full w-full object-contain"
            onError={(e) => {
              console.error('Failed to load genie logo');
              e.currentTarget.style.display = 'none';
            }}
          />
        </div>
      </header>

      <section className="mt-2 flex flex-col items-center md:mt-3 xl:mt-6">
        <div className="text-center">
          <p className="font-inter mb-1.5 text-xl font-normal text-slate-800 md:text-2xl xl:text-3xl">
            Welcome to
          </p>
          <h1 className="font-inter text-3xl font-bold text-slate-800 md:text-4xl xl:text-5xl">
            Genie Mentor Agent
          </h1>
        </div>
      </section>

      <section className="w-full" aria-labelledby="predefined-questions">
        <p
          id="predefined-questions"
          className="font-inter mb-4 text-center text-sm font-normal text-slate-800/60 md:text-base xl:mb-6 xl:text-lg"
        >
          Try predefined questions provided below
        </p>
        <div className="mx-auto grid w-[90%] max-w-[658px] grid-cols-2 gap-x-3 gap-y-2 xl:w-[658px] xl:gap-x-4 xl:gap-y-3">
          {PREDEFINED_QUESTIONS.map((question, index) => (
            <QuestionBox
              key={`question-${index}`}
              question={question}
              onClick={() => handleQuestionClick(question)}
            />
          ))}
        </div>
      </section>

      <section className="mt-6 flex w-full flex-col items-center md:mt-4 xl:mt-auto">
        <div className="flex w-full justify-center px-4 xl:px-0">
          <InputField
            onSubmit={handleQuestionClick}
            placeholder="Ask Anything..."
            width="100%"
            maxWidth="658px"
            aria-label="Ask a question"
          />
        </div>
      </section>
    </div>
  );
};

export default WelcomeScreen;
