import React from 'react';

interface QuestionBoxProps {
  question: string;
  onClick?: () => void;
}

const QuestionBox: React.FC<QuestionBoxProps> = ({ question, onClick }) => {
  return (
    <div
      className="flex w-[321px] cursor-pointer items-center justify-center gap-[10px] rounded-[8px] border border-[#9CBFBC] bg-[#F9FFFF] px-[18px] py-[15px] transition-colors hover:bg-[#e9f5f5]"
      onClick={onClick}
    >
      <p className="text-center font-['Inter'] text-[16px] font-normal text-[#002835]">
        {question}
      </p>
    </div>
  );
};

export default QuestionBox;
