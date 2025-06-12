import React from 'react';

interface QuestionBadgeProps {
  question: string;
  isLoading: boolean;
  error: string | null;
}

const QuestionBadge: React.FC<QuestionBadgeProps> = ({ 
  question,
  isLoading,
  error
}) => {
  return (
    <div>
      {/* Badge */}
      <div className="flex px-[9px] py-[5px] justify-center items-center gap-[10px] rounded-[50px] bg-[#00A599] mb-0 mt-8">
        <span className="text-white font-['Inter'] text-[14px] font-semibold">Question</span>
      </div>
      
      {/* User Question */}
      <div className="mt-[16px]">
        <span className="text-[#002835] font-['Inter'] text-[28px] font-semibold">{question}</span>
      </div>
      
      {/* Loading State */}
      {isLoading && (
        <div className="mt-[21px] flex items-center gap-2">
          <div className="animate-spin h-5 w-5 border-2 border-[#00A599] border-t-transparent rounded-full"></div>
          <span className="text-[#002835] font-['Inter'] text-[18px] font-normal">
            Processing your question...
          </span>
        </div>
      )}
      
      {/* Error Message */}
      {error && (
        <div className="mt-[21px] text-red-500 font-['Inter'] text-[18px] font-normal">
          {error}
        </div>
      )}
      
      {/* Info Text */}
      {!isLoading && !error && (
        <div className="mt-[21px]">
          <span className="text-[#002835] font-['Inter'] text-[18px] font-normal">
            It takes less than a minute to gather and compile best answers for you.
          </span>
        </div>
      )}
    </div>
  );
};

export default QuestionBadge;
