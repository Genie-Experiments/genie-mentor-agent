import React from 'react';

interface ResponseListProps {
  responses: string[];
}

const ResponseList: React.FC<ResponseListProps> = ({ responses }) => {
  return (
    <div className="w-full flex justify-center mt-8">
      <div className="w-full flex flex-col items-end">
        {responses.map((resp, idx) => (
          <div
            key={idx}
            className="mb-2 px-4 py-2 bg-[#F9FFFF] rounded-lg text-right max-w-[90%] text-[#002835] font-['Inter'] text-[16px] shadow"
          >
            {resp}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ResponseList;
