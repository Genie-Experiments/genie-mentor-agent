import React from 'react';

interface QuestionBadgeProps {
  question: string;
  isLoading: boolean;
  error: string | null;
}

const QuestionBadge: React.FC<QuestionBadgeProps> = ({ question, isLoading }) => {
  return (
    <div>
      <div className="width-[100%] mt-0 mb-0 flex max-w-[80px] items-center justify-center gap-[10px] rounded-[50px] bg-[#00A599] px-[9px] py-[5px]">
        <span className="font-['Inter'] text-[14px] font-semibold text-white">Question</span>
      </div>

      <div className="mt-[16px]">
        <span className="font-['Inter'] text-[28px] font-semibold text-[#002835]">{question}</span>
      </div>

      {isLoading && (
        <div className="mt-[21px] flex items-center gap-2">
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-[#00A599] border-t-transparent"></div>
          <span className="font-['Inter'] text-[18px] font-normal text-[#002835]">
            Processing your question...
          </span>
        </div>
      )}

      {!isLoading && (
        <div className="mt-[21px]">
          <span className="font-['Inter'] text-[18px] font-normal text-[#002835]">
            It takes less than a minute to gather and compile best answers for you.
          </span>
        </div>
      )}
    </div>
  );
};

export default QuestionBadge;
