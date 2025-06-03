import React from 'react';

interface QuestionBoxProps {
  question: string;
  onClick?: () => void;
}

const QuestionBox: React.FC<QuestionBoxProps> = ({ question, onClick }) => {
  return (
    <div 
      className="flex w-[321px] px-[18px] py-[15px] justify-center items-center gap-[10px] rounded-[8px] border border-[#9CBFBC] bg-[#F9FFFF] cursor-pointer hover:bg-[#e9f5f5] transition-colors"
      onClick={onClick}
    >
      <p className="text-[#002835] text-center font-['Inter'] text-[16px] font-normal">
        {question}
      </p>
    </div>
  );
};

export default QuestionBox;
